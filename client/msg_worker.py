from socket import socket, AF_INET, SOCK_STREAM
import threading
from common import msg_lib
from common.user import User

class MsgWorker(object):
    _instance = None
    after_login = None
    do_exit = None
    alive = True
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            ADDR = ('127.0.0.1', 3999)
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
                    print(msg_info)
                    if self.after_login:
                        t = threading.Thread(target=self.after_login, args=(User.parse_from_dic(msg_info),))
                        t.daemon = True
                        t.start()
                if msg_id == msg_lib.LOGOUT:
                    if self.do_exit:
                        self.do_exit()

    def send_msg(self, bytes):
        self._instance.tcp_client_sock.send(bytes)