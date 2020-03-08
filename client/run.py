#!/usr/bin/python
# -*- coding: UTF-8 -*-
from client.login import Login

# main = tk.Tk()
# win_width,win_height = 620,400
# main.title(u'客户端')
# main.geometry('%sx%s'%(620,400))

if __name__ == '__main__':
    login = Login()
    login.title(u'登录')
    login.mainloop()