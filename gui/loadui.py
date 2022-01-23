import json
import logging
import sys
import time
from datetime import datetime
from os import chown
from pathlib import Path

from PyQt5 import QtWidgets, uic, QtCore, QtGui
from picamera import PiCamera


# TODO: QSettings benutzen um root -> XOFFSET,YOFFSET und user -> XOFFSET,YOFFSET zu speichern?
# TODO: Fix setting directory for cam picture
# TODO: Set Tooltips for all elements (at least for quality)
# TODO: Fix Shortcuts
# TODO: Fail safe einbauen für den Fall das man ein profil lädt mit einem unbekannten Pfad
#  (z.B. nicht mehr vorhandener USB-Stick als Pfad)

class WorkerThread(QtCore.QThread):
    TIMESTAMP = QtCore.pyqtSignal(str)

    def __init__(self, obj):
        # TODO: send data to worker thread through signal, slot not through __init__
        super().__init__()
        self.obj = obj
        self.cam = obj.cam
        self.pic_directory = Path(obj.pic_directory)
        self.pic_name = Path(obj.pic_name)
        self.pic_format = obj.pic_format
        self.quality = obj.quality
        obj.CAMERA_SETTINGS.connect(self.set_settings)

    def set_settings(self, settings):
        self.pic_directory = settings['directory']
        self.pic_name = settings['name']
        self.pic_format = settings['format']
        self.quality = settings['quality']

    def run(self):
        # TODO: Replace with QTimer instead of sleep()?
        #  https://doc.qt.io/qtforpython-5/overviews/timers.html#timers
        time.sleep(5)
        timestamp = datetime.now().strftime('%Y_%m_%dT%H_%M_%S')
        full_path = Path(self.pic_directory, f"{self.pic_name}_{timestamp}.{self.pic_format}")
        if self.pic_format == 'jpeg':
            self.cam.capture(f'{full_path}', quality=self.quality, format=f'{self.pic_format}')
        else:
            self.cam.capture(f'{full_path}', format=f'{self.pic_format}')
        chown(full_path, 1000, 1000)
        self.TIMESTAMP.emit(timestamp)


class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtGui.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

    # TODO: add statusbar or logging field with information about what is being done
    # TODO: menu events (File, Help)


