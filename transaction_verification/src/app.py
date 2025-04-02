import sys
import os
from datetime import datetime
from utils.base_service.BaseService import BaseService

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
transaction_verification_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/transaction_verification'))
sys.path.insert(0, transaction_verification_grpc_path)
import transaction_verification_pb2 as transaction_verification
import transaction_verification_pb2_grpc as transaction_verification_grpc
from google.protobuf.empty_pb2 import Empty

import grpc
from concurrent import futures

# Create a class to define the server functions, derived from
# transaction_verification_pb2_grpc.HelloServiceServicer
class TransactionVerificationService(transaction_verification_grpc.TransactionVerificationServiceServicer, BaseService):
    def __init__(self):
        super().__init__("TransactionVerificationService", 2)

    def InitTransactionVerification(self, request, context):
        self.init_order(request.orderId, request.data)
        return Empty()

    def VerifyTransaction(self, request, context):
        order_data = self.orders[request.orderId]["data"]
        # Check whether terms are accepted
        if not order_data.termsAccepted:
            return transaction_verification.TransactionVerificationResponse(is_valid=False, vector_clock=[0,0,0], message="Terms not accepted.")

        # Check if user info is correct
        if not order_data.user or order_data.user.name == "" or order_data.user.contact == "":
            return transaction_verification.TransactionVerificationResponse(is_valid=False, vector_clock=[0,0,0], message="User info incomplete.")

        # Check if credit card number is correct
        if len(order_data.creditCard.number) != 16 or not order_data.creditCard.number.isdigit():
            return transaction_verification.TransactionVerificationResponse(is_valid=False, vector_clock=[0,0,0], message="Credit card number incorrect.")

        # Check cvv
        if len(order_data.creditCard.cvv) < 3 or len(order_data.creditCard.cvv) > 4:
            return transaction_verification.TransactionVerificationResponse(is_valid=False, vector_clock=[0,0,0], message="Credit card CVV is not 3 or 4 digits.")

        # Check expiration
        year, month = datetime.now().year, datetime.now().month
        expiration_month, expiration_year = map(int, order_data.creditCard.expirationDate.split("/"))
        expiration_year += 2000
        if expiration_month > 12 or expiration_month < 1:
            return transaction_verification.TransactionVerificationResponse(is_valid=False, vector_clock=[0,0,0], message="Credit card expiration date invalid.")
        if not (expiration_year >= year and expiration_month >= month):
            return transaction_verification.TransactionVerificationResponse(is_valid=False, vector_clock=[0,0,0], message="Credit card expired.")

        # Return the response object
        return transaction_verification.TransactionVerificationResponse(is_valid=True, vector_clock=[0,0,0], message="User info and credit card info OK.")

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())

    # Add TransactionVerificationService
    transaction_verification_grpc.add_TransactionVerificationServiceServicer_to_server(TransactionVerificationService(), server)

    # Listen on port 50052
    port = "50052"
    server.add_insecure_port("[::]:" + port)

    # Start the server
    server.start()
    print("Server started. Listening on port 50052.")

    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()