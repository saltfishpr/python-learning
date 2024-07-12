#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QIcon


class FirstMainWin(QMainWindow):
    def __init__(self, parent=None):
        super(FirstMainWin, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        # 设置窗口的位置和尺寸
        self.setGeometry(300, 300, 250, 250)
        # 主窗口标题
        self.setWindowTitle("设置窗口图标")
        # 设置窗口图标
        self.setWindowIcon(QIcon("../src/2.png"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = FirstMainWin()
    main.show()
    sys.exit(app.exec_())
    pass
