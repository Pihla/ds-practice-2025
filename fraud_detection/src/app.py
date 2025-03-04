import sys
import os
from google import genai

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
fraud_detection_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/fraud_detection'))
sys.path.insert(0, fraud_detection_grpc_path)
import fraud_detection_pb2 as fraud_detection
import fraud_detection_pb2_grpc as fraud_detection_grpc

import grpc
from concurrent import futures

# Create a class to define the server functions, derived from
# fraud_detection_pb2_grpc.FraudDetectionServiceServicer
class FraudDetectionService(fraud_detection_grpc.FraudDetectionServiceServicer):

    # Create an RPC function to detect fraud
    def FraudDetection(self, request, context):
        # Create a FraudDetectionResponse object
        response = fraud_detection.FraudDetectionResponse()

        # Try using online AI
        try:
            # Get API key from environment variables
            key = os.environ.get("GENAI_API_KEY")

            # Construct message to AI API
            message_to_ai = "Analyze the book order and give me boolean True or False whether it seems valid (not fraudulent). Then put semicolon and small explanation to customer. Order: " + str(request)

            # Send message to AI API
            print(f"Sending message to AI API for fraud detection")
            client = genai.Client(api_key=key)
            ai_api_response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=message_to_ai
            ).text
            print(f"AI API responded to fraud detection: {ai_api_response}")

            # Convert API response to correct format
            ai_api_response = ai_api_response.split(";")
            if ai_api_response[0] == "True":
                response.is_valid = True
            elif ai_api_response[0] == "False":
                response.is_valid = False
            else:
                raise ValueError(f"Expected boolean value, got {ai_api_response}")
            response.message = ai_api_response[1].strip()

        # Use simple fraud detection as fallback
        except Exception as e:
            print(f"Using fraud detection AI API failed. Cause: {e}")
            print("Using simple fraud detection as fallback.")

            # Set the fields of the response object
            if 0 < request.amount < 50:
                response.is_valid = True
                response.message = f"Order is not fraudulent. (nr of items: {request.amount})"
            else:
                response.is_valid = False
                response.message = f"Order is fraudulent. Too many items ({request.amount})."

        # Print the message
        print(response.message)

        # Return the response object
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