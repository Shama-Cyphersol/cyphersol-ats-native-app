from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QVBoxLayout, QWidget
# from apps.user_management.views import UserManagementApp
from apps.report.views import ReportsApp, FileOpenerTab
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QFrame, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QDialog, QFormLayout, QLineEdit, QPushButton, QLabel, QVBoxLayout
from apps.user_management.views import DashboardView
from PyQt6.QtGui import QIcon
class UserInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CypherSol")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 20px;
                text-align: left;
                font-size: 18px;
                border-radius: 10px;
                margin: 5px 10px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:checked {
                background-color: #3498db;
            }
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setStyleSheet("background-color: #2c3e50;")
        sidebar.setFixedWidth(300)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(10)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)

        # App title
        app_title = QLabel("CypherSol")
        app_title.setStyleSheet("color: white; font-size: 28px; font-weight: bold; padding: 20px 0;")
        app_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(app_title)

        # Navigation buttons
        self.nav_buttons = []
        for text, icon in [
            ("Dashboard", "dashboard.png"),
            ("Generate Report", "report.png"),
            ("File Opener", "file.png"),
            ("Settings", "settings.png")
        ]:
            btn = QPushButton(text)
            btn.setIcon(QIcon(f"resources/icons/{icon}"))
            btn.setCheckable(True)
            btn.setChecked(text == "Dashboard")
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        # Content area
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f0f0f0;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)

        self.content_area = QStackedWidget()
        self.content_area.addWidget(DashboardView())
        self.content_area.addWidget(ReportsApp())
        self.content_area.addWidget(FileOpenerTab())
        # self.content_area.addWidget(SettingsTab())
        content_layout.addWidget(self.content_area)

        main_layout.addWidget(content_widget)

        # Connect buttons to switch pages
        for i, btn in enumerate(self.nav_buttons):
            btn.clicked.connect(lambda checked, index=i: self.switch_page(index))

    def switch_page(self, index):
        self.content_area.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)


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