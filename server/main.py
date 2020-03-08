import logging
import sys
from struct import pack,unpack
import socketserver
import socket
import threading
from common import msg_lib,user
from server.msg_db import add_user, get_all_users, load_user_info

logging.basicConfig(format="%(asctime)s %(thread)d %(threadName)s %(message)s",stream=sys.stdout,level=logging.INFO)
log = logging.getLogger()


class Handler(socketserver.StreamRequestHandler):
    lock = threading.Lock()
    clients = {}
    name2client = {}

    def setup(self):
        super().setup()
        self.event = threading.Event()
        with self.lock:
            self.clients[self.client_address] = self.request
        log.info("新加入了一个连接{}".format(self.client_address))

    def send_all(self, data):
        expc = []
        for c, sk in self.clients.items():
            try:
                sk.send(data)
            except:
                expc.append(c)
        for c in expc:
            self.clients.pop(c)

    def handle(self):
        super().handle()
        import io
        rfile = self.rfile
        full_bytes = b''
        while not self.event.is_set():
            try:
                read_bytes = rfile.read1(1024)
            except Exception as e:
                log.error(e)
                break

            full_bytes += read_bytes
            if len(full_bytes) < 6:
                full_bytes = b''
                continue

            if not msg_lib.is_msg_valid(full_bytes):
                continue

            msg_info = msg_lib.parse_msg(full_bytes)
            if msg_info:
                msg_id = msg_info['msg_id']
                if msg_id == msg_lib.LOGIN:
                    u = load_user_info(msg_info['data']['name'], msg_info['data']['pwd'])
                    self.name2client[u.name] = self.client_address
                    with self.lock:
                        if u:
                            self.clients[self.client_address].send(msg_lib.build_online_msg(u))
                        else:
                            self.clients[self.client_address].send(msg_lib.build_login_fail_msg())
                if msg_id == msg_lib.LOGOUT:
                    with self.lock:
                        self.send_all(full_bytes)
                if msg_id == msg_lib.GET_USER_INFOS:
                    user_arr = get_all_users()
                    with self.lock:
                        self.clients[self.client_address].send(msg_lib.build_all_users_msg(user_arr))
                if msg_id == msg_lib.CHAT_MSG:
                    ufrom = msg_info['data']['from']
                    uto = msg_info['data']['to']
                    val = msg_info['data']['val']
                    to_address = self.name2client[uto]
                    self.clients[to_address].send(full_bytes)

            full_bytes = b''

    def finish(self):
        super().finish()
        self.event.set()
        with self.lock:
            if self.client_address in self.clients:
                self.clients.pop(self.client_address)
        self.request.close()
        log.info("{}退出了".format(self.client_address))

def run():
    server = socketserver.ThreadingTCPServer(("127.0.0.1", msg_lib.PORT), Handler)
    server.daemon_threads = True  # 设置所有创建的线程都为Daemo线程
    threading.Thread(target=server.serve_forever, name="server", daemon=True).start()
    while True:
        cmd = input(">>>")
        if cmd.strip() == "quit":
            server.shutdown()  # 告诉serve_forever循环停止。
            server.server_close()
            break
        logging.info(threading.enumerate())

if __name__ == "__main__":
    run()


