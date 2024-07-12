#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QLabel和伙伴控件
"""
import sys
from PyQt5.QtWidgets import *


class QLabelBuddy(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("QLabelBuddy")
        name_label = QLabel("&Name", self)
        name_line_edit = QLineEdit(self)
        # 设置伙伴控件
        name_label.setBuddy(name_line_edit)

        password_label = QLabel("&Password", self)
        password_line_edit = QLineEdit(self)
        # 设置伙伴控件
        password_label.setBuddy(password_line_edit)

        btn_ok = QPushButton("&OK")
        btn_cancel = QPushButton("&Cancel")
        # 栅格布局
        main_layout = QGridLayout(self)
        main_layout.addWidget(name_label, 0, 0)
        main_layout.addWidget(name_line_edit, 0, 1, 1, 2)  # 参数：控件对象，控件位置和尺寸
        main_layout.addWidget(password_label, 1, 0)
        main_layout.addWidget(password_line_edit, 1, 1, 1, 2)
        main_layout.addWidget(btn_ok, 2, 1)
        main_layout.addWidget(btn_cancel, 2, 2)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = QLabelBuddy()
    main.show()
    sys.exit(app.exec_())
    pass
