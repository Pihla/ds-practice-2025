# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: payment.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rpayment.proto\x12\x07payment\"\"\n\x0ePrepareRequest\x12\x10\n\x08order_id\x18\x01 \x01(\t\"1\n\x0fPrepareResponse\x12\r\n\x05ready\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"!\n\rCommitRequest\x12\x10\n\x08order_id\x18\x01 \x01(\t\"2\n\x0e\x43ommitResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\" \n\x0c\x41\x62ortRequest\x12\x10\n\x08order_id\x18\x01 \x01(\t\"1\n\rAbortResponse\x12\x0f\n\x07\x61\x62orted\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t2\xc1\x01\n\x0ePaymentService\x12<\n\x07Prepare\x12\x17.payment.PrepareRequest\x1a\x18.payment.PrepareResponse\x12\x39\n\x06\x43ommit\x12\x16.payment.CommitRequest\x1a\x17.payment.CommitResponse\x12\x36\n\x05\x41\x62ort\x12\x15.payment.AbortRequest\x1a\x16.payment.AbortResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'payment_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_PREPAREREQUEST']._serialized_start=26
  _globals['_PREPAREREQUEST']._serialized_end=60
  _globals['_PREPARERESPONSE']._serialized_start=62
  _globals['_PREPARERESPONSE']._serialized_end=111
  _globals['_COMMITREQUEST']._serialized_start=113
  _globals['_COMMITREQUEST']._serialized_end=146
  _globals['_COMMITRESPONSE']._serialized_start=148
  _globals['_COMMITRESPONSE']._serialized_end=198
  _globals['_ABORTREQUEST']._serialized_start=200
  _globals['_ABORTREQUEST']._serialized_end=232
  _globals['_ABORTRESPONSE']._serialized_start=234
  _globals['_ABORTRESPONSE']._serialized_end=283
  _globals['_PAYMENTSERVICE']._serialized_start=286
  _globals['_PAYMENTSERVICE']._serialized_end=479
# @@protoc_insertion_point(module_scope)
