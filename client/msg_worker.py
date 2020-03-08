from socket import socket, AF_INET, SOCK_STREAM
import threading
from common import msg_lib
from common.user import User

class MsgWorker(object):
    _instance = None
    alive = True
    login_flag = False
    user_info = None

    do_exit = None
    do_update = None
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
        while self.alive:
            bytes = self.tcp_client_sock.recv(1024)
            msg_info = msg_lib.parse_msg(bytes)
            if msg_info:
                msg_id = msg_info['msg_id']
                if msg_id == msg_lib.ONLINE:
                    self.user_info = msg_info['data']
                    self.login_flag = True
                if msg_id == msg_lib.LOGOUT:
                    if self.do_exit:
                        self.do_exit()
                if msg_id == msg_lib.ALL_USER_INFOS:
                    if self.do_update:
                        self.do_update(msg_info['data'])

    def send_msg(self, bytes):
        self._instance.tcp_client_sock.send(bytes)