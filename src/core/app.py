from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QWidget
# from apps.user_management.views import UserManagementApp
from apps.report.views import ReportsApp
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QFrame, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QDialog, QFormLayout, QLineEdit, QPushButton, QLabel, QVBoxLayout
from apps.user_management.views import DashboardView


class UserInterface(QWidget):
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
        button_report = QPushButton("Show Reports")
        button_report.clicked.connect(self.show_reports)  # Changed connection
        button_report.setStyleSheet(self.button_style())
        sidebar_layout.addWidget(button_report)

        self.sidebar.setLayout(sidebar_layout)
        main_layout.addWidget(self.sidebar)

        # Main Content Area
        self.main_content = QStackedWidget()  # Use StackedWidget to switch views
        self.dashboard_widget = DashboardView()  # Use the new DashboardView
        self.report_widget = ReportsApp()  # Use the ReportsApp directly

        self.main_content.addWidget(self.dashboard_widget)  # Add DashboardView to the stack
        self.main_content.addWidget(self.report_widget)  # Add ReportsApp to the stack

        main_layout.addWidget(self.main_content)

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

    def show_dashboard(self):
        self.main_content.setCurrentIndex(0)  # Switch to Dashboard

    def show_reports(self):
        self.main_content.setCurrentIndex(1)  # Show ReportsApp


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CypherSol")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # Initialize and add apps
        self.user_management_app = UserInterface()
        # self.reports_app = ReportsApp()

        self.central_widget.addWidget(self.user_management_app)
        # self.central_widget.addWidget(self.reports_app)

        # Start with the User Management app
        self.central_widget.setCurrentWidget(self.user_management_app)