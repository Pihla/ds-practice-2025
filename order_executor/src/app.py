import random
import sys
import os
import threading
import time
import ast

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
order_executor_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/order_executor'))
sys.path.insert(0, order_executor_grpc_path)
import order_executor_pb2 as order_executor
import order_executor_pb2_grpc as order_executor_grpc


# Set up orderqueue
orderqueue_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/orderqueue'))
sys.path.insert(0, orderqueue_grpc_path)
import orderqueue_pb2 as orderqueue
import orderqueue_pb2_grpc as orderqueue_grpc

# Set up books_database
books_database_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/books_database'))
sys.path.insert(0, books_database_grpc_path)
import books_database_pb2 as books_database
import books_database_pb2_grpc as books_database_grpc

# Set up dummy payment
payment_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/payment'))
sys.path.insert(0, payment_grpc_path)
import payment_pb2 as payment
import payment_pb2_grpc as payment_grpc

# Set up orchestrator
orchestrator_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/orchestrator'))
sys.path.insert(0, orchestrator_grpc_path)
import orchestrator_pb2 as orchestrator
import orchestrator_pb2_grpc as orchestrator_grpc

import grpc
from concurrent import futures
from google.protobuf.empty_pb2 import Empty

# Create a class to define the server functions, derived from
# order_executor_pb2_grpc.OrderExecutorServiceServicer
class OrderExecutorService(order_executor_grpc.OrderExecutorServiceServicer):
    def __init__(self):
        self.id = int(os.getenv("EXECUTOR_ID"))
        self.port = 50054 + self.id
        self.leader_id = None
        self.running = True
        self.leader_lock = threading.Lock()
        self.is_election_in_progress = threading.Event()
        self.last_leader_update = time.time()

        self.all_addresses = {
            1: "order_executor1:50055",
            2: "order_executor2:50056",
            3: "order_executor3:50057",
            4: "order_executor4:50058"
        }
        self.all_addresses.pop(self.id)

        if self.id == 4:
            print(f"[{self.id}] Starting first election.")
            self.start_election()
        threading.Thread(target=self.try_execute_orders, daemon=True).start()
        threading.Thread(target=self.monitor_leader, daemon=True).start()

    def Ping(self, request, context):
        return order_executor.PingResponse(is_alive=True)

    def StartElection(self, request, context):
        #print(f"[{self.id}] Received election request from {request.id}")
        if not self.is_election_in_progress.is_set():
            threading.Thread(target=self.start_election, daemon=True).start()
        return order_executor.ElectionResponse(is_success=True)

    def AnnounceLeader(self, request, context):
        #print(f"[{self.id}] Announcement received, new leader {request.leader_id}.")
        with self.leader_lock:
            self.leader_id = request.leader_id
            self.last_leader_update = time.time()
        return Empty()

    def try_execute_orders(self):
        # If the node is the leader it will try to execute an order
        while self.running:
            time.sleep(2)
            with self.leader_lock:
                if self.leader_id == self.id:
                    print(f"[{self.id}] Leader {self.leader_id} is trying to execute.")
                    self.execute_order()

    # Asks database and dummy payment service to prepare and returns whether all accepted
    def prepare_all(self, order, order_data):
        # Prepare decrementing number of books in database
        with grpc.insecure_channel('books_database1: 50059') as channel:
            stub = books_database_grpc.BooksDatabaseServiceStub(channel)
            for book in order_data["items"]:
                prepare_request = books_database.GenericBookRequest(order_id=order.orderId, title=book["name"],
                                                                amount=book["quantity"])
                response = stub.Prepare(prepare_request)
                if not response.ready:
                    print(f"Prepare database rejected for book {book['name']}, amount {book['quantity']}, order {order.orderId}")
                    return False, f"Not enough stock for book '{book['name']}'."

        # Prepare payment
        with grpc.insecure_channel('payment: 50062') as channel:
            stub = payment_grpc.PaymentServiceStub(channel)
            prepare_response = stub.Prepare(payment.PrepareRequest(order_id=order.orderId))
            if not prepare_response.ready:
                print(f"Prepare payment rejected for order {order.orderId}")
                return False, "Payment rejected."

        print(f"Prepared successfully.")
        return True, ""

    # Aborts all prepared events for the order
    def abort_all(self, order, order_data):
        all_succeed = True

        # Abort decrementing number of books in database
        with grpc.insecure_channel('books_database1: 50059') as channel:
            stub = books_database_grpc.BooksDatabaseServiceStub(channel)
            for book_line in order_data["items"]:
                abort_request = books_database.GenericBookRequest(order_id=order.orderId, title=book_line["name"],
                                                            amount=book_line["quantity"])
                response = stub.Abort(abort_request)
                if not response.aborted:
                    print("Error aborting database: " + response.message)
                    all_succeed = False

        # Abort payment
        with grpc.insecure_channel('payment: 50062') as channel:
            stub = payment_grpc.PaymentServiceStub(channel)
            abort_request = payment.AbortRequest(order_id=order.orderId)
            response = stub.Abort(abort_request)
            if not response.aborted:
                print("Error aborting payment: " + response.message)
                all_succeed = False

        return all_succeed

    # Commits all prepared events for the order
    def commit_all(self, order, order_data):
        all_succeed = True

        # Commit decrementing number of books in database
        with grpc.insecure_channel('books_database1: 50059') as channel:
            stub = books_database_grpc.BooksDatabaseServiceStub(channel)
            for book in order_data["items"]:
                commit_request = books_database.GenericBookRequest(order_id=order.orderId, title=book["name"],
                                                              amount=book["quantity"])
                response = stub.Commit(commit_request)
                if not response.success:
                    print(f"Failed to commit, reason: {response.message}")
                    all_succeed = False

        with grpc.insecure_channel('payment: 50062') as channel:
            stub = payment_grpc.PaymentServiceStub(channel)
            commit_response = stub.Commit(payment.CommitRequest(order_id=order.orderId))
            if commit_response.success:
                print("Dummy payment was successful.")
            else:
                print(f"Failed to commit, reason: {commit_response.message}")
                all_succeed = False

        return all_succeed

    def execute_order(self):
        # Node tries to retrieve the order from Order Queue
        order = self.dequeue_order()
        if order:
            print(f"Order is being executed, ID: {order.orderId}")
            order_data = ast.literal_eval(order.full_request_data)

            # Prepare
            while True:
                try:
                    agreed_to_prepare, prepare_message = self.prepare_all(order, order_data)
                    print(f"All participants agreed to prepare order {order.orderId}: {agreed_to_prepare}")
                    break
                except Exception as e:
                    print(f"Failed to prepare order {order.orderId}: {str(e)[:100]}...\n trying again later.")
                    time.sleep(5)

            # Abort
            if not agreed_to_prepare:
                with grpc.insecure_channel('orchestrator:5001') as channel:
                    stub = orchestrator_grpc.OrchestratorServiceStub(channel)
                    print(f"Sending order {order.orderId} failure message '{prepare_message}' to orchestrator.")
                    stub.AcceptOrderNotApprovedMessage(
                        orchestrator.OrderNotApprovedData(orderId=order.orderId, message=prepare_message))
                while True:
                    try:
                        all_succeed = self.abort_all(order, order_data)
                        print(f"Order {order.orderId} was aborted successfully: {all_succeed}.")
                        return
                    except Exception as e:
                        print(f"Failed to abort order {order.orderId}: {str(e)[:100]}...\n trying again later.")
                        time.sleep(5)

            # Commit
            while True:
                try:
                    all_succeed = self.commit_all(order, order_data)
                    print(f"Order {order.orderId} was committed successfully: {all_succeed}.")
                    with grpc.insecure_channel('orchestrator:5001') as channel:
                        stub = orchestrator_grpc.OrchestratorServiceStub(channel)
                        print(f"Sending order {order.orderId} confirmation to orchestrator.")
                        stub.AcceptOrderConfirmation(
                            orchestrator.OrderConfirmedData(orderId=order.orderId))
                    return
                except Exception as e:
                    print(f"Failed to commit order {order.orderId}: {str(e)[:100]}...\n trying again later.")
                    time.sleep(5)

    def dequeue_order(self):
        try:
            with grpc.insecure_channel('orderqueue:50054') as channel:
                # Create a stub object
                stub = orderqueue_grpc.OrderQueueServiceStub(channel)
                response = stub.Dequeue(Empty())
                if response.orderId:
                    return response
        except Exception as e:
            print(f"[{self.id}] Failed to dequeue: {e}")
        return None

    def monitor_leader(self):
        # Monitor whether the leader is alive
        while self.running:
            time.sleep(15 + random.uniform(0.0, 3.0))
            with self.leader_lock: # To prevent the leader lock while an election is running we use the current_leader
                current_leader = self.leader_id
                time_since_update = time.time() - self.last_leader_update

            if current_leader != self.id and time_since_update > 5.0: # current_leader can be stale so make sure with time_since_update
                if current_leader is None or not self.ping_leader(current_leader):
                    print(f"[{self.id}] Leader [{current_leader}] is unresponsive. Starting election.")
                    threading.Thread(target=self.start_election, daemon=True).start()

    def ping_leader(self, leader_id):
        # Try to Ping the leader to know if an election is needed
        try:
            address = self.all_addresses.get(leader_id)
            if not address:
                return False
            with grpc.insecure_channel(address) as channel:
                stub = order_executor_grpc.OrderExecutorServiceStub(channel)
                response = stub.Ping(Empty())
                return response.is_alive
        except Exception as e:
            return False

    def start_election(self):
        # Bully algorithm
        if self.is_election_in_progress.is_set(): # If election is in progress don't start it again
            #print(f"[{self.id}] Election already in progress, skipping.")
            return
        self.is_election_in_progress.set()

        try:
            # Try to contact all higher ids
            higher_ids = [eid for eid in self.all_addresses if eid > self.id]
            accepted = False

            for eid in higher_ids:
                try:
                    address = self.all_addresses[eid]
                    with grpc.insecure_channel(address) as channel:
                        stub = order_executor_grpc.OrderExecutorServiceStub(channel)
                        res = stub.StartElection(order_executor.ElectionRequest(id=self.id), timeout=1)
                        if res.is_success:
                            #print(f"[{self.id}] Election accepted by {eid}")
                            accepted = True
                            break
                except Exception as e:
                    print(f"[{self.id}] Failed to contact {eid} during election.")

            if not accepted: # If noone responded then the node that called is the new leader
                print(f"[{self.id}] No higher node responded, Trying to announce leader.")
                with self.leader_lock:
                    self.leader_id = self.id
                    print(f"[{self.id}] I am the new leader.")
                self.announce_leader()
        finally:
            self.is_election_in_progress.clear()

    def announce_leader(self):
        for eid, address in self.all_addresses.items():
            try:
                with grpc.insecure_channel(address) as channel:
                    stub = order_executor_grpc.OrderExecutorServiceStub(channel)
                    stub.AnnounceLeader(order_executor.LeaderInfo(leader_id=self.id), timeout=1) # Timeout is used because waiting too long is bad.
            except Exception as e:
                pass
                #print(f"[{self.id}] Could not announce to {eid}.")

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())

    # Add OrderQueueService
    order_executor_grpc.add_OrderExecutorServiceServicer_to_server(OrderExecutorService(), server)

    # Listen on port 50054
    port = 50054 + int(os.getenv("EXECUTOR_ID", "1"))
    server.add_insecure_port(f"[::]:{port}")

    # Start the server
    server.start()
    print(f"Executor {os.getenv('EXECUTOR_ID')} Server started. Listening on port {port}.")

    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()