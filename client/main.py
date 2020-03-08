#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys

import tkinter as tk
import tkinter.messagebox as tkmsgbox
from common import msg_lib
from client.msg_worker import MsgWorker

# main = tk.Tk()
# win_width,win_height = 620,400
# main.title(u'客户端')
# main.geometry('%sx%s'%(620,400))
class Main(tk.Tk):
    def __init__(self, user, width=160, height=660):
        super().__init__()
        self.user = user
        print(self.user)
        print(dict(self.user))
        self.frame = tk.Frame(self, width=width, height=height)
        self.frame.pack()
        self.resizable(0,0)

        self.lb = tk.Listbox(self.frame, width=250, height=56)
        self.lb.insert(tk.END, self.user.nick_name)
        self.lb.place(x=0, y=0)

        self.lb.insert(tk.END, 'test')
        self.lb.place(x=0, y=0)

        self.protocol("WM_DELETE_WINDOW", self.quit)

        MsgWorker().do_update = self.do_update
        self.frame.after(100, self.query_all_users)

    def query_all_users(self):
        MsgWorker().send_msg(msg_lib.build_get_all_users_msg())

    def do_update(self, all_users):
        for user in all_users:
            print(user.nick_name)

    def send(self):
        val = self.sdTxt.get('1.0', tk.END)
        MsgWorker().send_msg(val.encode())
        self.rcTxt.tag_config("tag_me", foreground="green")
        self.rcTxt.insert(tk.INSERT, '我:%s'%val, ("tag_me"))

    def quit(self):
        MsgWorker().send_msg(msg_lib.build_logout_msg(self.user.name))
        self.destroy()
