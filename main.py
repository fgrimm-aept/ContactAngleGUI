#!/usr/bin/env python3

from gui.loadui import UI
from PyQt5 import QtWidgets
import sys
# from picamera import PiCamera
import time


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui_window = UI()
    ui_window.showMaximized()
    app.exec_()
    print(ui_window.settings)


if __name__ == '__main__':
    main()
