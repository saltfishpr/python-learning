#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt


class QTextEditDemo(QWidget):
    def __init__(self):
        super(QTextEditDemo, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("QTextEdit控件")
        self.resize(400, 300)


if __name__ == "__main__":
    pass
