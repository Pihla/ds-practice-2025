from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GenericBookRequest(_message.Message):
    __slots__ = ("order_id", "title", "amount")
    ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    order_id: str
    title: str
    amount: int
    def __init__(self, order_id: _Optional[str] = ..., title: _Optional[str] = ..., amount: _Optional[int] = ...) -> None: ...

class PrepareResponse(_message.Message):
    __slots__ = ("ready", "message")
    READY_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    ready: bool
    message: str
    def __init__(self, ready: bool = ..., message: _Optional[str] = ...) -> None: ...

class CommitResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class AbortResponse(_message.Message):
    __slots__ = ("aborted", "message")
    ABORTED_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    aborted: bool
    message: str
    def __init__(self, aborted: bool = ..., message: _Optional[str] = ...) -> None: ...

class ReadRequest(_message.Message):
    __slots__ = ("title",)
    TITLE_FIELD_NUMBER: _ClassVar[int]
    title: str
    def __init__(self, title: _Optional[str] = ...) -> None: ...

class ReadResponse(_message.Message):
    __slots__ = ("stock",)
    STOCK_FIELD_NUMBER: _ClassVar[int]
    stock: int
    def __init__(self, stock: _Optional[int] = ...) -> None: ...

class WriteRequest(_message.Message):
    __slots__ = ("title", "new_stock")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    NEW_STOCK_FIELD_NUMBER: _ClassVar[int]
    title: str
    new_stock: int
    def __init__(self, title: _Optional[str] = ..., new_stock: _Optional[int] = ...) -> None: ...

class WriteResponse(_message.Message):
    __slots__ = ("is_success",)
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    def __init__(self, is_success: bool = ...) -> None: ...
