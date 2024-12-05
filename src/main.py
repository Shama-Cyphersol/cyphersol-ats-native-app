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

    if SessionManager.is_logged_in():
        user = SessionManager.get_current_user()
        print(f"Restored session for user: {user['username']}")
    else:
        license_key = LicenseManager.get_license_key()
        print(f"License Key present or not: {license_key}", type(license_key))
        user = {}

        if not license_key:
            print("License key not found. Showing license dialog...")
            license_dialog = LicenseDialog(test_mode=args.test)
            if license_dialog.exec() != LicenseDialog.DialogCode.Accepted:
                print("License verification failed or cancelled.")
                sys.exit(1)

            # Retrieve and store the license key
            license_key = license_dialog.license_key_input.text()
            print(f"License Key: {license_key}")
            LicenseManager.store_license_key(license_key=license_key)

            # Get or create user info based on license dialog
            user_info = license_dialog.user_info
            user_repository = UserRepository()
            user = user_repository.get_user_by_username(user_info.get("username"))

            if not user:
                user = user_repository.create_user(user_info)
        else:
            # Show login dialog for the user
            login_dialog = LoginDialog(test_mode=args.test)
            if login_dialog.exec() != LoginDialog.DialogCode.Accepted:
                print("Login failed or cancelled.")
                sys.exit(1)

            user = login_dialog.user

        SessionManager.login_user(user)

    # Only show main window if license is verified
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
