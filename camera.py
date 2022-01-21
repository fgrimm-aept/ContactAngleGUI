#!/usr/bin/env python3

from picamera import PiCamera
from time import sleep
from PyQt5 import QtWidgets, QtCore
import sys


class MainWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        
        self.setLayout(QtWidgets.QVBoxLayout())

        self.take_pic_button = QtWidgets.QPushButton("Take a picture", self)
        self.take_pic_button.clicked.connect(self.take_pic)
        self.layout().addWidget(self.take_pic_button)

        self.show()

    def take_pic(self):
        cam = PiCamera()
        cam.resolution = (1920, 1080)
        cam.brightness = 70
        cam.start_preview()
        sleep(2)
        cam.capture('foo.jpg')

        cam.close()


def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    app.exec_()


if __name__ == '__main__':
    main()
