#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow, QApplication
from PyQt5.QtGui import QIcon


class CenterForm(QMainWindow):
    def __init__(self, parent=None):
        super(CenterForm, self).__init__(parent)

        # 主窗口标题
        self.setWindowTitle("主窗口居中")

        # 窗口尺寸
        self.resize(500, 400)

    def center(self):
        # 获取屏幕坐标系
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口坐标系
        size = self.geometry()
        left = (screen.width() - size.width()) / 2
        top = (screen.height() - size.height()) / 2
        self.move(left, top)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main = CenterForm()
    main.center()
    main.show()

    sys.exit(app.exec_())
    pass
