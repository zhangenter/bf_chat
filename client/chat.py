#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys

from PyQt5.QtWidgets import QFrame,QDesktopWidget, QApplication, QWidget, QMessageBox, QLabel, QPushButton, QLineEdit, QListView, QAbstractItemView, QTextBrowser, QTextEdit
from PyQt5.QtGui import QIcon,QPixmap,QStandardItem,QStandardItemModel
from PyQt5.QtCore import QSize,QModelIndex,pyqtSignal
import threading
from common import msg_lib
from client.msg_worker import MsgWorker

class Chat(QWidget):
    msg_signal = pyqtSignal(dict)
    after_close = None
    chats = []
    cur_chat = None
    def __init__(self, parent=None):
        super().__init__(parent)

        self.msg_signal.connect(self.fill_msg)
        MsgWorker().do_recv_msg = self.do_recv_msg
        self.setWindowTitle('')
        self.op_bar = QFrame(self)
        self.op_bar.setStyleSheet('background-color:rgb(255, 255, 255);')
        self.send_bar = QFrame(self)
        self.send_bar.setStyleSheet('background-color:rgb(255, 255, 255);')
        self.rcTxt = QTextBrowser(self)
        self.rcTxt.setStyleSheet('background-color:rgb(255, 255, 255);')
        self.sdTxt = QTextEdit(self)
        self.sdTxt.setStyleSheet('background-color:rgb(255, 255, 255);')
        self.btn = QPushButton("发送", self.send_bar)
        self.btn.clicked.connect(self.send)
        self.lv = QListView(self)
        self.lv.setViewMode(QListView.ListMode)
        self.lv.setIconSize(QSize(30, 30))
        self.lv.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.lv.setResizeMode(QListView.Adjust)
        self.lv_model = QStandardItemModel()
        self.lv.setModel(self.lv_model)
        self.lv.clicked.connect(self.lv_clicked)
        self.lv.move(0,0)

        w,h = 600,400
        self.resize(800,600)

    def resizeEvent(self, evt):
        self.after_resize(evt.size().width(), evt.size().height())

    def after_resize(self, w, h):
        lv_width = 200
        sdTxt_height = 120
        bar_height = 30
        self.op_bar.move(200, h - sdTxt_height - bar_height*2)
        self.op_bar.resize(w - lv_width, bar_height)
        self.send_bar.move(200, h - bar_height)
        self.send_bar.resize(w - lv_width, bar_height)

        self.lv.resize(lv_width, h)
        self.rcTxt.move(lv_width, 0)
        self.rcTxt.resize(w - lv_width, h - sdTxt_height  - bar_height * 2)
        self.sdTxt.move(lv_width, h - sdTxt_height - bar_height)
        self.sdTxt.resize(w - lv_width, sdTxt_height)

    def lv_clicked(self, model_index):
        cur_chat = self.chats[model_index.row()]
        if cur_chat['mode'] == 'user':
            self.setWindowTitle(cur_chat['data'].nick_name)

    def refresh_cur_chat(self):
        if self.cur_chat['mode'] == 'user':
            self.setWindowTitle(self.cur_chat['data'].nick_name)

    def get_in_chat_index(self, chat):
        if chat['mode'] == 'user':
            name = chat['data'].name
            match = lambda x: x['mode'] == 'user' and x['data'].name == name
        for i in range(len(self.chats)):
            if match(self.chats[i]):
                return i

        return -1

    def chat_to(self, chat):
        i = self.get_in_chat_index(chat)
        if i == -1:
            if chat['mode'] == 'user':
                self.lv_model.appendRow(QStandardItem(QIcon("./client/image/man.png"), chat['data'].nick_name))
            self.chats.append(chat)
            self.cur_chat = chat
            i = len(self.chats) - 1
        else:
            self.cur_chat = self.chats[i]
        self.refresh_cur_chat()
        self.lv.setCurrentIndex(self.lv_model.index(i,0))

    def fill_msg(self, data):
        ufrom = data['from']
        uto = data['to']
        val = data['val']
        ufrom_nickname = ufrom
        try:
            self.rcTxt.setPlainText(self.rcTxt.toPlainText() + '%s:%s\n' % (ufrom_nickname, val))
        except Exception as ex:
            print(ex)

    def do_recv_msg(self, data):
        self.msg_signal.emit(data)

    def send(self):
        # val = self.sdTxt.toHtml()
        val = self.sdTxt.toPlainText()
        if self.cur_chat['mode'] == 'user':
            MsgWorker().send_msg(msg_lib.build_chat_msg(MsgWorker().user_info.name, self.cur_chat['data'].name, val))
        # self.rcTxt.setHtml(self.rcTxt.toHtml()+'\n我:%s'%val)
        self.rcTxt.setPlainText(self.rcTxt.toPlainText()+'我:%s\n'%val)
        self.sdTxt.setPlainText('')

    def closeEvent(self, event):
        self.chats.clear()
        if self.after_close:
            self.after_close()