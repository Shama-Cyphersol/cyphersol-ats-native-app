from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from ..core.session_manager import SessionManager

class LoginDialog(QDialog):
    class DialogCode:
        Accepted = QDialog.DialogCode.Accepted
        Rejected = QDialog.DialogCode.Rejected

    def __init__(self, test_mode=False, parent=None):
        super().__init__(parent)
        self.test_mode = test_mode
        self.setWindowTitle("Login")
        self.resize(300, 150)
        self.user = None

        self.layout = QVBoxLayout(self)

        # Add widgets
        self.error_label = QLabel("", self)  # Error label to show login failures
        self.error_label.setStyleSheet("color: red;")
        self.layout.addWidget(self.error_label)

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Username")
        self.layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login", self)
        self.login_button.clicked.connect(self.validate_login)
        self.layout.addWidget(self.login_button)

        if self.test_mode:
            self.username_input.setText("1-bd7c6c56")
            self.password_input.setText("password")

    def validate_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        user =  SessionManager.authenticate_user(username, password)
        if user:
            print("User authenticated successfully!")
            self.user = user
            self.accept()
        else:
            self.error_label.setText("Invalid username or password. Please try again.")
