from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OrderNotApprovedData(_message.Message):
    __slots__ = ("orderId", "message")
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    message: str
    def __init__(self, orderId: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class OrderConfirmedData(_message.Message):
    __slots__ = ("orderId",)
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    def __init__(self, orderId: _Optional[str] = ...) -> None: ...

class Book(_message.Message):
    __slots__ = ("bookId", "title", "author")
    BOOKID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    bookId: str
    title: str
    author: str
    def __init__(self, bookId: _Optional[str] = ..., title: _Optional[str] = ..., author: _Optional[str] = ...) -> None: ...

class BookSuggestions(_message.Message):
    __slots__ = ("orderId", "suggestedBooks")
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    SUGGESTEDBOOKS_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    suggestedBooks: _containers.RepeatedCompositeFieldContainer[Book]
    def __init__(self, orderId: _Optional[str] = ..., suggestedBooks: _Optional[_Iterable[_Union[Book, _Mapping]]] = ...) -> None: ...
