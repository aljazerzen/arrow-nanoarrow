#!/usr/bin/env python

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

import os
import subprocess
import sys

from setuptools import Extension, setup

# Run bootstrap.py to run cmake generating a fresh bundle based on this
# checkout or copy from ../dist if the caller doesn't have cmake available.
# Note that bootstrap.py won't exist if building from sdist.
this_dir = os.path.dirname(__file__)
bootstrap_py = os.path.join(this_dir, "bootstrap.py")
if os.path.exists(bootstrap_py):
    subprocess.run([sys.executable, bootstrap_py])


# Set some extra flags for compiling with coverage support
if os.getenv("NANOARROW_COVERAGE") == "1":
    extra_compile_args = ["--coverage"]
    extra_link_args = ["--coverage"]
    extra_define_macros = [("CYTHON_TRACE", 1)]
elif os.getenv("NANOARROW_DEBUG_EXTENSION") == "1":
    extra_compile_args = ["-g", "-O0"]
    extra_link_args = []
    extra_define_macros = []
else:
    extra_compile_args = []
    extra_link_args = []
    extra_define_macros = []

setup(
    ext_modules=[
        Extension(
            name="nanoarrow._lib",
            include_dirs=["src/nanoarrow"],
            language="c",
            sources=[
                "src/nanoarrow/_lib.pyx",
                "src/nanoarrow/nanoarrow.c",
                "src/nanoarrow/nanoarrow_device.c",
            ],
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
            define_macros=extra_define_macros,
        )
    ]
)
