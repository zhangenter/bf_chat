import logging
import sys
import socketserver
import socket
import threading
from common import msg_lib,user

logging.basicConfig(format="%(asctime)s %(thread)d %(threadName)s %(message)s",stream=sys.stdout,level=logging.INFO)
log = logging.getLogger()

user_arr = []
user_lock = threading.Lock()
def load_user_info(name, pwd):
    u = user.User()
    u.name = name
    u.nick_name = name
    return u

def add_user(new_user):
    with user_lock:
        flag = False
        for u in user_arr:
            if u.name == new_user.name:
                flag = True
        if not flag:
            user_arr.append(new_user)

class Handler(socketserver.StreamRequestHandler):
    lock = threading.Lock()
    clients = {}

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
        while not self.event.is_set():
            try:
                data = rfile.read1(1024)
            except Exception as e:
                log.error(e)
                data = b""
            log.info(data)
            if data == b"by" or data == b"":
                break
            msg_info = msg_lib.parse_msg(data)
            print(msg_info)
            if msg_info:
                msg_id = msg_info['msg_id']
                if msg_id == msg_lib.LOGIN:
                    u = load_user_info(msg_info['data']['name'], msg_info['data']['pwd'])
                    add_user(u)
                    with self.lock:
                        self.clients[self.client_address].send(msg_lib.build_online_msg(u))
                if msg_id == msg_lib.LOGOUT:
                    with self.lock:
                        self.send_all(data)
                if msg_id == msg_lib.GET_USER_INFOS:
                    with self.lock:
                        self.clients[self.client_address].send(msg_lib.build_all_users_msg(user_arr))

    def finish(self):
        super().finish()
        self.event.set()
        with self.lock:
            if self.client_address in self.clients:
                self.clients.pop(self.client_address)
        self.request.close()
        log.info("{}退出了".format(self.client_address))

if __name__ == "__main__":
    server = socketserver.ThreadingTCPServer(("127.0.0.1", msg_lib.PORT),Handler)
    server.daemon_threads = True  #设置所有创建的线程都为Daemo线程
    threading.Thread(target=server.serve_forever,name="server",daemon=True).start()
    while True:
        cmd = input(">>>")
        if cmd.strip() == "quit":
            server.shutdown() #告诉serve_forever循环停止。
            server.server_close()
            break
        logging.info(threading.enumerate())

