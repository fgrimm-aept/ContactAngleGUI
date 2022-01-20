#/usr/bin/env python3

from gui.loadui import UI
from PyQt5 import QtWidgets
import sys


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui_window = UI()
    ui_window.show()
    app.exec_()


if __name__ == '__main__':
    main()
