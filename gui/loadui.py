from pathlib import Path
from picamera import PiCamera
from time import sleep

from PyQt5 import QtWidgets, uic


class UI(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        # load the ui file
        path = Path(Path.cwd(), 'ui', 'main_window.ui')
        uic.loadUi(path, self)

        self.cam = PiCamera()

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
        self.brightness_slider.valueChanged[int].connect(self.brightness_spinbox.setValue)
        self.brightness_spinbox.valueChanged[int].connect(self.brightness_slider.setValue)
        self.brightness_slider.valueChanged[int].connect(self.set_brightness)

        # sharpness
        self.sharpness_slider = self.findChild(QtWidgets.QSlider, 'sharpness_slider')
        self.sharpness_spinbox = self.findChild(QtWidgets.QSpinBox, 'sharpness_spinbox')
        self.sharpness_label = self.findChild(QtWidgets.QLabel, 'sharpness_label')

        # sharpness connections
        self.sharpness_slider.valueChanged[int].connect(self.sharpness_spinbox.setValue)
        self.sharpness_spinbox.valueChanged[int].connect(self.sharpness_slider.setValue)
        self.sharpness_slider.valueChanged[int].connect(self.set_sharpness)

        # contrast
        self.contrast_slider = self.findChild(QtWidgets.QSlider, 'contrast_slider')
        self.contrast_spinbox = self.findChild(QtWidgets.QSpinBox, 'contrast_spinbox')
        self.contrast_label = self.findChild(QtWidgets.QLabel, 'contrast_label')

        # contrast connections
        self.contrast_slider.valueChanged[int].connect(self.contrast_spinbox.setValue)
        self.contrast_spinbox.valueChanged[int].connect(self.contrast_slider.setValue)
        self.contrast_slider.valueChanged[int].connect(self.set_contrast)

        # saturation
        self.saturation_slider = self.findChild(QtWidgets.QSlider, 'saturation_slider')
        self.saturation_spinbox = self.findChild(QtWidgets.QSpinBox, 'saturation_spinbox')
        self.saturation_label = self.findChild(QtWidgets.QLabel, 'saturation_label')

        # saturation connections
        self.saturation_slider.valueChanged[int].connect(self.saturation_spinbox.setValue)
        self.saturation_spinbox.valueChanged[int].connect(self.saturation_slider.setValue)
        self.saturation_slider.valueChanged[int].connect(self.set_saturation)

        # iso
        self.iso_slider = self.findChild(QtWidgets.QSlider, 'iso_slider')
        self.iso_spinbox = self.findChild(QtWidgets.QSpinBox, 'iso_spinbox')
        self.iso_label = self.findChild(QtWidgets.QLabel, 'iso_label')

        # iso connections
        self.iso_slider.valueChanged[int].connect(self.iso_spinbox.setValue)
        self.iso_spinbox.valueChanged[int].connect(self.iso_slider.setValue)
        self.iso_slider.valueChanged[int].connect(self.set_iso)

        # push buttons
        self.start_preview_button = self.findChild(QtWidgets.QPushButton, 'start_preview_button')
        self.stop_preview_button = self.findChild(QtWidgets.QPushButton, 'stop_preview_button')
        self.take_pic_button = self.findChild(QtWidgets.QPushButton, 'pic_button')

        # push buttons connections
        self.start_preview_button.clicked.connect(self.start_preview)
        self.stop_preview_button.clicked.connect(self.stop_preview)
        self.take_pic_button.clicked.connect(self.take_pic)

    def set_brightness(self, value):
        self.cam.brightness = value

    def set_sharpness(self, value):
        self.cam.sharpness = value

    def set_contrast(self, value):
        self.cam.contrast = value

    def set_saturation(self, value):
        self.cam.saturation = value

    def set_iso(self, value):
        self.cam.iso = value

    def start_preview(self):
        self.cam.start_preview(fullscreen=False, window=(1000, 500, 800, 640))
        sleep(2)

    def stop_preview(self):
        self.cam.stop_preview()

    def take_pic(self):
        self.cam.start_preview()
        sleep(5)
        self.cam.capture('foo.jpg')
        self.cam.stop_preview()

