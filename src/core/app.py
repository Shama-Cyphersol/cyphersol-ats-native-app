from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QWidget
from apps.user_management.views import UserManagementApp
from apps.report.views import ReportsApp

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CypherSol")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # Initialize and add apps
        self.user_management_app = UserManagementApp()
        self.reports_app = ReportsApp()

        self.central_widget.addWidget(self.user_management_app)
        self.central_widget.addWidget(self.reports_app)

        # Start with the User Management app
        self.central_widget.setCurrentWidget(self.user_management_app)