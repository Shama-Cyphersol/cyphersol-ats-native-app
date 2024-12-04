import sys
import argparse
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.ui.license_dialog import LicenseDialog
from src.ui.login_dialog import LoginDialog
from src.core.repository import *
from PyQt6 import QtGui
import os
from src.core.session_manager import SessionManager
from src.core.license_manager import LicenseManager

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
    
    license_key = LicenseManager.get_license_key()

    user_info = {}

    if not license_key:
        # Show license verification dialog
        license_dialog = LicenseDialog(test_mode=args.test)
        license_key = license_dialog.license_key_input.text()

        print(f"License Key: {license_key}")


        if license_dialog.exec() != LicenseDialog.DialogCode.Accepted:
            print("License verification failed or cancelled.")
            sys.exit(1)
        else:
            print("License verification successful.")
            # save the user data to the database
            user_info = license_dialog.user_info
            LicenseManager.store_license_key(license_key=user_info.get("license_key"))
            user_repository = UserRepository()
            user = user_repository.get_user_by_username(user_info.get("username"))
            if not user:
                user_info = user_repository.create_user(user_info)
    else:
        login_dialog = LoginDialog(test_mode=args.test)

        if login_dialog.exec() != LoginDialog.DialogCode.Accepted:
            sys.exit(1)
            print("Login failed or cancelled.")
        else:
            username = login_dialog.username_input.text()
            password = login_dialog.password_input.text()

    SessionManager.login_user(user)

    # Only show main window if license is verified
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
