import sys
import os
import threading
import time

# This set of lines are needed to import the gRPC stubs.
# The path of the stubs is relative to the current file, or absolute inside the container.
# Change these lines only if strictly needed.
FILE = __file__ if '__file__' in globals() else os.getenv("PYTHONFILE", "")
orderqueue_grpc_path = os.path.abspath(os.path.join(FILE, '../../../utils/pb/orderqueue'))
sys.path.insert(0, orderqueue_grpc_path)
import orderqueue_pb2 as orderqueue
import orderqueue_pb2_grpc as orderqueue_grpc

import grpc
from concurrent import futures
import queue
import itertools


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

# Service name is required for most backends
resource = Resource.create(attributes={
    SERVICE_NAME: "orderqueue",
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

meter = metrics.get_meter("orderqueue.meter")

# Metric
processing_duration = meter.create_histogram(name="orders.waiting_duration", description="Duration of waiting in queue.", unit="s") # Histogram


# Create a class to define the server functions, derived from
# orderqueue_pb2_grpc.OrderQueueServiceServicer
class OrderQueueService(orderqueue_grpc.OrderQueueServiceServicer):
    def __init__(self):
        self.lock = threading.Lock()
        self.queue = queue.PriorityQueue()
        # Counter is needed because if there is already same priority item in queue then need a tiebreak
        self.counter = itertools.count()

    # Create an RPC function to Enqueue orders
    def Enqueue(self, request, context):
        print("Enqueueing order", str(request.orderId))

        # Extract the amount to determine priority
        try:
            amount = int(request.amount)
        except ValueError:
            amount = 1
        enqueued_time = time.time()

        with self.lock: # Orders with bigger amount are more important
            # Counter is used because if orders have the same  priority then insert new one after the earlier one
            self.queue.put((-amount, next(self.counter), enqueued_time, request))

        return orderqueue.OrderQueueResponse(is_valid=True, message="Order enqueued")

    # Create an RPC function to Dequeue orders
    def Dequeue(self, request, context):
        with self.lock:
            if not self.queue.empty():
                _, _, enqueued_time, order = self.queue.get()
                duration = time.time() - enqueued_time
                processing_duration.record(duration, attributes={"queue": "queued_orders"})
                return order
        return orderqueue.Order() # If nothing in queue, return empty Order

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor())

    # Add OrderQueueService
    orderqueue_grpc.add_OrderQueueServiceServicer_to_server(OrderQueueService(), server)

    # Listen on port 50054
    port = "50054"
    server.add_insecure_port("[::]:" + port)

    # Start the server
    server.start()
    print("Server started. Listening on port 50054.")

    # Keep thread alive
    server.wait_for_termination()

if __name__ == '__main__':
    serve()