# main.py
import sys
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
from core.app import MainApp
from apps.user_management.views import LoginDialog  # Import the login dialog

class MyApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

    def exit_application(self):
        # Optional: Show confirmation dialog on exit
        reply = QMessageBox.question(None, 'Confirm Exit', 'Are you sure you want to exit?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.quit()  # Exits the application

if __name__ == "__main__":
    app = MyApp(sys.argv)

    # Show the login dialog
    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        window = MainApp()
        window.show()

        # Connect the application exit function to the main window close event
        window.closeEvent = lambda event: app.exit_application()

        sys.exit(app.exec())
    else:
        sys.exit()  # Exit if login fails