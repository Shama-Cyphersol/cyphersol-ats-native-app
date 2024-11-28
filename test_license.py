import sys
import os

# Add the src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

import argparse
from PyQt6.QtWidgets import QApplication
from ui.license_dialog import LicenseDialog
from ui.main_window import MainWindow
from PyQt6 import QtGui

if os.name == 'nt':
    import ctypes
    myappid = 'mycompany.myproduct.subproduct.version'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

def main():
    parser = argparse.ArgumentParser(description='License Verification Tool')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    args = parser.parse_args()
    
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('assets/icon.png'))
    
    # Create and show the license dialog
    dialog = LicenseDialog(test_mode=args.test)
    if dialog.exec() != LicenseDialog.DialogCode.Accepted:
        sys.exit(1)
        
    # Show main window after successful verification
    window = MainWindow()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
