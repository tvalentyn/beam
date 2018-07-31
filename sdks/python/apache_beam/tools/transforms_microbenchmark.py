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
from __future__ import division
from __future__ import print_function

import heapq
import random

from builtins import range

from apache_beam.tools import utils
from apache_beam.transforms import window


def hashable_object_benchmark_factory(generate_fn):
    """Creates a benchmark that tests hash performance of hashable objects.

    Args:
      generate_fn: a callable that generates a hashable object.
    """
    class HashableObjectsBenchmark(object):

        def __init__(self, num_elements_per_benchmark):
            self._list = [generate_fn()
                          for _ in range(num_elements_per_benchmark)]

        def __call__(self):
            self._dict = {}
            for e in self._list:
                self._dict[e] = 0

            for e in self._list:
                if self._dict[e]:
                   pass

    HashableObjectsBenchmark.__name__ = "%s: dict" % (
        generate_fn.__name__)

    return HashableObjectsBenchmark


def sortable_object_benchmark_factory(generate_fn):
    """Creates a benchmark that tests performance of sortable objects.

    Args:
      generate_fn: a callable that generates a sortable object.
    """
    class SortableObjectsBenchmark(object):

        def __init__(self, num_elements_per_benchmark):
            self._list = [generate_fn()
                          for _ in range(num_elements_per_benchmark)]

        def __call__(self):
            sorted(self._list)
            return
            # self._heap = []
            # for e in self._list:
            #     heapq.heappush(self._heap, e)

            # for _ in range(len(self._list)):
            #     heapq.heappop(self._heap)

    SortableObjectsBenchmark.__name__ = "%s: sorting." % (
        generate_fn.__name__)

    return SortableObjectsBenchmark


def interval_window():
    return window.IntervalWindow(random.randint(1000000000, 1500000000), random.randint(1500000000, 2000000000))


def timestamped_value():
    return window.TimestampedValue(random.randint(0, 1000), random.randint(1500000000, 2000000000))


def bounded_window():
   return window.BoundedWindow(random.randint(1500000000, 2000000000))

class BenchmarkFromUnitTest:
    def __init__(self, size):
        pass
    __name__ = "From test"

    def __call__(self):
        pass


def div_keys(kv1_kv2):
    (x1, _),  (x2, _) = kv1_kv2
    # !!!
    if isinstance(x1, int) and isinstance(x2, int):
      return x2 // x1
    return x2 / x1


class BenchmarkDivision:
    def __init__(self, size):
        self.data = [(random.randint(1, 100), 0) for _ in range(0, size)]

    def __call__(self):
      pairs = sorted(zip(self.data[::2], self.data[1::2]), key=div_keys)


def run_windowed_value_benchmarks(num_runs, input_size, seed, verbose=True):
    random.seed(seed)

    benchmarks = [
        # BenchmarkFromUnitTest,
        # BenchmarkDivision,
        # hashable_object_benchmark_factory(coders_microbenchmark.wv_with_one_window),
        # hashable_object_benchmark_factory(coders_microbenchmark.wv_with_multiple_windows),
        hashable_object_benchmark_factory(interval_window),
        hashable_object_benchmark_factory(timestamped_value),
        sortable_object_benchmark_factory(interval_window),
        sortable_object_benchmark_factory(timestamped_value),
        sortable_object_benchmark_factory(bounded_window),
    ]

    suite = [utils.BenchmarkConfig(b, input_size, num_runs) for b in benchmarks]
    utils.run_benchmarks(suite, verbose=verbose)


if __name__ == "__main__":
    utils.check_compiled("apache_beam.utils.windowed_value")

    num_runs = 20
    input_size = 10000
    seed = 42 # Fix the seed for better consistency

    run_windowed_value_benchmarks(num_runs, input_size, seed)
