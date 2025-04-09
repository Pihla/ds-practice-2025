# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
import suggestions_pb2 as suggestions__pb2


class SuggestionsServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.InitSuggestions = channel.unary_unary(
                '/suggestions.SuggestionsService/InitSuggestions',
                request_serializer=suggestions__pb2.SuggestionsData.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.UpdateVectorClock = channel.unary_unary(
                '/suggestions.SuggestionsService/UpdateVectorClock',
                request_serializer=suggestions__pb2.VectorClockStatus.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.DeleteCompletedOrder = channel.unary_unary(
                '/suggestions.SuggestionsService/DeleteCompletedOrder',
                request_serializer=suggestions__pb2.VectorClockStatus.SerializeToString,
                response_deserializer=suggestions__pb2.DeletionResponse.FromString,
                )


class SuggestionsServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def InitSuggestions(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdateVectorClock(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DeleteCompletedOrder(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SuggestionsServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'InitSuggestions': grpc.unary_unary_rpc_method_handler(
                    servicer.InitSuggestions,
                    request_deserializer=suggestions__pb2.SuggestionsData.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'UpdateVectorClock': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdateVectorClock,
                    request_deserializer=suggestions__pb2.VectorClockStatus.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'DeleteCompletedOrder': grpc.unary_unary_rpc_method_handler(
                    servicer.DeleteCompletedOrder,
                    request_deserializer=suggestions__pb2.VectorClockStatus.FromString,
                    response_serializer=suggestions__pb2.DeletionResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'suggestions.SuggestionsService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class SuggestionsService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def InitSuggestions(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/suggestions.SuggestionsService/InitSuggestions',
            suggestions__pb2.SuggestionsData.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdateVectorClock(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/suggestions.SuggestionsService/UpdateVectorClock',
            suggestions__pb2.VectorClockStatus.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DeleteCompletedOrder(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/suggestions.SuggestionsService/DeleteCompletedOrder',
            suggestions__pb2.VectorClockStatus.SerializeToString,
            suggestions__pb2.DeletionResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
