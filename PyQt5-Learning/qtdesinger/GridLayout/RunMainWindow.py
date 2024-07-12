#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import demo
from PyQt5.QtWidgets import QApplication, QMainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = demo.Ui_MainWindow()
    # 向主窗口添加控件
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())
    pass
