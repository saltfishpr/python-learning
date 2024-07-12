#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt


class QLineEditDemo(QWidget):
    def __init__(self):
        super(QLineEditDemo, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("QLineEdit综合案例")
        form_layout = QFormLayout()

        # 整数校验
        edit1 = QLineEdit()
        edit1.setValidator(QIntValidator())
        edit1.setMaxLength(4)
        edit1.setAlignment(Qt.AlignRight)  # 右对齐
        edit1.setFont(QFont("Arial", 20))

        form_layout.addRow("整数校验", edit1)

        self.setLayout(form_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = QLineEditDemo()
    main.show()
    sys.exit(app.exec_())
    pass
