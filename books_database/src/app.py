import sys
import os

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
books_database_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/books_database'))
sys.path.insert(0, books_database_grpc_path)
import books_database_pb2 as books_database
import books_database_pb2_grpc as books_database_grpc

import grpc
from concurrent import futures


# Create a class to define the server functions, derived from
# books_database_pb2_grpc.BooksDatabaseServiceServicer
class BooksDatabaseService(books_database_grpc.BooksDatabaseServiceServicer):
    def __init__(self):
        self.id = int(os.getenv("DATABASE_ID"))
        self.port = 50058 + self.id

        self.all_addresses = {
            1: "books_database1:50059",
            2: "books_database2:50060",
            3: "books_database3:50061",
        }
        self.all_addresses.pop(self.id)

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())

    # Add BooksDatabaseService
    books_database_grpc.add_BooksDatabaseServiceServicer_to_server(BooksDatabaseService(), server)

    # Listen on port 50059
    port = 50058 + int(os.getenv("DATABASE_ID", "1"))
    server.add_insecure_port(f"[::]:{port}")

    # Start the server
    server.start()
    print(f"Database {os.getenv('DATABASE_ID')} Server started. Listening on port {port}.")

    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()