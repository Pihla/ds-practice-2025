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
        try:
            print("Preparing for payment")
            # In real service, funds would be checked here
            transaction_is_possible = True if random.random() < 0.95 else False
            self.prepared = transaction_is_possible
            if transaction_is_possible:
                return payment_pb2.PrepareResponse(ready=True, message = "Transaction prepared")
            else:
                return payment_pb2.PrepareResponse(ready=False, message = "Transaction failed to prepare, because luck was not in your favour :(")
        except Exception as e:
            print(f"Preparing failed with exception: {e}")
            return payment_pb2.PrepareResponse(ready=False, message="Unexpected error while preparing for payment: " + str(e))

    def Commit(self, request, context):
        try:
            print("Committing payment")
            if self.prepared:
                # In real service, money would be subtracted here
                self.prepared = False
                return payment_pb2.CommitResponse(success=True)
            else:
                print(f"Payment not committed for order {request.order_id}")
                return payment_pb2.CommitResponse(success=False)
        except Exception as e:
            print(f"Commit failed with exception: {e}")
            return payment_pb2.CommitResponse(success=False, message="Unexpected error while committing payment: " + str(e))

    def Abort(self, request, context):
        try:
            print("Aborting payment")
            self.prepared = False
            return payment_pb2.AbortResponse(aborted=True, message = "Payment aborted")
        except Exception as e:
            print(f"Aborting failed with exception: {e}")
            return payment_pb2.AbortResponse(aborted=False, message="Unexpected error while aborting payment: " + str(e))

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