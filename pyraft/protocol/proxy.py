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

# basic proxy tool for protocol analysis

import argparse
import select
import socket
import threading


def dump_str(data):
    result = []
    result_ascii = []
    for i in data:
        result.append("%02x " % i)
        result_ascii.append("%c " % i)

    return "%s - %s" % ("".join(result), "".join(result_ascii))


def handle_client(server, c, addr):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        ip, port = server.split(":")
        s.connect((ip, int(port)))

        while True:
            rl, wl, el = select.select([c], [], [])
            for r in rl:
                data = r.recv(4096)
                if not data:
                    c.close()
                    return

                print("<< req[%d]: %s" % (len(data), dump_str(data)))
                s.sendall(data)

            rl, wl, el = select.select([s], [], [], 0.01)
            for r in rl:
                data = r.recv(4096)
                if not data:
                    c.close()
                    return

                print(">> resp[%d]: %s" % (len(data), dump_str(data)))
                c.sendall(data)


def do_proxy(server, listen):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip, port = listen.split(":")
    s.bind((ip, int(port)))
    s.listen(10)
    while True:
        conn, addr = s.accept()
        th = threading.Thread(target=handle_client, args=(server, conn, addr))
        th.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", dest="server", help="server side address", required=True)
    parser.add_argument("-a", dest="addr", help="listen address", required=True)

    args = parser.parse_args()

    do_proxy(args.server, args.addr)
