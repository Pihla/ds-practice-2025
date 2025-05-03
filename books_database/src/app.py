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

class BooksDatabaseService(books_database_grpc.BooksDatabaseServiceServicer):
    def __init__(self):
        self.store = {
            "The Lord of the Rings": 10,
            "The Twilight" : 10,
        }

    def Read(self, request, context=None):
        stock = self.store.get(request.title, 0)
        return books_database.ReadResponse(stock=stock)

    def Write(self, request, context=None):
        self.store[request.title] = request.new_stock
        return books_database.WriteResponse(is_success=True)

# Class for the primary replica that will handle Writes to backups
class PrimaryReplica(BooksDatabaseService):
    def __init__(self, backup_stubs):
        super().__init__()
        self.backup_stubs = backup_stubs

    def Write(self, request, context=None):
        # Write locally
        self.store[request.title] = request.new_stock
        # Write sequentially to all backups
        for backup_stub in self.backup_stubs:
            try:
                with grpc.insecure_channel(backup_stub) as channel:
                    stub = books_database_grpc.BooksDatabaseServiceStub(channel)
                    response = stub.Write(request)
            except Exception as e:
                print(f"Failed to replicate to backup stub: {e}")
        return books_database.WriteResponse(is_success=True)

    def DecrementStock(self, request, context):
        # Handle decrement logic
        read_request = books_database.ReadRequest(title=request.title)
        read_response = self.Read(read_request)

        # Check if there is enough to buy
        if read_response.stock < request.amount:
            return books_database.DecrementStockResponse(is_success=False, updated_stock=-1, message="Not enough stock.")

        new_stock = read_response.stock - request.amount
        # Writes to local and to backups
        write_request = books_database.WriteRequest(title=request.title, new_stock=new_stock)
        write_response = self.Write(write_request)
        # If write is done then it is success
        if write_response.is_success:
            return books_database.DecrementStockResponse(is_success=True, updated_stock=new_stock, message="Stock updated.")
        return books_database.DecrementStockResponse(is_success=False, updated_stock=-1, message="Unexpected error in write.")

def serve():
    service_id = int(os.getenv("DATABASE_ID"))
    port = 50058 + service_id
    all_addresses = {
        1: "books_database1:50059",
        2: "books_database2:50060",
        3: "books_database3:50061",
    }
    all_addresses.pop(service_id)

    # Set primary replica
    if service_id == 1:
        backup_stubs = all_addresses.values()
        service = PrimaryReplica(backup_stubs)
    else:
        service = BooksDatabaseService()

    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())
    # Add BooksDatabaseService
    books_database_grpc.add_BooksDatabaseServiceServicer_to_server(service, server)
    server.add_insecure_port(f"[::]:{port}")
    # Start the server
    server.start()
    print(f"Database {os.getenv('DATABASE_ID')} Server started. Listening on port {port}.")

    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()