import sys
import os
import threading
import time

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

        self.all_addresses = {
            1: "order_executor1:50055",
            2: "order_executor2:50056",
            3: "order_executor3:50057",
            4: "order_executor4:50058"
        }
        self.all_addresses.pop(self.id)

        if self.id == 1:
            print(f"[{self.id}] Starting first election.")
            self.start_election()
        threading.Thread(target=self.try_execute_orders, daemon=True).start()
        threading.Thread(target=self.monitor_leader, daemon=True).start()

    def Ping(self, request, context):
        return order_executor.PingResponse(is_alive=True)

    def StartElection(self, request, context):
        print(f"[{self.id}] Received election request from {request.id}")
        threading.Thread(target=self.start_election, daemon=True).start()
        return order_executor.ElectionResponse(is_success=True)

    def AnnounceLeader(self, request, context):
        with self.leader_lock:
            self.leader_id = request.leader_id
        return Empty()

    def try_execute_orders(self):
        while self.running:
            time.sleep(5)
            with self.leader_lock:
                if self.leader_id == self.id:
                    print(f"[{self.id}] Leader {self.leader_id} trying to execute.")
                    self.execute_order()

    def execute_order(self):
        try:
            with grpc.insecure_channel('orderqueue:50054') as channel:
                # Create a stub object
                stub = orderqueue_grpc.OrderQueueServiceStub(channel)
                response = stub.Dequeue(Empty())
                if response.orderId:
                    print(f"[{self.id}] Order is being executed, ID: {response.orderId}")
        except Exception as e:
            print(f"[{self.id}] Failed to dequeue: {e}")

    def monitor_leader(self):
        while self.running:
            time.sleep(12)
            with self.leader_lock:
                if self.leader_id != self.id:
                    if self.leader_id is None or not self.ping_leader(self.leader_id):
                        print(f"[{self.id}] Leader [{self.leader_id}] is unresponsive. Starting election.")
                        self.start_election()

    def ping_leader(self, leader_id):
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
        higher_ids = [eid for eid in self.all_addresses if eid > self.id]
        accepted = False

        for eid in higher_ids:
            try:
                address = self.all_addresses[eid]
                with grpc.insecure_channel(address) as channel:
                    stub = order_executor_grpc.OrderExecutorServiceStub(channel)
                    res = stub.StartElection(order_executor.ElectionRequest(id=self.id))
                    if res.is_success:
                        print(f"[{self.id}] Election accepted by {eid}")
                        accepted = True
                        break
            except Exception as e:
                print(f"[{self.id}] Failed to contact {eid} during election: {e}")

        if not accepted:
            print(f"[{self.id}] I am the new leader.")
            with self.leader_lock:
                self.leader_id = self.id
            self.announce_leader()

    def announce_leader(self):
        for eid, address in self.all_addresses.items():
            try:
                with grpc.insecure_channel(address) as channel:
                    stub = order_executor_grpc.OrderExecutorServiceStub(channel)
                    stub.AnnounceLeader(order_executor.LeaderInfo(leader_id=self.id))
            except Exception as e:
                print(f"[{self.id}] Could not announce to {eid}: {e}")

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