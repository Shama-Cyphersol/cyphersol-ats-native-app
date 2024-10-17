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
from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QLabel, QVBoxLayout, QMessageBox
from PyQt6.QtCore import Qt


class UserManagementApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User Management")
        self.setFixedSize(800, 600)  # Set fixed size for the app

        # Main layout
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Sidebar Navigation
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(200)  # Fixed width for the sidebar
        self.sidebar.setStyleSheet("background-color: #1e1e1e;")  # Dark background for sidebar

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align items to the top

        # Dashboard Button
        button_dashboard = QPushButton("Dashboard")
        button_dashboard.clicked.connect(self.show_dashboard)
        button_dashboard.setStyleSheet(self.button_style())
        sidebar_layout.addWidget(button_dashboard)

        # Generate Report Button
        button_report = QPushButton("Generate Report")
        button_report.clicked.connect(self.show_report)
        button_report.setStyleSheet(self.button_style())
        sidebar_layout.addWidget(button_report)

        self.sidebar.setLayout(sidebar_layout)
        main_layout.addWidget(self.sidebar)

        # Main Content Area
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane { 
                border: 1px solid #ccc; 
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #e0e0e0; 
                padding: 12px;
                font-size: 16px; 
                border: 1px solid #ccc; 
                border-bottom: none;
                border-radius: 5px 5px 0 0;  /* Rounded top corners */
            }
            QTabBar::tab:selected {
                background: #ffffff; 
                font-weight: bold; 
                color: #4CAF50; 
            }
            QTabBar::tab:hover {
                background: #d0d0d0;  /* Hover effect */
            }
        """)

        self.dashboard_widget = self.create_dashboard()
        self.report_widget = self.create_report()

        self.tab_widget.addTab(self.dashboard_widget, "Dashboard")
        self.tab_widget.addTab(self.report_widget, "Generate Report")

        main_layout.addWidget(self.tab_widget)

    def button_style(self):
        return """
            QPushButton {
                color: white;
                background-color: transparent;
                padding: 10px;
                font-size: 18px;
                border: none;
            }
            QPushButton:hover {
                background-color: #4CAF50;  /* Hover effect */
                border-radius: 5px;
            }
        """

    def create_dashboard(self):
        dashboard_widget = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Welcome to the Dashboard")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 20px; color: #333;")  # Label styling
        layout.addWidget(label)

        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center layout
        dashboard_widget.setLayout(layout)
        return dashboard_widget

    def create_report(self):
        report_widget = ReportsApp()  # Use the updated ReportsApp
        return report_widget

    def show_dashboard(self):
        self.tab_widget.setCurrentIndex(0)  # Switch to Dashboard tab

    def show_report(self):
        self.tab_widget.setCurrentIndex(1)  # Switch to Report tab


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