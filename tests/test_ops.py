# MIT License

# Copyright (c) 2023 Carlos (nzlosh@yahoo.com)
# Copyright (c) 2019 Martin Isaksson

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import unittest

import os, sys, time
import threading
import test_util as test
import redis, random

from pyraft import raft


class TestOPS(unittest.TestCase):
    def test_ops(self):
        nodes = []

        n1 = test.make_test_node(1, nodes)  # 1 is leader
        n1.start()

        count = 1000
        time.sleep(1)

        r = redis.StrictRedis(host=n1.ip, port=n1.port)

        start = time.time()
        for i in range(count):
            v = "value_%07d" % random.randrange(0, 1000000)
            r.set("key_%d" % i, v)
        end = time.time()
        print("ops: %d" % (count / (end - start)))

        start = time.time()
        for i in range(count):
            v = r.get("get_%d" % i)
        end = time.time()
        print("ops: %d" % (count / (end - start)))

        n2 = test.make_test_node(2, nodes)
        n2.start()

        start = time.time()
        for i in range(count):
            v = "value_%07d" % random.randrange(0, 1000000)
            r.set("key_%d" % i, v)
        end = time.time()
        print("ops: %d" % (count / (end - start)))

        start = time.time()
        for i in range(count):
            v = r.get("get_%d" % i)
        end = time.time()
        print("ops: %d" % (count / (end - start)))

        n3 = test.make_test_node(3, nodes)
        n3.start()

        start = time.time()
        for i in range(count):
            v = "value_%07d" % random.randrange(0, 1000000)
            r.set("key_%d" % i, v)
        end = time.time()
        print("ops: %d" % (count / (end - start)))

        start = time.time()
        for i in range(count):
            v = r.get("get_%d" % i)
        end = time.time()
        print("ops: %d" % (count / (end - start)))

        n1.shutdown()
        n1.join()
        n2.shutdown()
        n2.join()
        n3.shutdown()
        n3.join()


if __name__ == "__main__":
    unittest.main()
