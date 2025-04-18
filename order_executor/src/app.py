import random
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
            time.sleep(5)
            with self.leader_lock:
                if self.leader_id == self.id:
                    print(f"[{self.id}] Leader {self.leader_id} is trying to execute.")
                    self.execute_order()

    def execute_order(self):
        # Node tries to retrive the order from Order Queue
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