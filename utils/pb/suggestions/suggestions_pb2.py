# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: suggestions.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11suggestions.proto\x12\x05hello\"\x1c\n\x0cHelloRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\"!\n\rHelloResponse\x12\x10\n\x08greeting\x18\x01 \x01(\t2E\n\x0cHelloService\x12\x35\n\x08SayHello\x12\x13.hello.HelloRequest\x1a\x14.hello.HelloResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'suggestions_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_HELLOREQUEST']._serialized_start=28
  _globals['_HELLOREQUEST']._serialized_end=56
  _globals['_HELLORESPONSE']._serialized_start=58
  _globals['_HELLORESPONSE']._serialized_end=91
  _globals['_HELLOSERVICE']._serialized_start=93
  _globals['_HELLOSERVICE']._serialized_end=162
# @@protoc_insertion_point(module_scope)
