import sys
import os
from google import genai
import threading

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
orderqueue_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/orderqueue'))
sys.path.insert(0, orderqueue_grpc_path)
import orderqueue_pb2 as orderqueue
import orderqueue_pb2_grpc as orderqueue_grpc

import grpc
from concurrent import futures

# Create a class to define the server functions, derived from
# orderqueue_pb2_grpc.OrderQueueServiceServicer
class OrderQueueService(orderqueue_grpc.OrderQueueServiceServicer):
    def __init__(self):
        self.lock = threading.Lock()
        self.queue = []

    # Create an RPC function to Enqueue orders
    def Enqueue(self, request, context):
        # TODO lock queue, insert request.orderId
        # TODO return success response
        pass

    # Create an RPC function to Dequeue orders
    def Dequeue(self, request, context):
        # TODO lock queue, pop an order if available
        # TODO return dequeued order or empty result
        pass

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())

    # Add OrderQueueService
    orderqueue_grpc.add_OrderQueueServiceServicer_to_server(OrderQueueService(), server)

    # Listen on port 50054
    port = "50054"
    server.add_insecure_port("[::]:" + port)

    # Start the server
    server.start()
    print("Server started. Listening on port 50054.")

    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()