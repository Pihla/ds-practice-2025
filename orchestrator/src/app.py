import sys
import os
from concurrent.futures import ThreadPoolExecutor
import uuid

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


import grpc

def detect_fraud(order_id, data):
    print("Fraud detection in progress")

    # Establish a connection with the fraud-detection gRPC service
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        # Create a stub object
        stub = fraud_detection_grpc.FraudDetectionServiceStub(channel)

        # Calculate total amount of items
        amount = 0
        for item in data["items"]:
            amount += item["quantity"]

        order_data = fraud_detection.OrderData(amount=amount, full_request_data=str(data))
        stub.InitFraudDetection(fraud_detection.FraudDetectionData(orderId=order_id, data=order_data))
        # Call the service through the stub object
        response = stub.FraudDetection(fraud_detection.FraudDetectionRequest(orderId=order_id, vector_clock=[0,0,0]))
        #print(response)
    print("Fraud detection finished")
    return response

def suggest_books(order_id, data):
    print("Getting suggestions")
    with grpc.insecure_channel('suggestions:50053') as channel:
        # Create a stub object
        stub = suggestions_grpc.SuggestionsServiceStub(channel)

        # Create list of ordered books
        ordered_books = []
        for item in data["items"]:
            ordered_books.append(suggestions.Book(bookId="000", title=item["name"], author=item["author"]))

        stub.InitSuggestions(suggestions.SuggestionsData(orderId=order_id, data=ordered_books))
        # Call the service through the stub object
        response = stub.Suggest(suggestions.SuggestionsRequest(orderId=order_id, vector_clock=[0,0,0]))
        #print(response)
    return response

def verify_transaction(order_id, data):
    print("Transaction verification in progress")
    with grpc.insecure_channel('transaction_verification:50052') as channel:
        # Create a stub object
        stub = transaction_verification_grpc.TransactionVerificationServiceStub(channel)

        # Create transaction object
        transaction_request_data = transaction_verification.Transaction(
            user=
                transaction_verification.User(
                    name=data["user"]["name"],
                    contact=data["user"]["contact"]
                ),
            creditCard=
                transaction_verification.CreditCard(
                    number=data["creditCard"]["number"],
                    expirationDate=data["creditCard"]["expirationDate"],
                    cvv=data["creditCard"]["cvv"]
                ),
            termsAccepted=data["termsAccepted"]
        )
        stub.InitTransactionVerification(transaction_verification.TransactionVerificationData(orderId=order_id, data=transaction_request_data))
        # Call the service through the stub object
        response = stub.VerifyTransaction(transaction_verification.TransactionVerificationRequest(orderId=order_id, vector_clock=[0,0,0]))
        #print(response)
    print("Transaction verification finished")
    return response

# Import Flask.
# Flask is a web framework for Python.
# It allows you to build a web application quickly.
# For more information, see https://flask.palletsprojects.com/en/latest/
from flask import Flask, request
from flask_cors import CORS
import json

# Create a simple Flask app
app = Flask(__name__)
# Enable CORS for the app
CORS(app, resources={r'/*': {'origins': '*'}})

# Define a GET endpoint
@app.route('/', methods=['GET'])
def index():
    """
    Responds with 'Hello!' when a GET request is made to '/' endpoint.
    """
    print("Received GET REQUEST")
    response = "Hello!"
    # Return the response
    return response

@app.route('/checkout', methods=['POST'])
def checkout():
    """
    Responds with a JSON object containing the order ID, status, and suggested books.
    """
    # Get request object data to json
    print("Received POST REQUEST /checkout")
    request_data = json.loads(request.data)

    # Print request object data
    print("POST REQUEST Data:", request_data)

    # Define order id
    order_id = str(uuid.uuid4())

    # Use threads for fraud detection, transaction verification and book suggestions
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(f, order_id, request_data) for f in [detect_fraud, verify_transaction, suggest_books]]
        fraud_detection_response, transaction_verification_response, suggestions_response = [future.result() for future in futures]


    #TODO iga meetodi thread ja event ordering.
    # a - terms accepted (TV)
    # b - user info ok (TV)
    # c - credit card info ok (TV)
    # d - fraud detect user (FD)
    # e - fraud detect credit card (FD)
    # f - suggestions (S)

    # a võib samal ajal kui b
    # c peale a-d (aga võib samal ajal kui b)
    # d peale b-d, aga võib samal ajal kui c
    # e peale c ja d
    # f peale e

    if fraud_detection_response.is_valid and transaction_verification_response.is_valid:
        order_status_response = {
            'orderId': order_id,
            'status': "Order Approved",
            'suggestedBooks': [
            {"bookId": book.bookId, "title": book.title, "author": book.author}
            for book in suggestions_response.suggestedBooks
            ]
        }
    else:
        order_status_response = {
            'orderId': order_id,
            'status': f"Order not approved. \n{fraud_detection_response.message}\n{transaction_verification_response.message}",
            'suggestedBooks': []
        }
    return order_status_response


if __name__ == '__main__':
    # Run the app in debug mode to enable hot reloading.
    # This is useful for development.
    # The default port is 5000.
    app.run(host='0.0.0.0')
