import sys
from client.login import Login
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    login = Login()

    sys.exit(app.exec_())