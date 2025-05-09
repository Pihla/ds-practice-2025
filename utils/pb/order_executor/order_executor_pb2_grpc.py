# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
import order_executor_pb2 as order__executor__pb2


class OrderExecutorServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.StartElection = channel.unary_unary(
                '/order_executor.OrderExecutorService/StartElection',
                request_serializer=order__executor__pb2.ElectionRequest.SerializeToString,
                response_deserializer=order__executor__pb2.ElectionResponse.FromString,
                )
        self.AnnounceLeader = channel.unary_unary(
                '/order_executor.OrderExecutorService/AnnounceLeader',
                request_serializer=order__executor__pb2.LeaderInfo.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.Ping = channel.unary_unary(
                '/order_executor.OrderExecutorService/Ping',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=order__executor__pb2.PingResponse.FromString,
                )
        self.ExecuteOrders = channel.unary_unary(
                '/order_executor.OrderExecutorService/ExecuteOrders',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )


class OrderExecutorServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def StartElection(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AnnounceLeader(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Ping(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ExecuteOrders(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_OrderExecutorServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'StartElection': grpc.unary_unary_rpc_method_handler(
                    servicer.StartElection,
                    request_deserializer=order__executor__pb2.ElectionRequest.FromString,
                    response_serializer=order__executor__pb2.ElectionResponse.SerializeToString,
            ),
            'AnnounceLeader': grpc.unary_unary_rpc_method_handler(
                    servicer.AnnounceLeader,
                    request_deserializer=order__executor__pb2.LeaderInfo.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'Ping': grpc.unary_unary_rpc_method_handler(
                    servicer.Ping,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=order__executor__pb2.PingResponse.SerializeToString,
            ),
            'ExecuteOrders': grpc.unary_unary_rpc_method_handler(
                    servicer.ExecuteOrders,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'order_executor.OrderExecutorService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class OrderExecutorService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def StartElection(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/order_executor.OrderExecutorService/StartElection',
            order__executor__pb2.ElectionRequest.SerializeToString,
            order__executor__pb2.ElectionResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def AnnounceLeader(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/order_executor.OrderExecutorService/AnnounceLeader',
            order__executor__pb2.LeaderInfo.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Ping(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/order_executor.OrderExecutorService/Ping',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            order__executor__pb2.PingResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ExecuteOrders(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/order_executor.OrderExecutorService/ExecuteOrders',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
