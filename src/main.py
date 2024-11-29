import sys
import argparse
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.ui.license_dialog import LicenseDialog
from PyQt6 import QtGui
import os

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # Get parent of src directory
sys.path.insert(0, parent_dir)


if os.name == 'nt':
    import ctypes
    myappid = 'mycompany.myproduct.subproduct.version'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Cyphersol ATS Application')
    parser.add_argument('--test', action='store_true', help='Run in test mode with pre-filled license credentials')
    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(os.path.join(parent_dir, 'assets/icon.png')))
    
    # Show license verification dialog
    # license_dialog = LicenseDialog(test_mode=args.test)
    # if license_dialog.exec() != LicenseDialog.DialogCode.Accepted:
    #     print("License verification failed or cancelled.")
    #     sys.exit(1)
    
    # Only show main window if license is verified
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
