from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class User(_message.Message):
    __slots__ = ("name", "contact")
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONTACT_FIELD_NUMBER: _ClassVar[int]
    name: str
    contact: str
    def __init__(self, name: _Optional[str] = ..., contact: _Optional[str] = ...) -> None: ...

class CreditCard(_message.Message):
    __slots__ = ("number", "expirationDate", "cvv")
    NUMBER_FIELD_NUMBER: _ClassVar[int]
    EXPIRATIONDATE_FIELD_NUMBER: _ClassVar[int]
    CVV_FIELD_NUMBER: _ClassVar[int]
    number: str
    expirationDate: str
    cvv: str
    def __init__(self, number: _Optional[str] = ..., expirationDate: _Optional[str] = ..., cvv: _Optional[str] = ...) -> None: ...

class Transaction(_message.Message):
    __slots__ = ("user", "creditCard", "termsAccepted")
    USER_FIELD_NUMBER: _ClassVar[int]
    CREDITCARD_FIELD_NUMBER: _ClassVar[int]
    TERMSACCEPTED_FIELD_NUMBER: _ClassVar[int]
    user: User
    creditCard: CreditCard
    termsAccepted: bool
    def __init__(self, user: _Optional[_Union[User, _Mapping]] = ..., creditCard: _Optional[_Union[CreditCard, _Mapping]] = ..., termsAccepted: bool = ...) -> None: ...

class TransactionVerificationData(_message.Message):
    __slots__ = ("orderId", "data")
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    data: Transaction
    def __init__(self, orderId: _Optional[str] = ..., data: _Optional[_Union[Transaction, _Mapping]] = ...) -> None: ...

class VectorClockStatus(_message.Message):
    __slots__ = ("orderId", "vector_clock")
    ORDERID_FIELD_NUMBER: _ClassVar[int]
    VECTOR_CLOCK_FIELD_NUMBER: _ClassVar[int]
    orderId: str
    vector_clock: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, orderId: _Optional[str] = ..., vector_clock: _Optional[_Iterable[int]] = ...) -> None: ...

class DeletionResponse(_message.Message):
    __slots__ = ("everythingOK", "message")
    EVERYTHINGOK_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    everythingOK: bool
    message: str
    def __init__(self, everythingOK: bool = ..., message: _Optional[str] = ...) -> None: ...
