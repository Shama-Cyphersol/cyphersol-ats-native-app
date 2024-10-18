# Filename: user_management.py

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QFrame
)
from PyQt6.QtCore import Qt
from apps.report.views import ReportsApp
# src/apps/user_management/views.py
from PyQt6.QtWidgets import QApplication, QWidget, QFrame, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QDialog, QFormLayout, QLineEdit, QPushButton, QLabel, QVBoxLayout, QMessageBox
from PyQt6.QtCore import Qt


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setFixedSize(600, 400)  # Match size with other pages
        self.setStyleSheet("background-color: #f5f5f5;")  # Light gray background

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center layout

        # Title Label
        title_label = QLabel("Please Login")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: black;")  # Set text color to black
        layout.addWidget(title_label)

        # Username Input
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet("padding: 10px; font-size: 18px; border: 1px solid #ccc; border-radius: 5px; color: black;")  # Set text color to black
        layout.addWidget(self.username_input)

        # Password Input
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("padding: 10px; font-size: 18px; border: 1px solid #ccc; border-radius: 5px; color: black;")  # Set text color to black
        layout.addWidget(self.password_input)

        # Create a horizontal layout for the button
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the button horizontally

        # Login Button
        self.login_button = QPushButton("Login", self)
        self.login_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border: none; border-radius: 5px; font-size: 18px;")
        self.login_button.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Allow focus on button with Tab
        self.login_button.clicked.connect(self.handle_login)
        button_layout.addWidget(self.login_button)  # Add the button to the horizontal layout

        layout.addLayout(button_layout)  # Add the button layout to the main layout

        # Add a spacer to push elements to the center
        layout.addStretch()

        self.setLayout(layout)

        # Set the tab order to navigate correctly
        self.setTabOrder(self.username_input, self.password_input)  # Tab from username to password
        self.setTabOrder(self.password_input, self.login_button)     # Tab from password to login button

    def handle_login(self):
        # Bypass authentication
        self.accept()  # Close dialog and return success to show the main app




class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard")
        layout = QVBoxLayout()

        # Dashboard Title
        title_label = QLabel("Dashboard Overview")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")  # Title styling
        layout.addWidget(title_label)

        # Sample Content
        sample_label = QLabel("Here you can see an overview of user activities.")
        sample_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sample_label.setStyleSheet("font-size: 16px; color: #555;")  # Content styling
        layout.addWidget(sample_label)

        # Additional Button for demonstration
        button_info = QPushButton("View More Information")
        button_info.clicked.connect(self.view_more_info)
        layout.addWidget(button_info)

        # Set layout
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center layout
        self.setLayout(layout)

    def view_more_info(self):
        print("Viewing more information...")
        # Logic to display more information can be added here