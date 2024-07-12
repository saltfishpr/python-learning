#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QToolTip,
    QMainWindow,
    QPushButton,
    QApplication,
    QWidget,
)
from PyQt5.QtGui import QFont


class ToolTipForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        QToolTip.setFont(QFont("SanSerif", 10))
        self.setToolTip("今天是<b>星期五</b>")
        self.setGeometry(300, 300, 400, 300)
        self.setWindowTitle("控件提示消息")

        # 添加button
        self.button1 = QPushButton("窗口按钮")
        self.button1.setToolTip("这是一个按钮")

        layout = QHBoxLayout()
        layout.addWidget(self.button1)
        mainFrame = QWidget()
        mainFrame.setLayout(layout)

        self.setCentralWidget(mainFrame)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = ToolTipForm()
    main.show()
    sys.exit(app.exec_())
    pass
