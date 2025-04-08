import sys
import os
from google import genai
from utils.base_service.BaseService import BaseService

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
sys.path.insert(0, fraud_detection_grpc_path)
import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc
from google.protobuf.empty_pb2 import Empty

import grpc
from concurrent import futures

def send_message_to_ai(message_to_ai):
    # Get API key from environment variables
    key = os.environ.get("GENAI_API_KEY")

    # Send message to AI API
    print(f"Sending message to AI API for fraud detection. Message: {message_to_ai}")
    client = genai.Client(api_key=key)
    ai_api_response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=message_to_ai
    ).text

    # Convert API response to correct format
    ai_api_response = ai_api_response.split(";")
    response_message = ai_api_response[1].strip()
    if ai_api_response[0] == "True":
        return True, response_message
    elif ai_api_response[0] == "False":
        return False, response_message
    else:
        raise ValueError(f"Expected boolean value, got {ai_api_response}")


# Create a class to define the server functions, derived from
# fraud_detection_pb2_grpc.FraudDetectionServiceServicer
class FraudDetectionService(fraud_detection_grpc.FraudDetectionServiceServicer, BaseService):
    def __init__(self):
        super().__init__("FraudFetectionService", 1)
        self.when_to_execute_methods = [{"method": self.check_user_info_for_fraud, "min_vc_for_exec": [2, 0, 0]},
                                              {"method": self.check_credit_card_info_for_fraud, "min_vc_for_exec": [3, 1, 0]}]

    # Checks user info for fraud
    def check_user_info_for_fraud(self, order_id):
        print("Check user info for fraud")
        order_data = self.orders[order_id]["data"]
        user_info = order_data.user

        # Construct message to AI API
        message_to_ai = "Analyze user info and for the first word give me boolean True or False whether it seems valid (not fraudulent). Then put semicolon and small explanation to customer. User info: " + str(user_info)

        try:
            order_is_valid, validity_message = send_message_to_ai(message_to_ai)
            if not order_is_valid:
                validity_message = "User info is fraudulent. " + validity_message
                print(validity_message)
                self.send_order_failure_to_orchestrator(order_is_valid, validity_message)
                return

        # Use simple fraud detection as fallback
        except Exception as e:
            print(f"Using fraud detection AI API failed. Cause: {e}")
            print("Using simple fraud detection as fallback")

            names = user_info.name.split(" ")
            for name in names:
                if(len(name) < 3):
                    validity_message = f"User info is fraudulent. Name {name} is too short"
                    print(validity_message)
                    self.send_order_failure_to_orchestrator(order_id, validity_message)
                    return

        print("User info OK")


    # Checks credit card info for fraud
    def check_credit_card_info_for_fraud(self, order_id):
        print("Check credit card info for fraud")
        order_data = self.orders[order_id]["data"]
        credit_card_info = order_data.creditCard

        # Construct message to AI API
        message_to_ai = "Analyze the credit card info and for the first word give me boolean True or False whether it seems valid (not fraudulent). Then put semicolon and small explanation to customer. Credit card info: " + str(credit_card_info)

        try:
            order_is_valid, validity_message = send_message_to_ai(message_to_ai)
            if not order_is_valid:
                validity_message = "Order is fraudulent. " + validity_message
                print(validity_message)
                self.send_order_failure_to_orchestrator(order_is_valid, validity_message)
                return

        # Use simple fraud detection as fallback
        except Exception as e:
            print(f"Using fraud detection AI API failed. Cause: {e}")
            print("Using simple fraud detection as fallback")
            if order_data.amount > 50:
                validity_message = f"Order is fraudulent. Amount {order_data.amount} is too high."
                self.send_order_failure_to_orchestrator(order_id, validity_message)
                return

        print("Credit card info OK")

    def InitFraudDetection(self, request, context):
        self.init_order(request.orderId, request.data)
        return Empty()

    # Create an RPC function to detect fraud
    def FraudDetection(self, request, context):
        self.handle_incoming_vector_clock(request.orderId, request.vector_clock)
        response = fraud_detection.FraudDetectionResponse(vector_clock=[0, 0, 0])
        return response

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())

    # Add FraudDetectionService
    fraud_detection_grpc.add_FraudDetectionServiceServicer_to_server(FraudDetectionService(), server)

    # Listen on port 50051
    port = "50051"
    server.add_insecure_port("[::]:" + port)

    # Start the server
    server.start()
    print("Server started. Listening on port 50051.")

    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()