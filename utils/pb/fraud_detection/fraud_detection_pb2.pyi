from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class FraudDetectionRequest(_message.Message):
    __slots__ = ("amount", "full_request_data")
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    FULL_REQUEST_DATA_FIELD_NUMBER: _ClassVar[int]
    amount: int
    full_request_data: str
    def __init__(self, amount: _Optional[int] = ..., full_request_data: _Optional[str] = ...) -> None: ...

class FraudDetectionResponse(_message.Message):
    __slots__ = ("is_valid", "message")
    IS_VALID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    is_valid: bool
    message: str
    def __init__(self, is_valid: bool = ..., message: _Optional[str] = ...) -> None: ...
