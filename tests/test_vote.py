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


class TestVote(unittest.TestCase):
    def normal_election(self, n_node_list, repeat):
        i = 0
        while i < repeat:
            for n_node in n_node_list:
                i += 1

                nodes, ensemble = test.make_test_node_set(n_node)

                for n in nodes:
                    n.start()

                ret = test.check_state(nodes, timeout=10 + 2 * len(nodes))

                for n in nodes:
                    n.shutdown()
                    n.join()

                if ret == False:
                    return False

        return True

    def test_election(self):
        assert self.normal_election(
            [3, 3, 3, 3, 3, 4, 5, 5, 5, 5, 5, 6, 7, 7, 7, 7, 7, 8, 9, 10, 11, 12, 13], 100
        )


if __name__ == "__main__":
    unittest.main()
