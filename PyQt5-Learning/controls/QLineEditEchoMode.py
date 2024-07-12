#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QLineEdit控件与回显模式
基本功能：输入单行的文本
设置回显模式EchoMode
1. Normal 正常模式
2. NoEcho 不回显
3. Password 密码模式
4. PasswordEchoOnEdit 输入时回显
"""
import sys
from PyQt5.QtWidgets import *


class QLineEditEchoMode(QWidget):
    def __init__(self):
        super(QLineEditEchoMode, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("文本输入框回显模式")
        normal_line_edit = QLineEdit()
        no_echo_line_edit = QLineEdit()
        password_line_edit = QLineEdit()
        password_echo_on_edit_line_edit = QLineEdit()
        form_layout = QFormLayout()
        form_layout.addRow("Normal", normal_line_edit)
        form_layout.addRow("NoEcho", no_echo_line_edit)
        form_layout.addRow("Password", password_line_edit)
        form_layout.addRow("PasswordEchoOnEdit", password_echo_on_edit_line_edit)

        # placeholdertext 文本框输入内容提示
        normal_line_edit.setPlaceholderText("Normal")
        no_echo_line_edit.setPlaceholderText("NoEcho")
        password_line_edit.setPlaceholderText("Password")
        password_echo_on_edit_line_edit.setPlaceholderText("PasswordEchoOnEdit")

        normal_line_edit.setEchoMode(QLineEdit.Normal)
        no_echo_line_edit.setEchoMode(QLineEdit.NoEcho)
        password_line_edit.setEchoMode(QLineEdit.Password)
        password_echo_on_edit_line_edit.setEchoMode(QLineEdit.PasswordEchoOnEdit)

        self.setLayout(form_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = QLineEditEchoMode()
    main.show()
    sys.exit(app.exec_())
    pass
