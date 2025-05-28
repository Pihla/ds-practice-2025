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

resource = Resource.create(attributes={
    SERVICE_NAME: "orderqueue",
})

number_of_currently_enqueued_orders = 0

class MeasurementItem:
    def __init__(self, value):
        self.value = value
        self.attributes = {}

class MeasurementIterable:
    def __init__(self):
        self.items = [MeasurementItem(0)]

    def __add__(self, value):
        self.items.append(MeasurementItem(value))

    def __iter__(self):
        return iter(self.items)

measurementIterable = MeasurementIterable()

def get_currently_enqueued_orders(options):
    return measurementIterable

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
queue_wait_duration = meter.create_histogram(name="queue.waiting_duration", description="Duration of waiting in the order queue.", unit="s") # Histogram
queued_orders_updown = meter.create_up_down_counter(name="queue.queued_orders", description="Number of orders in queue.") #UpDownCounter
meter.create_observable_gauge(name="orderqueue.currently_enqueued_orders_gauge", callbacks=[get_currently_enqueued_orders],description="Current number of orders in queue (gauge).")


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
        queued_orders_updown.add(1)
        global number_of_currently_enqueued_orders
        number_of_currently_enqueued_orders += 1
        measurementIterable.__add__(number_of_currently_enqueued_orders)
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
                queued_orders_updown.add(-1)
                global number_of_currently_enqueued_orders
                number_of_currently_enqueued_orders -= 1
                measurementIterable.__add__(number_of_currently_enqueued_orders)
                _, _, enqueued_time, order = self.queue.get()
                duration = time.time() - enqueued_time
                print(f"I waited in queue {duration} seconds")
                queue_wait_duration.record(duration)
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