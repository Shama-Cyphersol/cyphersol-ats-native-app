import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from PyQt6 import QtGui
import os

if os.name == 'nt':
    import ctypes
    myappid = 'mycompany.myproduct.subproduct.version'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('assets/icon.png'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
