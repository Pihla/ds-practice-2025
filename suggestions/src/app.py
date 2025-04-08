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

orchestrator_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/orchestrator'))
sys.path.insert(0, orchestrator_grpc_path)
import orchestrator_pb2 as orchestrator
import orchestrator_pb2_grpc as orchestrator_grpc

import grpc
from concurrent import futures

# Create a class to define the server functions, derived from
# suggestions_pb2_grpc.SuggestionsServiceServicer
class SuggestionsService(suggestions_grpc.SuggestionsServiceServicer, BaseService):
    def __init__(self):
        super().__init__("SuggestionsService", 2)
        self.when_to_execute_methods = [{"method": self.find_suggestions_and_send_to_orchestrator, "min_vc_for_exec": [3, 2, 0]}]

    # Finds book suggestions and sends them to orchestrator
    def find_suggestions_and_send_to_orchestrator(self, order_id):
        print("Find suggestions.")
        ordered_books = self.orders[order_id]["data"]

        # Try using online AI
        try:
            # Get API key from environment variables
            key = os.environ.get("GENAI_API_KEY")

            # Construct message to AI API
            message_to_ai = "Give me 1 to 3 book suggestions that are different from those books. ONLY reply with the book name and author name separated by a comma. Separate each book with semicolon. INFO: " + str(
                ordered_books)

            # Send message to AI API
            print(f"Sending message to suggestions AI API. Message: {message_to_ai}")
            client = genai.Client(api_key=key)
            ai_api_response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=message_to_ai
            ).text
            print(f"Suggestions AI API responded: {ai_api_response}")

            # Convert API response to correct format
            ai_api_response = ai_api_response.split(";")
            ai_api_response = [ai_api_response[i].split(",") for i in range(len(ai_api_response))]
            suggested_books = [orchestrator.Book(bookId="000", title=book[0].strip(), author=book[1].strip()) for book in
                               ai_api_response]

        # Use dummy suggestion as fallback
        except Exception as e:
            print(f"Using suggestions AI API failed. Cause: {e}")
            print("Using dummy suggestions as fallback.")
            suggested_books = [
                suggestions.Book(bookId="000", title="Rehepapp", author="Andrus Kivirähk"),
                suggestions.Book(bookId="000", title="Kevade", author="Oskar Luts")
            ]

        # Send book suggestions to orchestrator
        with grpc.insecure_channel('orchestrator:5001') as channel:
            stub = orchestrator_grpc.OrchestratorServiceStub(channel)
            book_suggestions = orchestrator.BookSuggestions(orderId=order_id, suggestedBooks = suggested_books)
            print(f"Sending Book Suggestions: {book_suggestions}")
            stub.AcceptBookSuggestions(book_suggestions)

    def InitSuggestions(self, request, context):
        self.init_order(request.orderId, request.data)
        return Empty()

    # Create an RPC function
    def Suggest(self, request, context):
        order_id = request.orderId
        self.handle_incoming_vector_clock(order_id, request.vector_clock)

        suggested_books = [
            suggestions.Book(bookId="000", title="Rehepapp", author="Andrus Kivirähk"),
            suggestions.Book(bookId="000", title="Kevade", author="Oskar Luts")
        ]
        response = suggestions.SuggestionsResponse(vector_clock=[0, 0, 0], suggestedBooks=suggested_books)
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