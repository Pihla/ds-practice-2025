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


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11suggestions.proto\x12\x0bsuggestions\x1a\x1bgoogle/protobuf/empty.proto\"5\n\x04\x42ook\x12\x0e\n\x06\x62ookId\x18\x01 \x01(\t\x12\r\n\x05title\x18\x02 \x01(\t\x12\x0e\n\x06\x61uthor\x18\x03 \x01(\t\"C\n\x0fSuggestionsData\x12\x0f\n\x07orderId\x18\x01 \x01(\t\x12\x1f\n\x04\x64\x61ta\x18\x02 \x03(\x0b\x32\x11.suggestions.Book\":\n\x11VectorClockStatus\x12\x0f\n\x07orderId\x18\x01 \x01(\t\x12\x14\n\x0cvector_clock\x18\x02 \x03(\x05\"9\n\x10\x44\x65letionResponse\x12\x14\n\x0c\x65verythingOK\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t2\x81\x02\n\x12SuggestionsService\x12G\n\x0fInitSuggestions\x12\x1c.suggestions.SuggestionsData\x1a\x16.google.protobuf.Empty\x12K\n\x11UpdateVectorClock\x12\x1e.suggestions.VectorClockStatus\x1a\x16.google.protobuf.Empty\x12U\n\x14\x44\x65leteCompletedOrder\x12\x1e.suggestions.VectorClockStatus\x1a\x1d.suggestions.DeletionResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'suggestions_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_BOOK']._serialized_start=63
  _globals['_BOOK']._serialized_end=116
  _globals['_SUGGESTIONSDATA']._serialized_start=118
  _globals['_SUGGESTIONSDATA']._serialized_end=185
  _globals['_VECTORCLOCKSTATUS']._serialized_start=187
  _globals['_VECTORCLOCKSTATUS']._serialized_end=245
  _globals['_DELETIONRESPONSE']._serialized_start=247
  _globals['_DELETIONRESPONSE']._serialized_end=304
  _globals['_SUGGESTIONSSERVICE']._serialized_start=307
  _globals['_SUGGESTIONSSERVICE']._serialized_end=564
# @@protoc_insertion_point(module_scope)
