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
        self.frame = tk.Frame(self, width=width, height=height)
        self.frame.pack()
        self.resizable(0,0)

        self.lb = tk.Listbox(self.frame, width=25, height=56)
        self.lb.insert(tk.END, self.user.nick_name)
        self.lb.place(x=0, y=0)

        self.protocol("WM_DELETE_WINDOW", self.quit)

    def send(self):
        val = self.sdTxt.get('1.0', tk.END)
        MsgWorker().send_msg(val.encode())
        self.rcTxt.tag_config("tag_me", foreground="green")
        self.rcTxt.insert(tk.INSERT, '我:%s'%val, ("tag_me"))

    def quit(self):
        MsgWorker().send_msg(msg_lib.build_logout_msg(self.user.name))
        self.destroy()
