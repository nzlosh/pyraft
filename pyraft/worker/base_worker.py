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

from pyraft.common import *
from pyraft.worker.worker import RespProtocol, Worker


# worker for basic control (info, shutdown, add_node, del_node etc)
class BaseWorker(Worker):
    def __init__(self, addr):
        super().__init__(addr)
        self.init_base_handler()
        self.set_protocol(RespProtocol())

    # inherit & extend this interface
    def init_base_handler(self):
        self.handler["info"] = [self.do_info, "r", 0, 0]
        self.handler["shutdown"] = [self.do_shutdown, "e", 0, 0]
        self.handler["quit"] = [self.do_quit, "r", 0, 0]

        self.handler["add_node"] = [self.do_add_node, "we", 2, 2]
        self.handler["del_node"] = [self.do_del_node, "we", 1, 1]
        self.handler["checkpoint"] = [self.do_checkpoint, "r", 0, 0]
        self.handler["getdump"] = [self.do_getdump, "r", 0, 0]
        self.handler["getlog"] = [self.do_getlog, "r", 0, 2]

    def do_info(self, node, words):
        peers = {}
        for nid, p in node.get_peers().items():
            peers[nid] = {"state": p.state, "addr": p.addr, "term": p.term, "index": p.index}

        info = {
            "nid": node.nid,
            "state": node.state,
            "term": node.term,
            "index": node.index,
            "peers": peers,
            "last_checkpoint": node.last_checkpoint,
        }
        return str(info).replace("'", '"')

    def do_quit(self, node, words):
        return {"quit": True}

    def do_shutdown(self, node, words):
        node.shutdown()
        return True

    def do_add_node(self, node, words):
        node.add_node(words[1], words[2])
        return True

    def do_del_node(self, node, words):
        node.del_node(words[1])
        return True

    def do_checkpoint(self, node, words):
        name = None
        if len(words) > 1:
            name = words[1]

        node.checkpoint(name)
        return True

    def do_getdump(self, node, words):
        return node.get_snapshot()

    def do_getlog(self, node, words):
        start = 0
        end = -1

        if len(words) > 1:
            start = intcast(words[1])
            if start == None:
                raise ERROR_CAST

        if len(words) > 2:
            end = intcast(words[2])
            if end == None:
                raise ERROR_CAST

        result = node.log.get_range(start, end)
        return result.__repr__()
