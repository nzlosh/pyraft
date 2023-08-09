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

from pyraft import raft


class TestRecover(unittest.TestCase):
    def test_recover(self):
        nodes = []

        n = test.make_test_node(1, nodes)  # 1 is leader
        n.start()
        nodes.append(n)
        assert test.check_state(nodes)
        assert test.set_test_value(nodes)
        assert test.check_test_value(nodes)

        n = test.make_test_node(2, nodes)
        n.start()
        nodes.append(n)
        assert test.check_state(nodes)
        assert test.check_test_value(nodes)
        assert test.set_test_value(nodes)
        assert test.check_test_value(nodes)

        n = test.make_test_node(3, nodes)
        n.start()
        nodes.append(n)
        assert test.check_state(nodes)
        assert test.check_test_value(nodes)
        assert test.set_test_value(nodes)
        assert test.check_test_value(nodes)

        n = nodes[0]
        nodes = nodes[1:]

        n.shutdown()
        n.join()

        assert test.check_state(nodes)  # should one of 2, 3 should be leader
        assert test.check_test_value(nodes)
        assert test.set_test_value(nodes)
        assert test.check_test_value(nodes)

        n = test.make_test_node(1, nodes)
        n.start()
        nodes.append(n)
        assert test.check_state(nodes)  # now 1 is joined as follower

        for n in nodes:
            n.shutdown()
            n.join()


if __name__ == "__main__":
    unittest.main()
