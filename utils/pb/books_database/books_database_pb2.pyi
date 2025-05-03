from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

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

class DecrementStockRequest(_message.Message):
    __slots__ = ("title", "amount")
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    title: str
    amount: int
    def __init__(self, title: _Optional[str] = ..., amount: _Optional[int] = ...) -> None: ...

class DecrementStockResponse(_message.Message):
    __slots__ = ("is_success", "updated_stock", "message")
    IS_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    UPDATED_STOCK_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    is_success: bool
    updated_stock: int
    message: str
    def __init__(self, is_success: bool = ..., updated_stock: _Optional[int] = ..., message: _Optional[str] = ...) -> None: ...
