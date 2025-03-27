from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Order(_message.Message):
    __slots__ = ("orderId", "full_request_data", "amount")
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    FULL_REQUEST_DATA_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    full_request_data: str
    amount: str
    def __init__(self, orderId: _Optional[str] = ..., full_request_data: _Optional[str] = ..., amount: _Optional[str] = ...) -> None: ...

class OrderQueueResponse(_message.Message):
    __slots__ = ("is_valid", "message")
    IS_VALID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    is_valid: bool
    message: str
    def __init__(self, is_valid: bool = ..., message: _Optional[str] = ...) -> None: ...
