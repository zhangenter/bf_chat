#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os, sys, time, pickle

from PyQt5.QtWidgets import QCheckBox, QDesktopWidget, QApplication, QWidget, QMessageBox, QLabel, QPushButton, QLineEdit
from client.main import Main
from client.msg_worker import MsgWorker
from common.user import User
from common import msg_lib

pickle_file = 'data.pkl'
class Login(QWidget):
    def __init__(self):
        super().__init__()

        auto_login = False
        try:
            with open(pickle_file, 'rb') as rb:
                data = pickle.load(rb)
            auto_login = data['auto_login']
            MsgWorker().send_msg(msg_lib.build_login_msg(data['name'], data['pwd']))
            self.do_after_login(from_auto=True)
        except Exception as ex:
            print(ex)

        if not auto_login:
            self.init_ui()

    def init_ui(self):
        QLabel('用户名:', self).move(120,64)
        self.et_name = QLineEdit(self)
        self.et_name.move(180,60)
        QLabel('密  码:', self).move(120,104)
        self.et_pwd = QLineEdit(self)
        self.et_pwd.move(180,100)
        self.et_pwd.setEchoMode(QLineEdit.Password)

        self.cb = QCheckBox(self)
        self.cb.setText('自动登录')
        self.cb.move(180,140)

        btn = QPushButton("登录", self)
        btn.resize(80,30)
        btn.move(150,200)
        btn.clicked[bool].connect(self.click_login)
        btn = QPushButton("取消", self)
        btn.resize(80,30)
        btn.move(260,200)
        btn.clicked[bool].connect(self.click_cancel)

        self.resize(480, 280)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.setWindowTitle('登录')
        self.show()

    def click_login(self):
        name = self.et_name.text()
        if len(name) == 0:
            QMessageBox.information(self, '登录错误', "请输入用户名")
            # tkmsgbox.showerror('登录错误', '请输入用户名')
            return

        pwd = self.et_pwd.text()
        if len(pwd) == 0:
            QMessageBox.information(self, '登录错误', "请输入密码")
            # tkmsgbox.showerror('登录错误', '请输入密码')
            return

        MsgWorker().do_exit = self.click_cancel

        import hashlib
        md5 = hashlib.md5()
        md5.update(pwd.encode())
        md5_pwd = md5.hexdigest()

        self.login_name = name
        self.login_pwd = md5_pwd
        MsgWorker().send_msg(msg_lib.build_login_msg(name, md5_pwd))
        self.do_after_login()

    def do_after_login(self, from_auto=False):
        while MsgWorker().login_flag == 0:
            time.sleep(0.1)

        if MsgWorker().login_flag == 2:
            QMessageBox.information(self, '登录错误', "用户名或密码无效")
            # tkmsgbox.showerror('登录错误', '用户名或密码无效')
            return

        if not from_auto:
            with open(pickle_file, 'wb') as fw:
                if self.cb.isChecked():
                    pickle.dump({'auto_login': True, 'name':self.login_name, 'pwd':self.login_pwd}, fw)
                else:
                    pickle.dump({'auto_login': False}, fw)

        desktop = QApplication.desktop()
        frame_height = desktop.height() - 70
        frame_width = 160
        frame_left = desktop.width() - frame_width
        # self.withdraw()
        self.setVisible(False)

        main = Main(user=MsgWorker().user_info, width=frame_width, height=frame_height)
        main.setGeometry(frame_left, 30, frame_width, frame_height )
        main.show()

    def click_cancel(self):
        self.destroy()