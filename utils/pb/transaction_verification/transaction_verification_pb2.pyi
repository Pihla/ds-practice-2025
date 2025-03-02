from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

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

class TransactionVerificationRequest(_message.Message):
    __slots__ = ("transaction",)
    TRANSACTION_FIELD_NUMBER: _ClassVar[int]
    transaction: Transaction
    def __init__(self, transaction: _Optional[_Union[Transaction, _Mapping]] = ...) -> None: ...

class TransactionVerificationResponse(_message.Message):
    __slots__ = ("is_valid", "message")
    IS_VALID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    is_valid: bool
    message: str
    def __init__(self, is_valid: bool = ..., message: _Optional[str] = ...) -> None: ...
