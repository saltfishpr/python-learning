#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
限制QLineEdit控件的输入（校验器）
"""
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QRegExpValidator
from PyQt5.QtCore import QRegExp


class QLineEditValidator(QWidget):
    def __init__(self):
        super(QLineEditValidator, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("校验器")

        form_layout = QFormLayout()
        int_line_edit = QLineEdit()
        double_line_edit = QLineEdit()
        validator_line_edit = QLineEdit()

        form_layout.addRow("整数类型", int_line_edit)
        form_layout.addRow("浮点类型", double_line_edit)
        form_layout.addRow("数字和字母", validator_line_edit)

        int_line_edit.setPlaceholderText("整数类型")
        double_line_edit.setPlaceholderText("浮点类型")
        validator_line_edit.setPlaceholderText("数字和字母")

        # 整数校验器
        int_validator = QIntValidator(self)
        int_validator.setRange(0, 99)
        # 浮点校验器,精度：小数点后两位
        double_validator = QDoubleValidator(self)
        double_validator.setRange(-99, 99)
        double_validator.setNotation(QDoubleValidator.StandardNotation)
        double_validator.setDecimals(2)  # 设置精度，小数点后两位
        # 字符和数字
        reg = QRegExp("[a-zA-Z0-9]+$")  # 正则表达式
        validator = QRegExpValidator(self)
        validator.setRegExp(reg)

        int_line_edit.setValidator(int_validator)
        double_line_edit.setValidator(double_validator)
        validator_line_edit.setValidator(validator)

        self.setLayout(form_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = QLineEditValidator()
    main.show()
    sys.exit(app.exec_())
    pass
