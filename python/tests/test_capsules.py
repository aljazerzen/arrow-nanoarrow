# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
import pyarrow as pa
import pytest

import nanoarrow as na


class SchemaWrapper:
    def __init__(self, schema):
        self.schema = schema

    def __arrow_c_schema__(self):
        return self.schema.__arrow_c_schema__()


class ArrayWrapper:
    def __init__(self, array):
        self.array = array

    def __arrow_c_array__(self, requested_schema=None):
        return self.array.__arrow_c_array__(requested_schema=requested_schema)


class StreamWrapper:
    def __init__(self, stream):
        self.stream = stream

    def __arrow_c_stream__(self, requested_schema=None):
        return self.stream.__arrow_c_stream__(requested_schema=requested_schema)


def test_schema():
    pa_schema = pa.schema([pa.field("some_name", pa.int32())])

    for schema_obj in [pa_schema, SchemaWrapper(pa_schema)]:
        schema = na.schema(schema_obj)
        # some basic validation
        assert schema.is_valid()
        assert schema.format == "+s"
        assert schema._to_string(recursive=True) == "struct<some_name: int32>"

        # roundtrip
        pa_schema2 = pa.schema(schema)
        assert pa_schema2.equals(pa_schema)
        # schemas stay valid because it exports a deep copy
        del pa_schema2
        assert schema.is_valid()


def test_array():
    pa_arr = pa.array([1, 2, 3], pa.int32())

    for arr_obj in [pa_arr, ArrayWrapper(pa_arr)]:
        array = na.array(arr_obj)
        # some basic validation
        assert array.is_valid()
        assert array.length == 3
        assert array.schema._to_string(recursive=True) == "int32"

        # roundtrip
        pa_arr2 = pa.array(array)
        assert pa_arr2.equals(pa_arr)
        del pa_arr2
        assert array.is_valid()


def test_array_stream():
    pa_table = pa.table({"some_column": pa.array([1, 2, 3], pa.int32())})

    for stream_obj in [pa_table, StreamWrapper(pa_table)]:
        array_stream = na.array_stream(stream_obj)
        # some basic validation
        assert array_stream.is_valid()
        array = array_stream.get_next()
        assert array.length == 3
        assert (
            array_stream.get_schema()._to_string(recursive=True)
            == "struct<some_column: int32>"
        )

        # roundtrip
        array_stream = na.array_stream(stream_obj)
        pa_table2 = pa.table(array_stream)
        assert pa_table2.equals(pa_table)
        # exporting a stream marks the original object as released (it is moved)
        assert not array_stream.is_valid()
        # and thus exporting a second time doesn't work
        with pytest.raises(RuntimeError):
            pa.table(array_stream)


def test_export_invalid():
    schema = na.Schema.allocate()
    assert schema.is_valid() is False

    with pytest.raises(RuntimeError, match="schema is released"):
        pa.schema(schema)

    array = na.Array.allocate(na.Schema.allocate())
    assert array.is_valid() is False
    with pytest.raises(RuntimeError, match="Array is released"):
        pa.array(array)

    array_stream = na.ArrayStream.allocate()
    assert array_stream.is_valid() is False
    with pytest.raises(RuntimeError, match="array stream is released"):
        pa.table(array_stream)


def test_import_from_c_errors():
    # ensure proper error is raised in case of wrong object or wrong capsule
    pa_arr = pa.array([1, 2, 3], pa.int32())

    with pytest.raises(ValueError):
        na.Schema._import_from_c_capsule("wrong")

    with pytest.raises(ValueError):
        na.Schema._import_from_c_capsule(pa_arr.__arrow_c_array__())

    with pytest.raises(ValueError):
        na.Array._import_from_c_capsule("wrong", "wrong")

    with pytest.raises(ValueError):
        na.Array._import_from_c_capsule(
            pa_arr.__arrow_c_array__(), pa_arr.type.__arrow_c_schema__()
        )

    with pytest.raises(ValueError):
        na.ArrayStream._import_from_c_capsule("wrong")

    with pytest.raises(ValueError):
        na.ArrayStream._import_from_c_capsule(pa_arr.__arrow_c_array__())
