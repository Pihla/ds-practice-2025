import sys
import os
from google import genai
from utils.base_service.BaseService import BaseService

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
suggestions_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/suggestions'))
sys.path.insert(0, suggestions_grpc_path)
import suggestions_pb2 as suggestions
import suggestions_pb2_grpc as suggestions_grpc
from google.protobuf.empty_pb2 import Empty

import grpc
from concurrent import futures

# Create a class to define the server functions, derived from
# suggestions_pb2_grpc.SuggestionsServiceServicer
class SuggestionsService(suggestions_grpc.SuggestionsServiceServicer, BaseService):
    def __init__(self):
        super().__init__("SuggestionsService", 1)

    def InitSuggestions(self, request, context):
        self.init_order(request.orderId, request.data)
        return Empty()

    # Create an RPC function
    def Suggest(self, request, context):
        order_data = self.orders[request.orderId]["data"]
        # Try using online AI
        try:
            # Get API key from environment variables
            key = os.environ.get("GENAI_API_KEY")

            # Construct message to AI API
            message_to_ai = "Give me 1 to 3 book suggestions that are different from those books. ONLY reply with the book name and author name separated by a comma. Separate each book with semicolon. INFO: " + str(order_data)

            # Send message to AI API
            print(f"Sending message to suggestions AI API")
            client = genai.Client(api_key=key)
            ai_api_response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=message_to_ai
            ).text
            print(f"Suggestions AI API responded: {ai_api_response}")

            # Convert API response to correct format
            ai_api_response = ai_api_response.split(";")
            ai_api_response = [ai_api_response[i].split(",") for i in range(len(ai_api_response))]
            suggested_books = [suggestions.Book(bookId="000", title=book[0].strip(), author=book[1].strip()) for book in ai_api_response]
            return suggestions.SuggestionsResponse(vector_clock=[0,0,0], suggestedBooks=suggested_books)

        # Use dummy suggestion as fallback
        except Exception as e:
            print(f"Using suggestions AI API failed. Cause: {e}")
            print("Using dummy suggestions as fallback.")
            suggested_books = [
                suggestions.Book(bookId="000", title="Rehepapp", author="Andrus Kivirähk"),
                suggestions.Book(bookId="000", title="Kevade", author="Oskar Luts")
            ]
            response = suggestions.SuggestionsResponse(vector_clock=[0,0,0], suggestedBooks=suggested_books)

        # Return the response object
        return response

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())

    # Add SuggestionsService
    suggestions_grpc.add_SuggestionsServiceServicer_to_server(SuggestionsService(), server)

    # Listen on port 50053
    port = "50053"
    server.add_insecure_port("[::]:" + port)

    # Start the server
    server.start()
    print("Server started. Listening on port 50053.")

    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()