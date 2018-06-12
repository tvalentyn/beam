# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""A microbenchmark for measuring performance of windowed value hashability.

This creates a dictionary keyed with windowed values, and measures performance
of writes and reads operation.

Run as
  python -m apache_beam.tools.windowed_value_microbenchmark
"""

from __future__ import absolute_import
from __future__ import print_function

import collections
import random

from apache_beam.tools import coders_microbenchmark
from apache_beam.tools import utils


class WindowedValueAddToDictBenchmark:
  def __init__(self, size):
    self.size_ = size
    self.wv_dict_ = {}
    self.sample_wv_list_ = []

    # Pre-generate windowed values so that we don't include generation in
    # benchmarking time.

    for _ in range(0, self.size_):
      self.sample_wv_list_.append(coders_microbenchmark.generate_windowed_int_value())

  def __call__(self):
    for wv in self.sample_wv_list_:
      self.wv_dict_[wv] = 0


class WindowedValueReadFromDictBenchmark:
  def __init__(self, size):
    self.size_ = size
    self.wv_dict_ = {}
    self.wv_list_to_read_ = []

    for _ in range(0, self.size_):
      self.wv_list_to_read_.append(coders_microbenchmark.generate_windowed_int_value())

    for _ in range(0, self.size_):
      self.wv_dict_[coders_microbenchmark.generate_windowed_int_value()] = 0

    self.cnt_ = 0

  def __call__(self):
    for wv in self.wv_list_to_read_:
      if wv in self.wv_dict_:
        pass


def run_windowed_value_benchmarks(num_runs, input_size, seed, verbose=True):
  random.seed(seed)

  benchmarks = [
    WindowedValueAddToDictBenchmark,
    WindowedValueReadFromDictBenchmark
  ]

  BenchmarkConfig = collections.namedtuple(
      "BenchmarkConfig", ["benchmark", "size", "num_runs"])

  suite = [BenchmarkConfig(b, input_size, num_runs) for b in benchmarks]
  utils.run_benchmarks(suite, verbose=verbose)


if __name__ == "__main__":
  utils.check_compiled("apache_beam.utils.windowed_value")

  num_runs = 100
  input_size = 1000
  seed = 42 # Fix the seed for better consistency

  print("Number of runs:", num_runs)
  print("Input size:", input_size)
  print("Random seed:", seed)

  run_windowed_value_benchmarks(num_runs, input_size, seed)
