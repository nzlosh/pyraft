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

import threading

from pyraft.common import *
from pyraft.protocol import zk


class ZkEphermeralManager:
    def __init__(self, node):
        self.owner_path_node_map = {}  # TODO: move to node.data (for restart handling)
        self.lock = threading.Lock()
        # self.session_timeout = 60.0
        self.session_timeout = 10.0
        self.node = node

    def start(self):
        self.quit_flag = False
        self.th_worker = threading.Thread(target=self.ephemeral_check)
        self.th_worker.start()

    def join(self):
        self.quit_flag = True
        self.th_worker.join()

    def ephemeral_check(self):
        while True:
            expire_list = []
            with self.lock:
                # change ownerping to hgetall
                zk_session = self.node.data.get("zk_session")
                if zk_session is None:
                    time.sleep(1.0)
                    continue

                owner_list = zk_session.keys()
                for owner in owner_list:
                    ts = zk_session.get(owner)
                    if ts is None:  # can be removed while traversing
                        expire_list.append(owner)
                        continue

                    ts = int(ts)
                    # print('## check %s %d %d' % (owner, ts, time.time() - ts))
                    if time.time() - ts > self.session_timeout:  # TODO: by timeout
                        expire_list.append(owner)

            for owner in expire_list:
                self.expire(owner)
                self.node.request("hdel", "zk_session", str(owner))

            if self.quit_flag:
                return

            time.sleep(1.0)

    def regist(self, path, node):
        with self.lock:
            session = node.stat["ephemeralOwner"]
            self.node.request_async("rpush", "zk_sess_nodes_%s" % session, path)

    def unregist(self, path):
        with self.lock:
            node = self.worker._cd_path(self.node, path)
            session = node.stat["ephemeralOwner"]
            self.node.request_async("lrem", "zk_sess_nodes_%s" % session, path)

    def expire(self, session):
        with self.lock:
            logger.info("session %s is deleted" % session)
            print("## expire %s" % session)

            nodes = self.node.data.get("zk_sess_nodes_%s" % session)
            if nodes is None:
                return

            for node in nodes:
                logger.info("ephemeral node %s is deleted" % node)
                self.node.request("trm", "ZK%s" % node)
            self.node.request("del", "zk_sess_nodes_%s" % session)

            io = zk.get_session_io(session)
            if io is not None:  # can be none if disconnected
                io.close()
