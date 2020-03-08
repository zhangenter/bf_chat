#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys

from common import msg_lib
from client.msg_worker import MsgWorker
from PyQt5.QtWidgets import QDesktopWidget, QApplication, QWidget, QMessageBox, QLabel, QPushButton, QLineEdit, QListView, QAbstractItemView
from PyQt5.QtGui import QIcon,QPixmap,QStandardItem,QStandardItemModel
from PyQt5.QtCore import QSize
from PyQt5 import QtCore
from client.chat import Chat

class Main(QWidget):
    def __init__(self, user, width=160, height=660):
        super().__init__()
        self.user = user

        self.lv = QListView(self)
        self.lv.setViewMode(QListView.ListMode)
        self.lv.setIconSize(QSize(30,30))
        # self.lb.setGridSize(QSize(30,30))
        self.lv.resize(width,height)
        self.lv.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.lv.setResizeMode(QListView.Adjust)
        self.lv_model = QStandardItemModel()
        self.lv.setModel(self.lv_model)
        # self.lb_model.appendRow(QStandardItem(QIcon("./client/image/man.png"), "普通员工A"))
        # self.lb_model.appendRow(QStandardItem(QIcon("./client/image/woman.png"), "普通员工B"))
        self.lv.doubleClicked.connect(self.lv_clicked)

        MsgWorker().do_update = self.do_update
        self.query_all_users()

    def query_all_users(self):
        MsgWorker().send_msg(msg_lib.build_get_all_users_msg())

    def do_update(self, all_users):
        self.all_users = all_users
        for user in self.all_users:
            self.lv_model.appendRow(QStandardItem(QIcon("./client/image/man.png"), user.nick_name))

            # self.lb.insert(tk.END, user.nick_name)

    def lv_clicked(self, model_index):
        user = self.all_users[model_index.row()]
        self.chat_to({'mode': 'user', 'data': user})

    def send(self):
        pass
        # val = self.sdTxt.get('1.0', tk.END)
        # MsgWorker().send_msg(val.encode())
        # self.rcTxt.tag_config("tag_me", foreground="green")
        # self.rcTxt.insert(tk.INSERT, '我:%s'%val, ("tag_me"))

    chat_form = None
    def chat_to(self, user):
        if not self.chat_form:
            self.chat_form = Chat()
            self.chat_form.after_close = self.do_after_close
            self.chat_form.show()

        self.chat_form.chat_to(user)
        self.chat_form.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.chat_form.raise_()
        self.chat_form.activateWindow()

    def do_after_close(self):
        self.chat_form = None

    def closeEvent(self, event):
        if self.chat_form:
            self.chat_form.close()
        MsgWorker().send_msg(msg_lib.build_logout_msg(self.user.name))