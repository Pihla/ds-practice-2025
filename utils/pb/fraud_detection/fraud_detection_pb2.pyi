from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OrderData(_message.Message):
    __slots__ = ("amount", "full_request_data")
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    FULL_REQUEST_DATA_FIELD_NUMBER: _ClassVar[int]
    amount: int
    full_request_data: str
    def __init__(self, amount: _Optional[int] = ..., full_request_data: _Optional[str] = ...) -> None: ...

class FraudDetectionData(_message.Message):
    __slots__ = ("orderId", "data")
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    data: OrderData
    def __init__(self, orderId: _Optional[str] = ..., data: _Optional[_Union[OrderData, _Mapping]] = ...) -> None: ...

class FraudDetectionRequest(_message.Message):
    __slots__ = ("orderId", "vector_clock")
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    VECTOR_CLOCK_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    vector_clock: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, orderId: _Optional[str] = ..., vector_clock: _Optional[_Iterable[int]] = ...) -> None: ...

class FraudDetectionResponse(_message.Message):
    __slots__ = ("is_valid", "vector_clock", "message")
    IS_VALID_FIELD_NUMBER: _ClassVar[int]
    VECTOR_CLOCK_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    is_valid: bool
    vector_clock: _containers.RepeatedScalarFieldContainer[int]
    message: str
    def __init__(self, is_valid: bool = ..., vector_clock: _Optional[_Iterable[int]] = ..., message: _Optional[str] = ...) -> None: ...
