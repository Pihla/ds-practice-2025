import sys
import os
from concurrent.futures import ThreadPoolExecutor
from concurrent import futures
import uuid
import time

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")

# Set up orchestrator
orchestrator_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/orchestrator'))
sys.path.insert(0, orchestrator_grpc_path)
import orchestrator_pb2 as orchestrator
import orchestrator_pb2_grpc as orchestrator_grpc
from google.protobuf.empty_pb2 import Empty

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

# Set up orderqueue
orderqueue_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/orderqueue'))
sys.path.insert(0, orderqueue_grpc_path)
import orderqueue_pb2 as orderqueue
import orderqueue_pb2_grpc as orderqueue_grpc
import grpc

active_orders = {}

class OrchestratorService(orchestrator_grpc.OrchestratorServiceServicer):
    # Create an RPC function to handle book suggestions
    def AcceptBookSuggestions(self, request, context):
        order_id = request.orderId
        print(f"Received book suggestions for order {order_id}")
        active_orders[order_id] = {"status": "success", "suggested_books": request.suggestedBooks}
        return Empty()

    # Create an RPC function to handle rejected order
    def AcceptOrderNotApprovedMessage(self, request, context):
        order_id = request.orderId
        print(f"Received order not approves message for order {order_id}, message: {request.message}")
        active_orders[order_id] = {"status": "failure", "message": request.message}
        return Empty()

# Sends new order to transaction verification service using gRPC
def send_new_order_to_transaction_verification_service(order_id, data):
    print("Sending new order details to transaction verification service")
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
        stub.UpdateVectorClock(transaction_verification.VectorClockStatus(orderId=order_id, vector_clock=[0, 0, 0]))

# Sends new order to fraud detection service using gRPC
def send_new_order_to_fraud_detection_service(order_id, data):
    print("Sending new order details to fraud detection service")
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        # Create a stub object
        stub = fraud_detection_grpc.FraudDetectionServiceStub(channel)

        # Create transaction object
        fraud_detection_request_data = fraud_detection.Transaction(
            user=
            fraud_detection.User(
                name=data["user"]["name"],
                contact=data["user"]["contact"]
            ),
            creditCard=
            fraud_detection.CreditCard(
                number=data["creditCard"]["number"],
                expirationDate=data["creditCard"]["expirationDate"],
                cvv=data["creditCard"]["cvv"]
            ),
            termsAccepted=data["termsAccepted"]
        )
        stub.InitFraudDetection(fraud_detection.FraudDetectionData(orderId=order_id, data=fraud_detection_request_data))
        stub.UpdateVectorClock(fraud_detection.VectorClockStatus(orderId=order_id, vector_clock=[0, 0, 0]))

# Sends new order to suggestions service using gRPC
def send_new_order_to_suggestions_service(order_id, data):
    print("Sending new order details to suggestions service")
    with grpc.insecure_channel('suggestions:50053') as channel:
        # Create a stub object
        stub = suggestions_grpc.SuggestionsServiceStub(channel)

        # Create list of ordered books
        ordered_books = []
        for item in data["items"]:
            ordered_books.append(suggestions.Book(bookId="000", title=item["name"], author=item["author"]))

        stub.InitSuggestions(suggestions.SuggestionsData(orderId=order_id, data=ordered_books))
        stub.UpdateVectorClock(suggestions.VectorClockStatus(orderId=order_id, vector_clock=[0, 0, 0]))

# Deletes order from suggestions service
def delete_order_from_suggestions_service(order_id, vector_clock):
    print("Deleting order from suggestions service")
    with grpc.insecure_channel('suggestions:50053') as channel:
        stub = suggestions_grpc.SuggestionsServiceStub(channel)
        return stub.DeleteCompletedOrder(suggestions.VectorClockStatus(orderId=order_id, vector_clock=vector_clock))

