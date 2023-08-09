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

import logging
import os
import socket
import sys
import threading
import time

CONF_LOG_MAX = 100000
CONF_LOG_FILE_MAX = 10000

CONF_VOTING_TIME = 1.0
CONF_PING_TIMEOUT = 5  # re-elect leader after CONF_PING_TIMEOUT


def intcast(src):
    if isinstance(src, int):
        return src

    if src.isdigit() == False:
        return None

    return int(src)


ERROR_CAST = Exception("number format error")
ERROR_APPEND_ENTRY = Exception("append entry failed")
ERROR_TYPE = Exception("invalid data type")
ERROR_NOT_EXISTS = Exception("not exists")
ERROR_INVALID_PARAM = Exception("invalid parameter")


class RaftException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class Future(object):
    def __init__(self, cmd, worker_offset=0):
        self.worker_offset = worker_offset
        self.cmd = cmd
        self.value = None
        self.cond = threading.Condition()

    def get(self, timeout=None):
        if self.value != None:
            return self.value

        try:
            with self.cond:
                self.cond.wait(timeout)
        except RuntimeError:
            return None

        return self.value

    def set(self, value):
        with self.cond:
            self.value = value
            self.cond.notify()


def bytes_to_str(b):
    out = []
    for c in b:
        out.append("%02x" % c)

    return " ".join(out)


logger = logging.getLogger("pyraft")
