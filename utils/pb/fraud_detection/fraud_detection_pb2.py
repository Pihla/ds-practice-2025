# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: fraud_detection.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15\x66raud_detection.proto\x12\x0f\x66raud_detection\"\'\n\x15\x46raudDetectionRequest\x12\x0e\n\x06\x61mount\x18\x01 \x01(\x05\";\n\x16\x46raudDetectionResponse\x12\x10\n\x08is_valid\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t2z\n\x15\x46raudDetectionService\x12\x61\n\x0e\x46raudDetection\x12&.fraud_detection.FraudDetectionRequest\x1a\'.fraud_detection.FraudDetectionResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'fraud_detection_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_FRAUDDETECTIONREQUEST']._serialized_start=42
  _globals['_FRAUDDETECTIONREQUEST']._serialized_end=81
  _globals['_FRAUDDETECTIONRESPONSE']._serialized_start=83
  _globals['_FRAUDDETECTIONRESPONSE']._serialized_end=142
  _globals['_FRAUDDETECTIONSERVICE']._serialized_start=144
  _globals['_FRAUDDETECTIONSERVICE']._serialized_end=266
# @@protoc_insertion_point(module_scope)
