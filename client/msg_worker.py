from socket import socket, AF_INET, SOCK_STREAM
import threading
from common import msg_lib
from common.user import User

class MsgWorker(object):
    _instance = None
    alive = True
    login_flag = 0
    user_info = None

    do_exit = None
    do_update = None
    do_recv_msg = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            ADDR = ('127.0.0.1', msg_lib.PORT)
            cls._instance.tcp_client_sock = socket(AF_INET, SOCK_STREAM)
            cls._instance.tcp_client_sock.connect(ADDR)
            cls._instance.recv_thread = threading.Thread(target=cls._instance.do_recv)
            cls._instance.recv_thread.daemon = True
            cls._instance.recv_thread.start()

        return cls._instance

    def do_recv(self):
        full_bytes = b''
        while self.alive:
            read_bytes = self.tcp_client_sock.recv(1024)
            full_bytes += read_bytes
            if len(full_bytes) < 6:
                full_bytes = b''
                continue
            if not msg_lib.is_msg_valid(full_bytes):
                continue

            msg_info = msg_lib.parse_msg(full_bytes)
            if msg_info:
                msg_id = msg_info['msg_id']
                if msg_id == msg_lib.LOGIN_FAIL:
                    self.login_flag = 2
                elif msg_id == msg_lib.ONLINE:
                    self.user_info = msg_info['data']
                    self.login_flag = 1
                elif msg_id == msg_lib.LOGOUT:
                    if self.do_exit:
                        self.do_exit()
                elif msg_id == msg_lib.ALL_USER_INFOS:
                    if self.do_update:
                        self.do_update(msg_info['data'])
                elif msg_id == msg_lib.CHAT_MSG:
                    if self.do_recv_msg:
                        self.do_recv_msg(msg_info['data'])
            full_bytes = b''

    def send_msg(self, bytes):
        self._instance.tcp_client_sock.send(bytes)