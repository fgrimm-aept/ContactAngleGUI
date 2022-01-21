#!/usr/bin/env python3

from picamera import PiCamera
from time import sleep
from PyQt5 import QtWidgets, QtCore
import sys


class MainWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        
        self.cam = PiCamera()

        self.setLayout(QtWidgets.QVBoxLayout())
        
        self.start_preview_button = QtWidgets.QPushButton("Start Preview", self)
        self.start_preview_button.clicked.connect(self.start_preview)
        self.layout().addWidget(self.start_preview_button)

        self.stop_preview_button = QtWidgets.QPushButton("Stop Preview", self)
        self.stop_preview_button.clicked.connect(self.stop_preview)
        self.layout().addWidget(self.stop_preview_button)
        
        self.pic_button = QtWidgets.QPushButton("Take a picture", self)
        self.pic_button.clicked.connect(self.take_pic)
        self.layout().addWidget(self.pic_button)

        self.brightness_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.brightness_slider.valueChanged[int].connect(self.set_brightness)
        self.layout().addWidget(self.brightness_slider)

        self.show()
<<<<<<< HEAD

    def take_pic(self):
        cam = PiCamera()
        cam.resolution = (1920, 1080)
        cam.brightness = 70
        cam.start_preview()
=======
    
    def start_preview(self):
        self.cam.resolution = (1920, 1080)
        
        self.cam.start_preview(fullscreen=False, window=(1000, 500, 800, 640))
        
>>>>>>> d0d5c38db243ea08077501f1a425871cec426a75
        sleep(2)
    
    def stop_preview(self):
        self.cam.stop_preview()

    def take_pic(self):
        self.cam.capture('foo.jpg')

    def set_brightness(self, value):
        self.cam.brightness = value



def main():
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    app.exec_()


if __name__ == '__main__':
    main()
