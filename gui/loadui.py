from PyQt5 import QtWidgets, QtCore, uic
from pathlib import Path
from picamera import PiCamera
from time import sleep

class UI(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        # load the ui file
        path = Path(Path.cwd(), 'ui', 'settings_groupbox.ui')
        uic.loadUi(path, self)

        # threads
        self.threads = {}

        # define our widgets

        # Menus #
        self.file_menu = self.findChild(QtWidgets.QMenu, 'menuFile')
        self.help_menu = self.findChild(QtWidgets.QMenu, 'menuHelp')

        # Settings Group #
        self.groupbox_settings = self.findChild(QtWidgets.QWidget, 'settings_groupbox')

        # brightness
        self.brightness_slider = self.findChild(QtWidgets.QSlider, 'brightness_slider')
        self.brightness_spinbox = self.findChild(QtWidgets.QSpinBox, 'brightness_spinbox')
        self.brightness_label = self.findChild(QtWidgets.QLabel, 'brightness_label')

        # brightness connections
        self.brightness_slider.valueChanged['int'].connect(self.brightness_spinbox.setValue)
        self.brightness_spinbox.valueChanged['int'].connect(self.brightness_slider.setValue)

        # sharpness
        self.sharpness_slider = self.findChild(QtWidgets.QSlider, 'sharpness_slider')
        self.sharpness_spinbox = self.findChild(QtWidgets.QSpinBox, 'sharpness_spinbox')
        self.sharpness_label = self.findChild(QtWidgets.QLabel, 'sharpness_label')

        # sharpness connections
        self.sharpness_slider.valueChanged['int'].connect(self.sharpness_spinbox.setValue)
        self.sharpness_spinbox.valueChanged['int'].connect(self.sharpness_slider.setValue)

        # contrast
        self.contrast_slider = self.findChild(QtWidgets.QSlider, 'contrast_slider')
        self.contrast_spinbox = self.findChild(QtWidgets.QSpinBox, 'contrast_spinbox')
        self.contrast_label = self.findChild(QtWidgets.QLabel, 'contrast_label')

        # contrast connections
        self.contrast_slider.valueChanged['int'].connect(self.contrast_spinbox.setValue)
        self.contrast_spinbox.valueChanged['int'].connect(self.contrast_slider.setValue)

        # saturation
        self.saturation_slider = self.findChild(QtWidgets.QSlider, 'saturation_slider')
        self.saturation_spinbox = self.findChild(QtWidgets.QSpinBox, 'saturation_spinbox')
        self.saturation_label = self.findChild(QtWidgets.QLabel, 'saturation_label')

        # saturation connections
        self.saturation_slider.valueChanged['int'].connect(self.saturation_spinbox.setValue)
        self.saturation_spinbox.valueChanged['int'].connect(self.saturation_slider.setValue)

        # iso
        self.iso_slider = self.findChild(QtWidgets.QSlider, 'iso_slider')
        self.iso_spinbox = self.findChild(QtWidgets.QSpinBox, 'iso_spinbox')
        self.iso_label = self.findChild(QtWidgets.QLabel, 'iso_label')

        # iso connections
        self.iso_slider.valueChanged['int'].connect(self.iso_spinbox.setValue)
        self.iso_spinbox.valueChanged['int'].connect(self.iso_slider.setValue)

        # take pic push button
        self.take_pic_push = self.findChild(QtWidgets.QPushButton, 'take_pic_push_button')

        # take pic connections
        self.take_pic_push.clicked.connect(self.take_pic)

    def take_pic(self):
        self.threads[1] = ThreadClass()
        self.threads[1].start()
        self.threads[1].any_signal.connect(self.my_function)
        self.take_pic_push.setEnabled(False)

    def pic_taken(self):
        self.threads[1].stop()
        self.take_pic_push.setEnabled(True)

    def my_function(self, counter):

        cnt = counter
        index = self.sender().index
        if index == 1:
            print("Taking picture")


class ThreadClass(QtCore.QThread):

    any_signal = QtCore.pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.is_running = True
        self.cam = PiCamera()

    def run(self):
        self.cam.start_preview()
        sleep(2)
        self.cam.capture('foo.jpg')
        self.cam.stop_preview()

    def stop(self):
        self.is_running = False
        self.cam.close()
        self.terminate()