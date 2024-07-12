#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QIcon


class FirstMainWin(QMainWindow):
    def __init__(self, parent=None):
        super(FirstMainWin, self).__init__(parent)

        # 主窗口标题
        self.setWindowTitle("第一个主窗口应用")

        # 窗口尺寸
        self.resize(500, 400)

        # 状态栏
        self.status = self.statusBar()

        self.status.showMessage("此消息只存在5s", 5000)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("../src/2.png"))
    main = FirstMainWin()
    main.show()

    sys.exit(app.exec_())
    pass