# Deletes order from fraud detection service
def delete_order_from_fraud_detection_service(order_id, vector_clock):
    print("Deleting order from fraud detection service")
    with grpc.insecure_channel('fraud_detection:50051') as channel:
        stub = fraud_detection_grpc.FraudDetectionServiceStub(channel)
        return stub.DeleteCompletedOrder(fraud_detection.VectorClockStatus(orderId=order_id, vector_clock=vector_clock))

# Deletes order from transaction verification service
def delete_order_from_transaction_verification_service(order_id, vector_clock):
    print("Deleting order from transaction verification service")
    with grpc.insecure_channel('transaction_verification:50052') as channel:
        stub = transaction_verification_grpc.TransactionVerificationServiceStub(channel)
        return stub.DeleteCompletedOrder(transaction_verification.VectorClockStatus(orderId=order_id, vector_clock=vector_clock))


# Enqueues order
def enqueue_order(order_id, data):
    with grpc.insecure_channel('orderqueue:50054') as channel:
        # Create a stub object
        stub = orderqueue_grpc.OrderQueueServiceStub(channel)

        # Find the amount of items for the priority queue
        amount = 0
        for item in data["items"]:
            amount += item["quantity"]

        order_data = orderqueue.Order(orderId=order_id, full_request_data=str(data), amount=str(amount))
        response = stub.Enqueue(order_data)
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

    # Add current order to dictionary of active orders
    active_orders[order_id] = {"status": "processing"}

    # Use threads to send new order details to fraud detection, transaction verification and book suggestions services
    threadpool_executor = ThreadPoolExecutor(max_workers=3)

    for f in [
        send_new_order_to_transaction_verification_service,
        send_new_order_to_fraud_detection_service,
        send_new_order_to_suggestions_service,
    ]:
        threadpool_executor.submit(f, order_id, request_data)

    # Check if order has been processed
    while active_orders[order_id]["status"] == "processing":
        time.sleep(0.1)

    # Check if order is accepted or rejected and construct response to frontend
    if active_orders[order_id]["status"] == "success":
        queue_response = enqueue_order(order_id, request_data)
        if queue_response.is_valid:
            suggested_books = active_orders[order_id]["suggested_books"]
            order_status_response = {
                'orderId': order_id,
                'status': "Order Approved",
                'suggestedBooks': [
                    {"bookId": book.bookId, "title": book.title, "author": book.author}
                    for book in suggested_books
                ]
            }
        else: # if cannot queue the order then cannot process it
            order_status_response = {
                'orderId': order_id,
                'status': "Could not process the order.",
                'suggestedBooks': []
            }
    else:
        failure_message = active_orders[order_id]["message"]
        order_status_response = {
            'orderId': order_id,
            'status': f"Order not approved. {failure_message}",
            'suggestedBooks': []
        }

    # Check if vector clocks are valid in each service and delete order from each service
    with ThreadPoolExecutor(max_workers=3) as executor:
        final_vector_clock = [3,2,1]
        futures = [executor.submit(f, order_id, final_vector_clock) for f in
                   [delete_order_from_transaction_verification_service, delete_order_from_fraud_detection_service, delete_order_from_suggestions_service]]

        all_vector_clocks_ok = all(future.result().everythingOK for future in futures)
        if all_vector_clocks_ok:
            print(f"All vector clocks ok for order {order_id}")
        else:
            print(f"ERROR: mistake with vector clocks for order {order_id}")

    # Delete current order from dictionary of active orders
    del active_orders[order_id]

    return order_status_response


def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())

    # Add OrchestraroeService
    orchestrator_grpc.add_OrchestratorServiceServicer_to_server(OrchestratorService(), server)

    # Listen on port 5001
    port = "5001"
    server.add_insecure_port("[::]:" + port)

    # Start the server
    server.start()
    print(f"Server started. Listening on port {port}.")

    # Keep thread alive
    server.wait_for_termination()

def run():
    # Run the app in debug mode to enable hot reloading.
    # This is useful for development.
    # The default port is 5000.
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(serve)
        executor.submit(run)
