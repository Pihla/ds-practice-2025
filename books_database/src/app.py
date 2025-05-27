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

# Set up metrics
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

resource = Resource.create(attributes={
    SERVICE_NAME: "books_database",
})

tracerProvider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="observability:4317", insecure=True))
tracerProvider.add_span_processor(processor)
trace.set_tracer_provider(tracerProvider)

reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint="observability:4317", insecure=True)
)
meterProvider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(meterProvider)

meter = metrics.get_meter("books_database.meter")

# Metric
prepared_orders_updown = meter.create_up_down_counter(name="books_database.prepard_order_lines", description="Number of currently prepared order lines waiting for commit.") #UpDownCounter
commit_duration = meter.create_histogram(name="books_database.commit_duration", description="Time taken to commit orders.", unit="s") # Histogram


class BooksDatabaseService(books_database_grpc.BooksDatabaseServiceServicer):
    def __init__(self):
        self.store = {
            "The Lord of the Rings": 100,
            "The Twilight" : 100,
            "The Book Thief": 100,
            "Pride and Prejudice": 100,
        }
        self.prepared_order_lines = {} # key: book_title, value: list of (order_id, amount)

    def Read(self, request, context=None):
        stock = self.store.get(request.title, 0)
        return books_database.ReadResponse(stock=stock)

    # Reads value how many books are left when all prepared orders would be executed
    def ReadConsideringPreparedOrders(self, title, context=None):
        stock = self.store.get(title, 0)
        if title not in self.prepared_order_lines:
            return books_database.ReadResponse(stock=stock)
        for order_id, amount in self.prepared_order_lines[title]:
            stock -= amount
        return books_database.ReadResponse(stock=stock)

    def Write(self, request, context=None):
        self.store[request.title] = request.new_stock
        return books_database.WriteResponse(is_success=True)

    def AddOrderLineToPrepared(self, request, context=None):
        if not request.title in self.prepared_order_lines:
            self.prepared_order_lines[request.title] = set()
        self.prepared_order_lines[request.title].add((request.order_id, request.amount))
        prepared_orders_updown.add(1)
        #print(f"Added order line to prepared ({request.title}): {request.order_id}, {request.amount}")
        return books_database.WriteResponse(is_success=True)

    def RemoveOrderLineFromPrepared(self, request, context=None):
        if request.title in self.prepared_order_lines and (request.order_id, request.amount) in self.prepared_order_lines[request.title]:
            self.prepared_order_lines[request.title].remove((request.order_id, request.amount))
            prepared_orders_updown.add(-1)
            #print(f"Removed order line from prepared ({request.title}): {request.order_id}, {request.amount}")
        else:
            pass
            #print(f"Order line has already been removed or hasn't been initialized ({request.title}): {request.order_id}, {request.amount}")
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

    def AddOrderLineToPreparedAndSendToReplicas(self, request, context=None):
        try:
            # Write locally
            self.AddOrderLineToPrepared(request, context)

            succeeded_writes = 0
            # Write sequentially to all backups
            for backup_stub in self.backup_stubs:
                for attempt_idx in range(self.max_retries):
                    try:
                        with grpc.insecure_channel(backup_stub) as channel:
                            stub = books_database_grpc.BooksDatabaseServiceStub(channel)
                            response = stub.AddOrderLineToPrepared(request)
                            if response.is_success:
                                succeeded_writes += 1
                                break
                    except Exception as e:
                        print(f"Attempt {attempt_idx+1} failed to replicate to backup stub {backup_stub}, reason: {e}")
                        time.sleep(self.retry_delay)
            if succeeded_writes < len(self.backup_stubs):
                print("Could not replicate to all backup stubs.")
        except Exception as e:
            print(f"Error with adding to prepared order lines: {e}")

    def RemoveOrderLineFromPreparedAndSendToReplicas(self, request, context=None):
        try:
            # Write locally
            self.RemoveOrderLineFromPrepared(request, context)

            succeeded_writes = 0
            # Write sequentially to all backups
            for backup_stub in self.backup_stubs:
                for attempt_idx in range(self.max_retries):
                    try:
                        with grpc.insecure_channel(backup_stub) as channel:
                            stub = books_database_grpc.BooksDatabaseServiceStub(channel)
                            response = stub.RemoveOrderLineFromPrepared(request)
                            if response.is_success:
                                succeeded_writes += 1
                                break
                    except Exception as e:
                        print(f"Attempt {attempt_idx + 1} failed to replicate to backup stub {backup_stub}, reason: {e}")
                        time.sleep(self.retry_delay)
            if succeeded_writes < len(self.backup_stubs):
                print("Could not replicate to all backup stubs.")
        except Exception as e:
            print(f"Error with removing from prepared order lines: {e}")


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
        try:
            if request.title in self.prepared_order_lines and (request.order_id, request.amount) in self.prepared_order_lines[request.title]:
                print(f"This order line is already prepared ({request.title}): {request.order_id}, {request.amount}.")
                return books_database.PrepareResponse(ready=True, message="Order line is already prepared")
            print(f"Preparing to remove {request.amount} copies of {request.title} for order {request.order_id}")
            # print(f"Already prepared books: {self.prepared_order_lines}")
            read_response = self.ReadConsideringPreparedOrders(request.title)
            stock = read_response.stock
            enough_books = stock >= request.amount
            self.AddOrderLineToPreparedAndSendToReplicas(request, context)
            if enough_books:
                print(f"Order prepared ({request.title}): {request.order_id}, {request.amount}. Database has enough books.")
                return books_database.PrepareResponse(ready=True, message="Database has enough books")
            else:
                print(f"Order prepare is rejected for book {request.title}. Database doesn't have enough books.")
                return books_database.PrepareResponse(ready=False, message="Database doesn't have enough books")
        except Exception as e:
            print(f"Preparing failed with exception: {e}")
            return books_database.PrepareResponse(ready=False, message="Unexpected error while preparing database: " + str(e))


    # Removes order line from prepared order lines
    def Abort(self, request, context):
        try:
            print(f"Aborting removing {request.amount} copies of {request.title} for order {request.order_id}")
            self.RemoveOrderLineFromPreparedAndSendToReplicas(request, context)
            return books_database.AbortResponse(aborted=True, message = "Database has aborted")
        except Exception as e:
            print(f"Abort failed with exception: {e}")
            return books_database.AbortResponse(aborted=False, message="Unexpected error while aborting database: " + str(e))

    # Commits order line by updating value in database
    def Commit(self, request, context):
        start_time = time.time()
        try:
            if (request.order_id, request.amount) not in self.prepared_order_lines[request.title]:
                print(f"Order line is already committed ({request.title}): {request.order_id}, {request.amount}")
                return books_database.CommitResponse(success=True, message="Order has already been committed")

            print(f"Committing order {request.order_id} by removing {request.amount} copies of {request.title}")
            success = self.DecrementStock(request.title, request.amount)
            self.RemoveOrderLineFromPreparedAndSendToReplicas(request, context)
            duration = time.time() - start_time
            commit_duration.record(duration)
            if success:
                return books_database.CommitResponse(success=True, message = "Order successfully committed")
            else:
                return books_database.CommitResponse(success=False, message = f"Write to database failed")
        except Exception as e:
            print(f"Commit failed with exception: {e}")
            return books_database.CommitResponse(success = False, message = "Unexpected error while committing order: " + str(e))

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
            print("Write failed for some replicas.")
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