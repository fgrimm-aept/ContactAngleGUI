#!/usr/bin/env python

from gui.loadui import UI
from PyQt5 import QtWidgets
import sys
# from picamera import PiCamera


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('fusion')
    ui_window = UI()
    ui_window.showMaximized()
    app.exec_()


if __name__ == '__main__':
    main()
