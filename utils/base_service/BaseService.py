import grpc
from concurrent.futures import ThreadPoolExecutor
import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")

# Set up fraud detection
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
sys.path.insert(0, fraud_detection_grpc_path)
import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc

# Set up suggestions
suggestions_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/suggestions'))
sys.path.insert(0, suggestions_grpc_path)
import suggestions_pb2 as suggestions
import suggestions_pb2_grpc as suggestions_grpc

# Set up transaction verification
transaction_verification_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_verification'))
sys.path.insert(0, transaction_verification_grpc_path)
import transaction_verification_pb2 as transaction_verification
import transaction_verification_pb2_grpc as transaction_verification_grpc

# Set up orchestrator
orchestrator_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/orchestrator'))
sys.path.insert(0, orchestrator_grpc_path)
import orchestrator_pb2 as orchestrator
import orchestrator_pb2_grpc as orchestrator_grpc


class BaseService:
    def __init__(self, service_name, svc_indx, total_svcs=3):
        self.service_name = service_name
        self.svc_indx = svc_indx
        self.total_svcs = total_svcs
        self.orders = {}
        self.when_to_execute_methods = None
        print(f"{self.service_name} initialized. Service index: {self.svc_indx}.")

    # Saves information about the order and creates a vector clock for the actions on the order
    def init_order(self, order_id, data):
        self.orders[order_id] = {"data": data, "vector_clock": [0]*self.total_svcs}
        print(f"Order {order_id} initialized.")
        self.do_actions_based_on_vector_clock(order_id)

    # Increments vector clock of order with given id by 1 for current service
    def increment_vector_clock(self, order_id):
        self.orders[order_id]["vector_clock"][self.svc_indx] += 1
        print(f"Incremented vector clock for order {order_id}. New vector clock: {self.orders[order_id]['vector_clock']}. Value of current service: {self.orders[order_id]['vector_clock'][self.svc_indx]}")

    # Combines local and incoming vector clocks of order with given id by taking biggest value for each service
    def merge_with_incoming_vector_clock(self, order_id, incoming_vc):
        local_vc = self.orders[order_id]["vector_clock"]
        for i in range(self.total_svcs):
            local_vc[i] = max(local_vc[i], incoming_vc[i])
        print(f"Merged incoming and local vector clocks. New vector clock: {local_vc}")

    # Sends current vector clock to all services
    def send_vector_clock_to_others(self, order_id):
        print("Sending vector clock to other services")
        vector_clock = self.orders[order_id]["vector_clock"]

        def send_vc_to_fraud_detection():
            if self.svc_indx != 1:
                with grpc.insecure_channel('fraud_detection:50051') as channel:
                    stub = fraud_detection_grpc.FraudDetectionServiceStub(channel)
                    stub.UpdateVectorClock(
                        fraud_detection.VectorClockStatus(orderId=order_id, vector_clock=vector_clock))

        def send_vc_to_suggestions_service():
            if self.svc_indx != 2:
                with grpc.insecure_channel('suggestions:50053') as channel:
                    stub = suggestions_grpc.SuggestionsServiceStub(channel)
                    stub.UpdateVectorClock(
                        suggestions.VectorClockStatus(orderId=order_id, vector_clock=vector_clock))

        def send_vc_to_transaction_verification():
            if self.svc_indx != 0:
                with grpc.insecure_channel('transaction_verification:50052') as channel:
                    stub = transaction_verification_grpc.TransactionVerificationServiceStub(channel)
                    stub.UpdateVectorClock(
                        transaction_verification.VectorClockStatus(orderId=order_id, vector_clock=vector_clock))

        threadpool_executor = ThreadPoolExecutor(max_workers=3)

        for f in [
            send_vc_to_transaction_verification,
            send_vc_to_fraud_detection,
            send_vc_to_suggestions_service,
        ]:
            threadpool_executor.submit(f)

    # Checks if value of vc1 is at least the same as value of vc2
    def vector_clock_is_at_least(self, vc1, vc2):
        print("comparing", vc1, vc2)
        for i in range(len(vc1)):
            if vc1[i] < vc2[i]:
                return False
        return True

    # Looks at vector clock for order with given id and decides if any of the methods should be executed in this service.
    # Executes all necessary methods and sends updated vector clock to other services
    def do_actions_based_on_vector_clock(self, order_id, depth=0):
        vector_clock = self.orders[order_id]["vector_clock"]
        print(f"Searching for the next action based on vector clock {vector_clock} for order {order_id}.")
        for possible_method in self.when_to_execute_methods:
            if self.vector_clock_is_at_least(vector_clock, possible_method["min_vc_for_exec"]): # if all preconditions are fulfilled
                if possible_method["min_vc_for_exec"][self.svc_indx] == vector_clock[self.svc_indx]: # if function hasn't already been executed
                    self.increment_vector_clock(order_id)
                    possible_method["method"](order_id)
                    print(f"Called function {possible_method['method']}")
                    self.do_actions_based_on_vector_clock(order_id, depth + 1) # call itself recursively to check if new action can be done in current service
        if depth == 1: # if vector clock has changed (depth=1 means that at least one action was done which means that vc changed)
            print(f"Sending vector clock {vector_clock} for order {order_id} to other services because nothing to do in current service.")
            self.send_vector_clock_to_others(order_id)

    # Handles incoming vector clock
    def handle_incoming_vector_clock(self, order_id, incoming_vc):
        print(f"Handling incoming vector clock {incoming_vc} for order {order_id}.")
        self.merge_with_incoming_vector_clock(order_id, incoming_vc)
        self.do_actions_based_on_vector_clock(order_id)

    # Sends notification to orchestrator that order has been rejected
    def send_order_failure_to_orchestrator(self, order_id, message):
        with grpc.insecure_channel('orchestrator:5001') as channel:
            stub = orchestrator_grpc.OrchestratorServiceStub(channel)
            print(f"Sending order {order_id} failure message {message} to orchestrator.")
            stub.AcceptOrderNotApprovedMessage(orchestrator.OrderNotApprovedData(orderId=order_id, message=message))
