#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys

import tkinter as tk
import tkinter.messagebox as tkmsgbox
from socket import socket, AF_INET, SOCK_STREAM
import threading
from common import msg_lib

class Chart(tk.Frame):
    def __init__(self, master=None, width=win_width, height=win_height):
        super().__init__(master, width=width, height=height)
        self.master = master
        self.pack()
        ADDR = ('127.0.0.1', 3999)
        self.tcp_client_sock = socket(AF_INET, SOCK_STREAM)
        self.tcp_client_sock.connect(ADDR)
        self.recv_thread = threading.Thread(target=self.do_recv)
        self.recv_thread.daemon = True
        self.recv_thread.start()

        self.tcp_client_sock.send(msg_lib.build_login_msg(lg.name))

        self.rcVal = tk.StringVar(master=self)
        self.rcTxt = tk.Text(self.master, width=56, height=20)
        self.rcTxt.place(x=10, y=10)

        self.sdTxt = tk.Text(self.master, width=56, height=10)
        self.sdTxt.place(x=10, y=330)
        btn = tk.Button(self.master, text="发送", font=('Arial', 10), width=10, height=1, command=self.send)
        btn.place(x=318, y=475)

        self.lb = tk.Listbox(self.master, width=24, height=25)
        self.lb.insert(tk.END, lg.name)
        self.lb.place(x=420, y=10)

    def send(self):
        val = self.sdTxt.get('1.0', tk.END)
        self.tcp_client_sock.send(val.encode())
        self.rcTxt.tag_config("tag_me", foreground="green")
        self.rcTxt.insert(tk.INSERT, '我:%s'%val, ("tag_me"))

    def do_recv(self):
        while True:
            bytes = self.tcp_client_sock.recv(1024)
            msg_info = msg_lib.parse_msg(bytes)
            if msg_info:
                msg_id = msg_info['msg_id']
                if msg_id == msg_lib.LOGIN:
                    self.lb.insert(tk.END, msg_info['name'])
                if msg_id == msg_lib.LOGOUT:
                    break
        import sys
        sys.exit()

    def quit(self):
        self.tcp_client_sock.send(msg_lib.build_logout_msg(lg.name))
        import time
        time.sleep(5)
        self.tcp_client_sock.close()
