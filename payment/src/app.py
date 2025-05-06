from concurrent import futures
import os
import sys

FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
payment_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/payment'))
sys.path.insert(0, payment_grpc_path)
import payment_pb2
import payment_pb2_grpc as payment_grpc
import random

import grpc


class PaymentService(payment_grpc.PaymentServiceServicer):
    def __init__(self):
        self.prepared = False

    def Prepare(self, request, context):
        # In real service, funds would be checked here
        transaction_is_possible = True if random.random() < 0.95 else False

        self.prepared = transaction_is_possible
        print(f"Answer to prepare request: {self.prepared} for order {request.order_id}")
        return payment_pb2.PrepareResponse(ready=transaction_is_possible)

    def Commit(self, request, context):
        if self.prepared:
            print(f"Payment committed for order {request.order_id}")
            # In real service, money would be subtracted here
            self.prepared = False
            return payment_pb2.CommitResponse(success=True)
        else:
            print(f"Payment not committed for order {request.order_id}")
            return payment_pb2.CommitResponse(success=False)

    def Abort(self, request, context):
        self.prepared = False
        print(f"Payment aborted for order {request.order_id}")
        return payment_pb2.AbortResponse(aborted=True)

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())

    # Add Service
    payment_grpc.add_PaymentServiceServicer_to_server(PaymentService(), server)

    # Listen on port
    port = "50062"
    server.add_insecure_port("[::]:" + port)

    # Start the server
    server.start()
    print(f"Server started. Listening on port {port}.")

    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()