class UI(QtWidgets.QMainWindow):
    CAMERA_SETTINGS = QtCore.pyqtSignal(dict)
    RESIZED = QtCore.pyqtSignal()
    FILE_DELETED = QtCore.pyqtSignal()
    X_OFFSET = 0
    Y_OFFSET = 0
    PREVIEW_RUNNING = False
    PROGRAM_START_TIME = datetime.now().strftime('%Y_%m_%dT%H_%M_%S')

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
                                 'iso': 0,
                                 'quality': 75,
                                 'directory': f'{self.paths["pictures"]}',
                                 'filename': 'foo',
                                 'pic_format': 0}
        path = Path(self.paths['profiles'], 'default.json')
        with open(path, 'w') as f_default:
            json.dump(self.default_settings, f_default)
            chown(path, 1000, 1000)

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
        self.iso_label = self.findChild(QtWidgets.QLabel, 'iso_label')
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

        # quality
        self.quality_slider = self.findChild(QtWidgets.QSlider, 'quality_slider')
        self.quality_spinbox = self.findChild(QtWidgets.QSpinBox, 'quality_spinbox')
        self.quality_label = self.findChild(QtWidgets.QLabel, 'quality_label')

        # quality connections
        self.quality_slider.valueChanged[int].connect(self.quality_spinbox.setValue)
        self.quality_spinbox.valueChanged[int].connect(self.quality_slider.setValue)
        self.quality = 75
        self.quality_slider.valueChanged[int].connect(self.set_quality)

        # camera push buttons
        self.preview_button = self.findChild(QtWidgets.QPushButton, 'preview_button')
        self.preview_button.setCheckable(True)
        self.preview_button.setToolTip('Toggles camera Preview.\nShortcut: "P", "Space"')
        self.preview_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_P), self)
        self.preview_shortcut.activated.connect(self.toggle_preview)
        self.preview_shortcut_space = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Space), self)
        self.preview_shortcut_space.activated.connect(self.toggle_preview)
        self.take_pic_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_T), self)
        self.take_pic_shortcut.activated.connect(self.take_pic)
        self.load_pic_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_L), self)
        self.load_pic_shortcut.activated.connect(self.open_picture)

        self.take_pic_button = self.findChild(QtWidgets.QPushButton, 'pic_button')
        self.take_pic_button.setToolTip('Takes a picture with the current settings.\n Shortcut: "T"')
        self.load_pic_button = self.findChild(QtWidgets.QPushButton, 'load_pic_button')
        self.load_pic_button.setToolTip('Load a picture to be displayed.\n Shortcut: "L"')
        self.open_picture_dialog = QtWidgets.QFileDialog(self)
        self.open_picture_dialog.setWindowTitle('Open Picture')
        self.open_picture_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        self.open_picture_dialog.setOption(QtWidgets.QFileDialog.DontResolveSymlinks, True)
        self.open_picture_dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        self.reset_button = self.findChild(QtWidgets.QPushButton, 'reset_button')

        # camera push buttons connections
        self.preview_button.clicked.connect(self.preview)
        self.take_pic_button.clicked.connect(self.take_pic)
        self.load_pic_button.clicked.connect(self.open_picture)
        self.reset_button.clicked.connect(self.reset_values)

        # set profile names
        self.profile_name_save_label = self.findChild(QtWidgets.QLabel, 'profile_name_save_label')
        self.profile_name_load_label = self.findChild(QtWidgets.QLabel, 'profile_name_load_label')
        self.profile_name_line_edit = self.findChild(QtWidgets.QLineEdit, 'profile_name_line_edit')
        self.profile_name_line_edit.setText('default')
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

        # picture buttons
        self.pic_dir_label = self.findChild(QtWidgets.QLabel, 'pic_dir_label')
        self.pic_dir_line_edit = self.findChild(QtWidgets.QLineEdit, 'pic_dir_line_edit')
        self.pic_dir_line_edit.setText(f"{Path('..', self.paths['pictures'].parent.name, self.paths['pictures'].stem)}")
        self.pic_name_line_edit = self.findChild(QtWidgets.QLineEdit, 'pic_name_line_edit')
        self.pic_name_line_edit.setText('foo')
        self.pic_dir_button = self.findChild(QtWidgets.QPushButton, 'pic_dir_button')
        self.open_directory_dialog = QtWidgets.QFileDialog(self)
        self.open_directory_dialog.setWindowTitle('Open picture save directory')
        self.open_directory_dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        self.open_directory_dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
        self.open_directory_dialog.setOption(QtWidgets.QFileDialog.DontResolveSymlinks, True)
        self.open_directory_dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        self.pic_name_label = self.findChild(QtWidgets.QLabel, 'pic_name_label')
        self.pic_format_combobox = self.findChild(QtWidgets.QComboBox, 'pic_format_combobox')
        self.pic_format_combobox.addItem('jpeg', True)
        self.pic_format_combobox.addItem('png', False)
        self.pic_format_combobox.addItem('gif', False)
        self.pic_format_combobox.addItem('bmp', False)
        self.pic_format_combobox.addItem('yuv', False)
        self.pic_format_combobox.addItem('rgb', False)
        self.pic_format_combobox.addItem('rgba', False)
        self.pic_format_combobox.addItem('bgr', False)
        self.pic_format_combobox.addItem('bgra', False)

        # init status bar with default values
        full_path = Path(self.paths['pictures'], f'foo_{{timestamp}}.jpg')
        self.pic_dir_line_edit.setStatusTip(f'{full_path.parent}')
        self.pic_name_line_edit.setStatusTip(f'{full_path}')

        self.take_pic_button.setStatusTip(f'{full_path}')

        # picture buttons connections
        self.pic_format_combobox.currentIndexChanged.connect(self.toggle_quality)
        self.pic_format_combobox.currentIndexChanged.connect(self.set_pic_format)
        self.pic_name_line_edit.editingFinished.connect(self.set_pic_name)
        self.pic_dir_button.clicked.connect(self.open_directory)

        # set status bar connections
        self.pic_format_combobox.currentIndexChanged.connect(self.set_statusbar)
        self.pic_dir_line_edit.textEdited.connect(self.set_statusbar)
        self.pic_name_line_edit.textEdited.connect(self.set_statusbar)

        # Window Events
        self.RESIZED.connect(self.resize_window)
        self.installEventFilter(self)
        self.FILE_DELETED.connect(self.set_profile_combobox)

        # set UI
        self.set_profile_combobox()

        # Take Picture Events
        self.pic_name = 'foo'
        self.pic_format = 'jpeg'
        self.pic_directory = Path(self.paths['pictures'])
        self.timestamp = datetime.now().strftime('%Y_%m_%dT%H_%M_%S')
        self.worker = WorkerThread(self)
        self.worker.TIMESTAMP.connect(self.set_timestamp)

        # offset sliders
        self.x_offset_slider = self.findChild(QtWidgets.QSlider, 'x_offset_slider')
        self.y_offset_slider = self.findChild(QtWidgets.QSlider, 'y_offset_slider')

        # offset slider connections
        self.x_offset_slider.sliderMoved.connect(self.move_preview_x)
        self.x_offset_slider.valueChanged.connect(self.move_preview_x)
        self.y_offset_slider.sliderMoved.connect(self.move_preview_y)
        self.y_offset_slider.valueChanged.connect(self.move_preview_y)

        # preview frame
        self.preview_frame = self.findChild(QtWidgets.QFrame, 'preview_frame')
        self.preview_pos = (self.preview_frame.geometry().x() + self.X_OFFSET,
                            self.preview_frame.geometry().y() + 85 + self.Y_OFFSET,
                            self.preview_frame.frameGeometry().width(),
                            self.preview_frame.frameGeometry().height())
        self.picture_label = self.findChild(QtWidgets.QLabel, 'picture_label')

    def set_pic_format(self):
        self.pic_format = self.pic_format_combobox.currentText()

    def set_pic_name(self):
        self.pic_name = self.pic_name_line_edit.text()

    def open_directory(self):
        home_path = str(self.pic_directory)
        self.open_directory_dialog.setDirectory(home_path)
        self.open_directory_dialog.open()
        self.open_directory_dialog.finished.connect(self.set_directory)

    def set_directory(self, value):

        if value == 1:
            self.pic_directory = Path(self.open_directory_dialog.selectedFiles()[0])
            chown(self.pic_directory, 1000, 1000)
            string = f"{Path('..', self.pic_directory.parent.name, self.pic_directory.stem)}"
            self.pic_dir_line_edit.setText(string)
            self.set_statusbar()
        if value == 0:
            return

    def open_picture(self):
        home_path = str(self.pic_directory)
        print(home_path)
        self.open_picture_dialog.setDirectory(home_path)
        self.open_picture_dialog.open()
        self.open_picture_dialog.finished.connect(self.display_picture)

    def display_picture(self, value):
        if value == 1:
            path = Path(self.open_directory_dialog.selectedFiles()[0])
            img = QtGui.QPixmap(f'{path}')
            self.picture_label.setPixmap(img)
        if value == 0:
            return

    def set_statusbar(self):
        path = Path(self.pic_directory, f"{self.pic_name}_{{timestamp}}.{self.pic_format}")
        self.pic_dir_line_edit.setStatusTip(f'{path}')
        self.pic_name_line_edit.setStatusTip(f'{path}')
        self.take_pic_button.setStatusTip(f'{path}')
        self.pic_dir_button.setStatusTip(f'{path}')
        self.pic_format_combobox.setStatusTip(f'{path}')

    def save_profile(self):

        self.current_settings = {'brightness': self.brightness_spinbox.value(),
                                 'sharpness': self.sharpness_spinbox.value(),
                                 'contrast': self.contrast_spinbox.value(),
                                 'saturation': self.saturation_spinbox.value(),
                                 'iso': self.iso_combobox.currentIndex(),
                                 'directory': f'{self.pic_directory}',
                                 'filename': self.pic_name,
                                 'pic_format': self.pic_format_combobox.currentIndex()}
        profile_name = self.profile_name_line_edit.text()
        if profile_name == 'default':
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText('Can not overwrite default profile')
            msg.setWindowTitle("Error")
            msg.exec_()
            return
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
            chown(path, 1000, 1000)
        self.set_profile_combobox()

    def set_profile_combobox(self):
        self.profile_name_combobox.clear()
        files = sorted(self.paths['profiles'].glob('*.json'), key=lambda path: path.stem.upper())
        for file in files:
            self.profile_name_combobox.addItem(file.stem, file)

    def load_profile(self):
        path = self.profile_name_combobox.currentData()
        try:
            with open(path, 'r') as load_file:
                self.current_settings = json.load(load_file)
        except TypeError:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText('No profile selected.')
            msg.setWindowTitle("Error")
            msg.exec_()
            return
        self.profile_name_line_edit.setText(path.stem)
        self.set_values()

    def delete_profile(self):

        profile = self.profile_name_combobox.currentText()
        if profile == 'default':
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText('Can not delete default profile')
            msg.setWindowTitle("Error")
            msg.exec_()
            return
        if not profile:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText('No profile selected.')
            msg.setWindowTitle("Error")
            msg.exec_()
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
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setText('No profile selected.')
                msg.setWindowTitle("Error")
                msg.exec_()
                return
        else:
            return

    def eventFilter(self, a0: 'QtCore.QObject', a1: 'QtCore.QEvent') -> bool:
        if a1.type() == QtCore.QEvent.WindowDeactivate:
            self.cam.stop_preview()
            self.PREVIEW_RUNNING = False
            self.preview_button.setChecked(False)
        if a1.type() == QtCore.QEvent.WindowStateChange:
            self.cam.stop_preview()
            self.PREVIEW_RUNNING = False
            self.preview_button.setChecked(False)
        return False

    def closeEvent(self, a0):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def move_preview_x(self, value):
        if self.cam.preview:
            self.X_OFFSET = value
            preview_pos = (self.preview_pos[0] + value,
                           self.preview_pos[1],
                           self.preview_pos[2],
                           self.preview_pos[3])
            self.cam.preview.window = preview_pos
        else:
            self.X_OFFSET = 0
            self.x_offset_slider.setValue(0)

    def move_preview_y(self, value):
        if self.cam.preview:
            self.Y_OFFSET = value
            preview_pos = (self.preview_pos[0],
                           self.preview_pos[1] + value,
                           self.preview_pos[2],
                           self.preview_pos[3])
            self.cam.preview.window = preview_pos
        else:
            self.Y_OFFSET = 0
            self.y_offset_slider.setValue(0)

    def toggle_quality(self):
        flag = self.pic_format_combobox.currentData()
        self.quality_slider.setEnabled(flag)
        self.quality_spinbox.setEnabled(flag)
        self.quality_label.setEnabled(flag)

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

    def set_quality(self, value):
        self.quality = value

    def preview(self):

        # possible way to resize window and set preview window accordingly
        self.preview_pos = (self.preview_frame.geometry().x() + self.X_OFFSET,
                            self.preview_frame.geometry().y() + 85 + self.Y_OFFSET,
                            self.preview_frame.frameGeometry().width(),
                            self.preview_frame.frameGeometry().height())
        if self.preview_button.isChecked():

            self.start_preview()
        else:

            self.stop_preview()

    def start_preview(self):
        self.x_offset_slider.setValue(self.X_OFFSET)
        self.y_offset_slider.setValue(self.Y_OFFSET)
        self.cam.start_preview(fullscreen=False, window=self.preview_pos)
        self.PREVIEW_RUNNING = True

    def stop_preview(self):
        self.cam.stop_preview()
        self.PREVIEW_RUNNING = False

    def toggle_preview(self):
        if self.PREVIEW_RUNNING:
            self.preview_button.setChecked(False)
            self.stop_preview()
        elif not self.PREVIEW_RUNNING:
            self.preview_button.setChecked(True)
            self.start_preview()

    def take_pic(self):
        self.groupbox_settings.setDisabled(True)
        settings = {'directory': self.pic_directory,
                    'name': self.pic_name,
                    'format': self.pic_format,
                    'quality': self.quality}
        self.CAMERA_SETTINGS.emit(settings)

        self.take_pic_button.setDisabled(True)
        self.worker.start()
        self.worker.finished.connect(self.evt_worker_finished)

    def evt_worker_finished(self):
        self.groupbox_settings.setDisabled(False)
        self.take_pic_button.setDisabled(False)

    def set_timestamp(self, timestamp):
        self.timestamp = timestamp

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.RESIZED.emit()
        # Possible way to be able to resize window
        super(UI, self).resizeEvent(event)

    def resize_window(self):
        self.showMaximized()

    def reset_values(self):
        self.brightness_spinbox.setValue(self.default_settings['brightness'])
        self.sharpness_spinbox.setValue(self.default_settings['sharpness'])
        self.contrast_spinbox.setValue(self.default_settings['contrast'])
        self.saturation_spinbox.setValue(self.default_settings['saturation'])
        self.iso_combobox.setCurrentIndex(0)
        self.quality_spinbox.setValue(self.default_settings['quality'])

    def set_values(self):
        self.brightness_spinbox.setValue(self.current_settings['brightness'])
        self.sharpness_spinbox.setValue(self.current_settings['sharpness'])
        self.contrast_spinbox.setValue(self.current_settings['contrast'])
        self.saturation_spinbox.setValue(self.current_settings['saturation'])
        self.iso_combobox.setCurrentIndex(self.current_settings['iso'])
        _dir = Path(self.current_settings['directory'])
        _dir_str = Path('..', _dir.parent.name, _dir.stem)
        self.pic_dir_line_edit.setText(f"{_dir_str}")
        self.pic_name_line_edit.setText(self.current_settings['filename']),
        self.pic_format_combobox.setCurrentIndex(self.current_settings['pic_format'])
