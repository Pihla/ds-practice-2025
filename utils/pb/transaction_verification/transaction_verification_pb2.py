# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: transaction_verification.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1etransaction_verification.proto\x12\x18transaction_verification\x1a\x1bgoogle/protobuf/empty.proto\"%\n\x04User\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontact\x18\x02 \x01(\t\"A\n\nCreditCard\x12\x0e\n\x06number\x18\x01 \x01(\t\x12\x16\n\x0e\x65xpirationDate\x18\x02 \x01(\t\x12\x0b\n\x03\x63vv\x18\x03 \x01(\t\"\x8c\x01\n\x0bTransaction\x12,\n\x04user\x18\x01 \x01(\x0b\x32\x1e.transaction_verification.User\x12\x38\n\ncreditCard\x18\x02 \x01(\x0b\x32$.transaction_verification.CreditCard\x12\x15\n\rtermsAccepted\x18\x03 \x01(\x08\"c\n\x1bTransactionVerificationData\x12\x0f\n\x07orderId\x18\x01 \x01(\t\x12\x33\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32%.transaction_verification.Transaction\"G\n\x1eTransactionVerificationRequest\x12\x0f\n\x07orderId\x18\x01 \x01(\t\x12\x14\n\x0cvector_clock\x18\x02 \x03(\x05\"Z\n\x1fTransactionVerificationResponse\x12\x10\n\x08is_valid\x18\x01 \x01(\x08\x12\x14\n\x0cvector_clock\x18\x02 \x03(\x05\x12\x0f\n\x07message\x18\x03 \x01(\t2\x99\x02\n\x1eTransactionVerificationService\x12l\n\x1bInitTransactionVerification\x12\x35.transaction_verification.TransactionVerificationData\x1a\x16.google.protobuf.Empty\x12\x88\x01\n\x11VerifyTransaction\x12\x38.transaction_verification.TransactionVerificationRequest\x1a\x39.transaction_verification.TransactionVerificationResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'transaction_verification_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_USER']._serialized_start=89
  _globals['_USER']._serialized_end=126
  _globals['_CREDITCARD']._serialized_start=128
  _globals['_CREDITCARD']._serialized_end=193
  _globals['_TRANSACTION']._serialized_start=196
  _globals['_TRANSACTION']._serialized_end=336
  _globals['_TRANSACTIONVERIFICATIONDATA']._serialized_start=338
  _globals['_TRANSACTIONVERIFICATIONDATA']._serialized_end=437
  _globals['_TRANSACTIONVERIFICATIONREQUEST']._serialized_start=439
  _globals['_TRANSACTIONVERIFICATIONREQUEST']._serialized_end=510
  _globals['_TRANSACTIONVERIFICATIONRESPONSE']._serialized_start=512
  _globals['_TRANSACTIONVERIFICATIONRESPONSE']._serialized_end=602
  _globals['_TRANSACTIONVERIFICATIONSERVICE']._serialized_start=605
  _globals['_TRANSACTIONVERIFICATIONSERVICE']._serialized_end=886
# @@protoc_insertion_point(module_scope)
