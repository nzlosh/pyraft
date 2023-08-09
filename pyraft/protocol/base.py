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

import select
import socket

from pyraft.common import *


class base_io:
    def __init__(self, sock):
        self.sock = sock
        self.buff = b""
        self.timeout = -1

        self.last_decodable = False
        self.last_buff_len = 0

    def connected(self):
        return self.sock != None

    def close(self):
        if self.sock != None:
            self.sock.close()

        self.sock = None

    def raw_write(self, msg):
        if self.sock == None:
            return None

        msg = self.raw_encode(msg)

        try:
            if isinstance(msg, str):
                msg = msg.encode()
            ret = self.sock.send(msg)
        except socket.error:
            self.close()
            return None

        if ret == 0:
            self.close()
            return None

        return ret

    def write(self, msg):
        if self.sock == None:
            return None

        try:
            msg = self.encode(msg)
            if isinstance(msg, str):
                msg = msg.encode()

            ret = self.sock.send(msg)
            if ret == 0:
                self.close()
                return None
            return ret

        except socket.error:
            self.close()
            return None

    def read(self, timeout=None):
        if self.sock == None:
            return None

        while True:
            readable = False
            if timeout != None:  # avoid useless decodable check
                if self.last_decodable == False and self.last_buff_len == len(self.buff):
                    reads, writes, excepts = select.select([self.sock], [], [], timeout)
                    if len(reads) == 0:
                        return b""
                    else:
                        readable = True

            self.last_decodable = True
            if not self.decodable(self.buff):
                if timeout != None and not readable:  # skip double wait
                    reads, writes, excepts = select.select([self.sock], [], [], timeout)
                    if len(reads) == 0:
                        self.last_decodable = False
                        self.last_buff_len = len(self.buff)
                        return b""

                try:
                    tmp = self.sock.recv(4096)
                except socket.error:
                    self.close()
                    return None
                except Exception:
                    self.close()
                    return None

                if tmp == b"":
                    self.close()
                    return None

                self.buff += tmp

            result, self.buff = self.decode(self.buff)
            if result == None:
                if timeout != None:
                    reads, writes, excepts = select.select([self.sock], [], [], timeout)
                    if len(reads) == 0:
                        self.last_decodable = False
                        self.last_buff_len = len(self.buff)
                        return b""

                try:
                    tmp = self.sock.recv(4096)
                except socket.error:
                    self.close()
                    return None

                if tmp == b"":
                    self.close()
                    return None

                self.buff += tmp
                continue

            return result

    def read_all(self, timeout=None):
        result = []

        while True:
            ret = self.read(timeout)
            if ret == None:
                return None

            if ret == b"":
                break

            result.append(ret)
            item, remain = self.decode(self.buff)
            if item == None:
                break

        return result

    # inherit below 4 interface
    def raw_encode(self, msg):
        pass

    def encode(self, msg):
        pass

    def decode(self, msg):
        pass

    def decodable(self, buff):
        pass
