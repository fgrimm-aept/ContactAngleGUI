import json
import time
from pathlib import Path

from PyQt5 import QtWidgets, uic, QtCore, QtGui
from picamera import PiCamera


class UI(QtWidgets.QMainWindow):
    RESIZED = QtCore.pyqtSignal()
    PREVIEW_POS = (630, 161, 1280, 720)

    def __init__(self):
        super().__init__()

        # PiCamera init
        self.cam = PiCamera()

        # load the ui file
        path = Path(Path.cwd(), 'ui', 'main_window.ui')
        uic.loadUi(path, self)

        # thread
        self.worker = WorkerThread(cam=self.cam)
        self.settings = {'brightness': self.cam.brightness,
                         'sharpness': self.cam.sharpness,
                         'contrast': self.cam.contrast,
                         'saturation': self.cam.saturation,
                         'iso': self.cam.iso}
        self.paths = {'settings': Path(Path.cwd(), 'settings'),
                      'pictures': Path(Path.cwd(), 'pictures')}
        for path in self.paths.values():
            path.mkdir(parents=True, exist_ok=True)
        self.default_settings = Path(self.paths['settings'], 'default.json')
        try:
            with open(f'{self.default_settings}', 'r') as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            with open(f'{self.default_settings}', 'w') as f:
                json.dump(self.settings, f)

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
        self.iso_combobox = self.findChild(QtWidgets.QComboBox, 'iso_combobox')
        self.iso_combobox.addItem("Auto", 0)
        self.iso_combobox.addItem("100", 100)
        self.iso_combobox.addItem("200", 200)
        self.iso_combobox.addItem("320", 320)
        self.iso_combobox.addItem("400", 400)
        self.iso_combobox.addItem("500", 500)
        self.iso_combobox.addItem("640", 640)
        self.iso_combobox.addItem("800", 800)

        # iso connections
        self.iso_combobox.activated.connect(self.set_iso)

        # push buttons
        self.preview_button = self.findChild(QtWidgets.QPushButton, 'preview_button')
        self.preview_button.setCheckable(True)
        self.take_pic_button = self.findChild(QtWidgets.QPushButton, 'pic_button')

        # push buttons connections
        self.preview_button.clicked.connect(self.preview)
        self.take_pic_button.clicked.connect(self.take_pic)

        # Window Events
        self.RESIZED.connect(self.resize_window)
        self.installEventFilter(self)

    def eventFilter(self, a0: 'QObject', a1: 'QEvent') -> bool:
        if a1.type() == QtCore.QEvent.WindowDeactivate:
            self.cam.stop_preview()
            self.preview_button.setChecked(False)
        if a1.type() == QtCore.QEvent.WindowStateChange:
            self.cam.stop_preview()
            self.preview_button.setChecked(False)
        return False

    def set_brightness(self, value):
        self.cam.brightness = value

    def set_sharpness(self, value):
        self.cam.sharpness = value

    def set_contrast(self, value):
        self.cam.contrast = value

    def set_saturation(self, value):
        self.cam.saturation = value

    def set_iso(self, index):
        self.cam.iso = self.iso_combobox.itemData(index)

    def preview(self):
        if self.preview_button.isChecked():
            self.start_preview()
        else:
            self.stop_preview()

    def start_preview(self):
        self.cam.start_preview(fullscreen=False, window=self.PREVIEW_POS)

    def stop_preview(self):
        self.cam.stop_preview()

    def take_pic(self):
        self.take_pic_button.setDisabled(True)
        self.worker.start()
        self.worker.finished.connect(self.evt_worker_finished)

    def evt_worker_finished(self):
        self.take_pic_button.setDisabled(False)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.RESIZED.emit()

    def resize_window(self):
        self.showMaximized()


class WorkerThread(QtCore.QThread):

    def __init__(self, cam):
        super().__init__()
        self.cam = cam

    def run(self):
        time.sleep(5)
        self.cam.capture('foo.jpg')
