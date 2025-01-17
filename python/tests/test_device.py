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

from nanoarrow import device


def test_cpu_device():
    cpu = device.Device.cpu()
    assert cpu.device_type == 1
    assert cpu.device_id == 0
    assert "device_type: 1" in repr(cpu)

    cpu = device.Device.resolve(1, 0)
    assert cpu.device_type == 1

    pa_array = pa.array([1, 2, 3])

    darray = device.device_array(pa_array)
    assert darray.device_type == 1
    assert darray.device_id == 0
    assert darray.array.length == 3
    assert "device_type: 1" in repr(darray)

    assert device.device_array(darray) is darray
