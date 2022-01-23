import json
import logging
import time
from datetime import datetime
from pathlib import Path

from PyQt5 import QtWidgets, uic, QtCore, QtGui
from picamera import PiCamera


# TODO: QSettings benutzen um root -> XOFFSET,YOFFSET und user -> XOFFSET,YOFFSET zu speichern?
# TODO: Fix setting directory for cam picture
# TODO: Set Tooltips for all elements (at least for quality)

class WorkerThread(QtCore.QThread):
    TIMESTAMP = QtCore.pyqtSignal(str)

    def __init__(self, obj):
        # TODO: send data to worker thread through signal, slot not through __init__
        super().__init__()
        self.cam = obj.cam
        self.file_path = Path(obj.pic_path, obj.pic_name)
        self.suffix = obj.pic_suffix
        self.quality = obj.quality

    def run(self):
        # TODO: Replace with QTimer instead of sleep()?
        #  https://doc.qt.io/qtforpython-5/overviews/timers.html#timers
        time.sleep(5)
        timestamp = datetime.now().strftime('%Y_%m_%dT%H_%M_%S')
        if self.suffix == 'jpeg':
            print('JPEG call')
            self.cam.capture(f'{self.file_path}_{timestamp}.{self.suffix}', quality=self.quality)
        else:
            print('Not JPEG call')
            self.cam.capture(f'{self.file_path}_{timestamp}.{self.suffix}')
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
    RESIZED = QtCore.pyqtSignal()
    FILE_DELETED = QtCore.pyqtSignal()
    PREVIEW_POS = (0, 0, 0, 0)
    X_OFFSET = 0
    Y_OFFSET = 0

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
                                 'quality': 75}
        with open(Path(self.paths['profiles'], 'default.json'), 'w') as f_default:
            json.dump(self.default_settings, f_default)

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
        self.preview_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence('space'), self)
        self.preview_shortcut.activated.connect(self.take_pic)

        self.take_pic_button = self.findChild(QtWidgets.QPushButton, 'pic_button')
        self.load_pic_button = self.findChild(QtWidgets.QPushButton, 'load_pic_button')
        self.reset_button = self.findChild(QtWidgets.QPushButton, 'reset_button')

        # camera push buttons connections
        self.preview_button.clicked.connect(self.preview)
        self.take_pic_button.clicked.connect(self.take_pic)
        self.load_pic_button.clicked.connect(self.load_pic)
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

        # set status bar
        self.full_path = Path(self.paths['pictures'], f'{self.pic_name_line_edit.text()}_{{timestamp}}.'
                                                      f'{self.pic_format_combobox.currentText()}')
        self.pic_dir_line_edit.setStatusTip(f'{self.full_path.parent}')
        self.pic_name_line_edit.setStatusTip(f'{self.full_path}')

        self.take_pic_button.setStatusTip(f'{self.full_path}')

        # set status bar connections
        self.pic_format_combobox.currentIndexChanged.connect(self.set_statusbar)
        self.pic_dir_line_edit.textEdited.connect(self.set_statusbar)
        self.pic_name_line_edit.textEdited.connect(self.set_statusbar)

        # picture buttons connections
        self.pic_format_combobox.currentIndexChanged.connect(self.toggle_quality)
        self.pic_dir_button.clicked.connect(self.open_directory)

        # Window Events
        self.RESIZED.connect(self.resize_window)
        self.installEventFilter(self)
        self.FILE_DELETED.connect(self.set_profile_combobox)

        # set UI
        self.start_preview()
        self.set_profile_combobox()

        # Take Picture Events
        self.pic_name = 'foo'
        self.pic_suffix = 'jpeg'
        self.pic_path = Path(self.paths['pictures'])
        self.timestamp = ''
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

    def open_directory(self):
        home_path = str(self.paths['pictures'])
        self.open_directory_dialog.setDirectory(home_path)
        self.open_directory_dialog.open()
        self.open_directory_dialog.finished.connect(self.set_path)

    def set_path(self, value):
        print(value)
        if value == 1:
            path = self.open_directory_dialog.selectedFiles()
            self.pic_path = self.paths['pictures'] = Path(path[0])
            string = f"{Path('..', self.paths['pictures'].parent.name, self.paths['pictures'].stem)}"
            self.pic_dir_line_edit.setText(string)
            self.set_statusbar()
        if value == 0:
            return

    def set_statusbar(self):
        self.full_path = Path(self.paths['pictures'], f'{self.pic_name_line_edit.text()}_{{timestamp}}.'
                                                      f'{self.pic_format_combobox.currentText()}')
        self.pic_dir_line_edit.setStatusTip(f'{self.full_path.parent}')
        self.pic_name_line_edit.setStatusTip(f'{self.full_path}')
        self.take_pic_button.setStatusTip(f'{self.full_path}')

    def save_profile(self):

        self.current_settings = {'brightness': self.brightness_spinbox.value(),
                                 'sharpness': self.sharpness_spinbox.value(),
                                 'contrast': self.contrast_spinbox.value(),
                                 'saturation': self.saturation_spinbox.value(),
                                 'iso': self.iso_combobox.currentIndex(),
                                 'directory': self.pic_dir_line_edit.text(),
                                 'filename': self.pic_name_line_edit.text(),
                                 'suffix': self.pic_format_combobox.currentIndex()}
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
            self.preview_button.setChecked(False)
        if a1.type() == QtCore.QEvent.WindowStateChange:
            self.cam.stop_preview()
            self.preview_button.setChecked(False)
        return False

    def move_preview_x(self, value):
        if self.cam.preview:
            self.X_OFFSET = value
            preview_pos = (self.PREVIEW_POS[0] + value,
                           self.PREVIEW_POS[1],
                           self.PREVIEW_POS[2],
                           self.PREVIEW_POS[3])
            self.cam.preview.window = preview_pos
        else:
            self.X_OFFSET = 0
            self.x_offset_slider.setValue(0)

    def move_preview_y(self, value):
        if self.cam.preview:
            self.Y_OFFSET = value
            preview_pos = (self.PREVIEW_POS[0],
                           self.PREVIEW_POS[1] + value,
                           self.PREVIEW_POS[2],
                           self.PREVIEW_POS[3])
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
        self.PREVIEW_POS = (self.preview_frame.pos().x() + self.X_OFFSET,
                            self.preview_frame.pos().y() + 90 + self.Y_OFFSET,
                            self.preview_frame.frameGeometry().width(),
                            self.preview_frame.frameGeometry().height())
        if self.preview_button.isChecked():
            self.start_preview()
        else:
            self.stop_preview()

    def start_preview(self):
        self.x_offset_slider.setValue(self.X_OFFSET)
        self.y_offset_slider.setValue(self.Y_OFFSET)
        self.cam.start_preview(fullscreen=False, window=self.PREVIEW_POS)

    def stop_preview(self):
        # TODO: Remember X-OFFSET and Y-OFFSET and use it for next start_preview call
        # self.x_offset_slider.setValue(0)
        # self.y_offset_slider.setValue(0)
        self.cam.stop_preview()

    def take_pic(self):

        self.groupbox_settings.setDisabled(True)
        self.pic_name = self.pic_name_line_edit.text()  # TODO: change to grab full path
        self.pic_suffix = self.pic_format_combobox.currentText()

        if not self.pic_name:
            self.pic_name = 'foo'

        self.take_pic_button.setDisabled(True)
        self.worker.start()
        self.worker.finished.connect(self.evt_worker_finished)

    def set_timestamp(self, timestamp):
        self.timestamp = timestamp

    def evt_worker_finished(self):
        self.groupbox_settings.setDisabled(False)
        self.take_pic_button.setDisabled(False)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        self.RESIZED.emit()
        # Possible way to be able to resize window
        super(UI, self).resizeEvent(event)

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
        self.quality_spinbox.setValue(self.default_settings['quality'])

    def set_values(self):
        self.brightness_spinbox.setValue(self.current_settings['brightness'])
        self.sharpness_spinbox.setValue(self.current_settings['sharpness'])
        self.contrast_spinbox.setValue(self.current_settings['contrast'])
        self.saturation_spinbox.setValue(self.current_settings['saturation'])
        self.iso_combobox.setCurrentIndex(self.current_settings['iso'])
        self.pic_dir_line_edit.setText(self.current_settings['directory']),
        self.pic_name_line_edit.setText(self.current_settings['filename']),
        self.pic_format_combobox.currentIndex(self.current_settings['suffix'])
