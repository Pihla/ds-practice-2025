from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Book(_message.Message):
    __slots__ = ("bookId", "title", "author")
    BOOKID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    AUTHOR_FIELD_NUMBER: _ClassVar[int]
    bookId: str
    title: str
    author: str
    def __init__(self, bookId: _Optional[str] = ..., title: _Optional[str] = ..., author: _Optional[str] = ...) -> None: ...

class SuggestionsData(_message.Message):
    __slots__ = ("orderId", "data")
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    data: _containers.RepeatedCompositeFieldContainer[Book]
    def __init__(self, orderId: _Optional[str] = ..., data: _Optional[_Iterable[_Union[Book, _Mapping]]] = ...) -> None: ...

class SuggestionsRequest(_message.Message):
    __slots__ = ("orderId", "vector_clock")
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    VECTOR_CLOCK_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    vector_clock: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, orderId: _Optional[str] = ..., vector_clock: _Optional[_Iterable[int]] = ...) -> None: ...

class SuggestionsResponse(_message.Message):
    __slots__ = ("vector_clock", "suggestedBooks")
    VECTOR_CLOCK_FIELD_NUMBER: _ClassVar[int]
    SUGGESTEDBOOKS_FIELD_NUMBER: _ClassVar[int]
    vector_clock: _containers.RepeatedScalarFieldContainer[int]
    suggestedBooks: _containers.RepeatedCompositeFieldContainer[Book]
    def __init__(self, vector_clock: _Optional[_Iterable[int]] = ..., suggestedBooks: _Optional[_Iterable[_Union[Book, _Mapping]]] = ...) -> None: ...
