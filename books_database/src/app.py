import sys
import os
import threading
import time

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
        self.prepared_order_lines = {} # key: book_title, value: (order_id, amount)

    def Read(self, request, context=None):
        stock = self.store.get(request.title, 0)
        return books_database.ReadResponse(stock=stock)

    # Reads value how many books are left when all prepared orders would be executed
    def ReadConsideringPreparedOrders(self, request, context=None):
        stock = self.store.get(request.title, 0)
        orders_with_current_title = self.prepared_order_lines.setdefault(request.title, [])
        for order_id, amount in orders_with_current_title:
            stock -= amount
        return books_database.ReadResponse(stock=stock)

    def Write(self, request, context=None):
        self.store[request.title] = request.new_stock
        return books_database.WriteResponse(is_success=True)

# Class for the primary replica that will handle Writes to backups
class PrimaryReplica(BooksDatabaseService):
    def __init__(self, backup_stubs):
        super().__init__()
        self.backup_stubs = backup_stubs
        self.locks = {}
        # Retires for Write operation on backup stubs
        self.max_retries = 2
        self.retry_delay = 0.5

    def _get_lock(self, title):
        if title not in self.locks:
            self.locks[title] = threading.Lock()
        return self.locks[title]

    def Write(self, request, context=None):
        # Write locally
        self.store[request.title] = request.new_stock
        succeeded_writes = 0
        # Write sequentially to all backups
        for backup_stub in self.backup_stubs:
            for attempt_idx in range(self.max_retries):
                try:
                    with grpc.insecure_channel(backup_stub) as channel:
                        stub = books_database_grpc.BooksDatabaseServiceStub(channel)
                        response = stub.Write(request)
                        if response.is_success:
                            succeeded_writes += 1
                            break
                except Exception as e:
                    print(f"Attempt {attempt_idx+1} failed to replicate to backup stub {backup_stub}, reason: {e}")
                    time.sleep(self.retry_delay)
        if succeeded_writes < len(self.backup_stubs):
            print("Could not replicate to all backup stubs.")
        return books_database.WriteResponse(is_success=True)

    # Checks that there is enough of the book even when all currently prepared orders are filled, adds current order line to prepared order lines
    def Prepare(self, request, context):
        read_request = books_database.ReadRequest(title=request.title)
        read_response = self.ReadConsideringPreparedOrders(read_request)
        stock = read_response.stock
        ready = stock >= request.amount
        self.prepared_order_lines[request.title] = (request.order_id, request.amount)
        print(f"Prepared to remove {request.amount} copies of {request.title} for order {request.order_id}")
        return books_database.PrepareResponse(ready=ready)

    # Removes order line from prepared order lines
    def Abort(self, request, context):
        self.prepared_order_lines.pop(request.title)
        print(f"Aborted removing {request.amount} copies of {request.title} for order {request.order_id}")
        return books_database.AbortResponse(aborted=True)

    # Commits order line by updating value in database
    def Commit(self, request, context):
        success = self.DecrementStock(request.title, request.amount)
        print(f"Committed order {request.order_id} by removing {request.amount} copies of {request.title}")
        return books_database.CommitResponse(success=success)

    def DecrementStock(self, title, amount):
        # Lock each title when working on it
        lock = self._get_lock(title)
        with lock:
            # Handle decrement logic
            read_request = books_database.ReadRequest(title=title)
            read_response = self.Read(read_request)

            new_stock = read_response.stock - amount
            # Writes to local and to backups
            write_request = books_database.WriteRequest(title=title, new_stock=new_stock)
            write_response = self.Write(write_request)
            # If write is done then it is success
            if write_response.is_success:
                return True
            return False

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