import json
import logging
import time
from pathlib import Path

from PyQt5 import QtWidgets, uic, QtCore, QtGui
from picamera import PiCamera


class WorkerThread(QtCore.QThread):

    def __init__(self, cam, path):
        super().__init__()
        self.cam = cam
        self.path = path

    def run(self):
        time.sleep(5)
        self.cam.capture(f'{self.path}')


class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtGui.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

    # TODO: add statusbar or logging field with information about what is being done


class UI(QtWidgets.QMainWindow):
    RESIZED = QtCore.pyqtSignal()
    FILE_DELETED = QtCore.pyqtSignal()
    PREVIEW_POS = (630, 161, 1280, 720)

    def __init__(self):
        super().__init__()

        # PiCamera init
        self.cam = PiCamera()

        # load the ui file
        ui_path = Path(Path.cwd(), 'ui', 'main_window.ui')
        uic.loadUi(ui_path, self)

        # Directories Setup
        self.paths = {'profiles': Path(Path.cwd(), 'profiles'),
                      'pictures': Path(Path.cwd(), 'pictures')}
        for path in self.paths.values():
            path.mkdir(parents=True, exist_ok=True)

        # Save Cam Settings in dict
        self.default_settings = {'brightness': 50,
                                 'sharpness': 0,
                                 'contrast': 0,
                                 'saturation': 0,
                                 'iso': 0}

        self.current_settings = self.default_settings

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
        self.iso_combobox.currentIndexChanged.connect(self.set_iso)

        # picture push buttons
        self.preview_button = self.findChild(QtWidgets.QPushButton, 'preview_button')
        self.preview_button.setCheckable(True)
        self.take_pic_button = self.findChild(QtWidgets.QPushButton, 'pic_button')
        self.load_pic_button = self.findChild(QtWidgets.QPushButton, 'load_pic_button')
        self.reset_button = self.findChild(QtWidgets.QPushButton, 'reset_button')

        # picture push buttons connections
        self.preview_button.clicked.connect(self.preview)
        self.take_pic_button.clicked.connect(self.take_pic)
        self.load_pic_button.clicked.connect(self.load_pic)
        self.reset_button.clicked.connect(self.reset_values)

        # Profile Groupbox #

        self.groupbox_profile = self.findChild(QtWidgets.QWidget, 'profile_groupbox')

        # set profile names
        self.profile_name_line_edit = self.findChild(QtWidgets.QLineEdit, 'profile_name_line_edit')
        self.profile_name_combobox = self.findChild(QtWidgets.QComboBox, 'load_profile_combobox')

        # set profile names connections
        self.profile_name_line_edit.returnPressed.connect(self.save_profile)

        # save/load profile buttons
        self.save_profile_button = self.findChild(QtWidgets.QPushButton, 'save_profile_button')
        self.load_profile_button = self.findChild(QtWidgets.QPushButton, 'load_profile_button')
        self.delete_profile_button = self.findChild(QtWidgets.QPushButton, 'delete_profile_button')

        # push buttons connections
        self.save_profile_button.clicked.connect(self.save_profile)
        self.load_profile_button.clicked.connect(self.load_profile)
        self.delete_profile_button.clicked.connect(self.delete_profile)
        self.delete_profile_button.clicked.connect(self.set_profile_combobox)

        # Window Events
        self.RESIZED.connect(self.resize_window)
        self.installEventFilter(self)
        self.FILE_DELETED.connect(self.set_profile_combobox)

        # set UI
        self.start_preview()
        self.set_profile_combobox()

        self.pic_name_line_edit = self.findChild(QtWidgets.QLineEdit, 'pic_name_line_edit')
        pic_name = self.pic_name_line_edit.text()
        if not pic_name:
            pic_name = 'foo.jpg'
        pic_path = Path(self.paths['pictures'], pic_name)
        self.worker = WorkerThread(cam=self.cam, path=pic_path)

    def save_profile(self):

        self.current_settings = {'brightness': self.brightness_spinbox.value(),
                                 'sharpness': self.sharpness_spinbox.value(),
                                 'contrast': self.contrast_spinbox.value(),
                                 'saturation': self.saturation_spinbox.value(),
                                 'iso': self.iso_combobox.currentIndex()}
        profile_name = self.profile_name_line_edit.text()
        if not profile_name:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText('No profile name set.')
            msg.setWindowTitle("Error")
            msg.exec_()
            return
        path = Path(self.paths['profiles'], f'{profile_name}.json')
        with open(path, 'w') as save_file:
            json.dump(self.current_settings, save_file)
        self.set_profile_combobox()

    def set_profile_combobox(self):
        self.profile_name_combobox.clear()
        files = sorted(self.paths['profiles'].glob('*.json'), key=lambda path: path.stem.upper())
        for file in files:
            self.profile_name_combobox.addItem(file.stem, file)

    def load_profile(self):
        path = self.profile_name_combobox.currentData()
        with open(path, 'r') as load_file:
            self.current_settings = json.load(load_file)
        self.profile_name_line_edit.setText(path.stem)
        self.set_values()

    def delete_profile(self):

        profile = self.profile_name_combobox.currentText()
        if not profile:
            return
        path = Path(self.paths['profiles'], f'{profile}.json')
        qm = QtWidgets.QMessageBox()

        ret = qm.question(self, 'Warning', f'Are you sure you want to delete the profile: '
                                           f'{profile}', qm.Yes | qm.No)

        if ret == qm.Yes:
            if path.is_file():
                path.unlink()
                self.FILE_DELETED.emit()
            else:
                return
        else:
            return

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
        # thread creation for camera

        self.take_pic_button.setDisabled(True)
        self.worker.start()
        self.worker.finished.connect(self.evt_worker_finished)

    def evt_worker_finished(self):
        self.take_pic_button.setDisabled(False)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.RESIZED.emit()

    def resize_window(self):
        self.showMaximized()

    def load_pic(self):
        pass

    def reset_values(self):
        self.brightness_spinbox.setValue(self.default_settings['brightness'])
        self.sharpness_spinbox.setValue(self.default_settings['sharpness'])
        self.contrast_spinbox.setValue(self.default_settings['contrast'])
        self.saturation_spinbox.setValue(self.default_settings['saturation'])
        self.iso_combobox.setCurrentIndex(0)

    def set_values(self):
        self.brightness_spinbox.setValue(self.current_settings['brightness'])
        self.sharpness_spinbox.setValue(self.current_settings['sharpness'])
        self.contrast_spinbox.setValue(self.current_settings['contrast'])
        self.saturation_spinbox.setValue(self.current_settings['saturation'])
        self.iso_combobox.setCurrentIndex(self.current_settings['iso'])
        # all_elements = [(self.iso_combobox.itemText(i), self.iso_combobox.itemData(i))
        #                 for i in range(self.iso_combobox.count())]
        # for i, elem in enumerate(all_elements):
        #     if elem[1] == self.current_settings['iso']:
        #         self.iso_combobox.setCurrentIndex(i)
        #         break
        # else:
        #     self.iso_combobox.setCurrentIndex(0)
