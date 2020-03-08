#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys, time

import tkinter as tk
import tkinter.messagebox as tkmsgbox
from client.main import Main
from client.msg_worker import MsgWorker
from common.user import User
from common import msg_lib

class Login(tk.Tk):
    def __init__(self):
        super().__init__()

        # self.geometry('%sx%s' % (620, 400))
        self.frame = tk.Frame(self, width=620, height=400)
        self.frame.pack()
        self.create_controls()

    def create_controls(self):
        tk.Label(self.frame, text='用户名:', font=('Arial', 10), width=20, height=1).place(x=120,y=104)
        self.name_val = tk.StringVar(value='test')
        self.et_name = tk.Entry(self.frame, text='', bg='white', font=('Arial', 18), width=13, textvariable=self.name_val)
        self.et_name.place(x=280,y=100)
        tk.Label(self.frame, text='密码:', font=('Arial', 10), width=20, height=1).place(x=120,y=164)
        self.pwd_val = tk.StringVar(value='')
        self.et_pwd = tk.Entry(self.frame, text='', bg='white', font=('Arial', 18), width=13, textvariable=self.pwd_val)
        self.et_pwd['show'] = '*'
        self.et_pwd.place(x=280,y=160)

        btn = tk.Button(self.frame, text ="登录", font=('Arial', 10), width=10, height=1, command = self.click_login)
        btn.place(x=200,y=230)
        btn = tk.Button(self.frame, text ="取消", font=('Arial', 10), width=10, height=1, command = self.click_cancel)
        btn.place(x=320,y=230)

    def click_login(self):
        if len(self.name_val.get()) == 0:
            tkmsgbox.showerror('登录错误', '请输入用户名')
            return

        if len(self.pwd_val.get()) == 0:
            tkmsgbox.showerror('登录错误', '请输入密码')
            return

        MsgWorker().do_exit = self.click_cancel

        import hashlib
        md5 = hashlib.md5()
        md5.update(self.pwd_val.get().encode())
        md5_pwd = md5.hexdigest()
        MsgWorker().send_msg(msg_lib.build_login_msg(self.name_val.get(), md5_pwd))
        self.do_after_login()

    def do_after_login(self):
        while MsgWorker().login_flag == 0:
            time.sleep(0.1)

        if MsgWorker().login_flag == 2:
            tkmsgbox.showerror('登录错误', '用户名或密码无效')
            return

        frame_height = self.winfo_screenheight() - 70
        frame_width = 160
        frame_left = self.winfo_screenwidth() - frame_width
        self.withdraw()

        main = Main(user=MsgWorker().user_info, width=frame_width, height=frame_height)
        main.geometry("%sx%s+%s+0" % (frame_width, frame_height, frame_left))
        main.mainloop()

        # MsgWorker().alive = False
        # import sys
        # sys.exit(0)

    def click_cancel(self):
        self.destroy()