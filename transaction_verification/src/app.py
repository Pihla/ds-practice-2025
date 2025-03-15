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

import grpc
from concurrent import futures

# Create a class to define the server functions, derived from
# transaction_verification_pb2_grpc.HelloServiceServicer
class TransactionVerificationService(transaction_verification_grpc.TransactionVerificationServiceServicer, BaseService):
    def __init__(self):
        super().__init__(service_name="TransactionVerificationService")

    # Create an RPC function to say hello
    def VerifyTransaction(self, request, context):
        # Check whether terms are accepted
        if not request.transaction.termsAccepted:
            return transaction_verification.TransactionVerificationResponse(is_valid=False, message="Terms not accepted.")

        # Check if user info is correct
        if not request.transaction.user or request.transaction.user.name == "" or request.transaction.user.contact == "":
            return transaction_verification.TransactionVerificationResponse(is_valid=False, message="User info incomplete.")

        # Check if credit card number is correct
        if len(request.transaction.creditCard.number) != 16 or not request.transaction.creditCard.number.isdigit():
            return transaction_verification.TransactionVerificationResponse(is_valid=False, message="Credit card number incorrect.")

        # Check cvv
        if len(request.transaction.creditCard.cvv) < 3 or len(request.transaction.creditCard.cvv) > 4:
            return transaction_verification.TransactionVerificationResponse(is_valid=False, message="Credit card CVV is not 3 or 4 digits.")

        # Check expiration
        year, month = datetime.now().year, datetime.now().month
        expiration_month, expiration_year = map(int, request.transaction.creditCard.expirationDate.split("/"))
        expiration_year += 2000
        if expiration_month > 12 or expiration_month < 1:
            return transaction_verification.TransactionVerificationResponse(is_valid=False, message="Credit card expiration date invalid.")
        if not (expiration_year >= year and expiration_month >= month):
            return transaction_verification.TransactionVerificationResponse(is_valid=False, message="Credit card expired.")

        # Return the response object
        return transaction_verification.TransactionVerificationResponse(is_valid=True, message="User info and credit card info OK.")

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