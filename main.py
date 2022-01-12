from PyQt5 import QtWidgets
from main_window_cleaned import UiMainWindow

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    main_window = QtWidgets.QMainWindow()
    ui = UiMainWindow(main_window)
    ui.setup_ui()
    main_window.show()
    sys.exit(app.exec_())
