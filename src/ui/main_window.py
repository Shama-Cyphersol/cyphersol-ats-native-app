from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt
from .dashboard import DashboardTab
from .file_opener import FileOpenerTab
from .report_generator import ReportGeneratorTab
from .settings import SettingsTab

class MainWindow(QMainWindow):
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
            ("File Opener", "file.png"),
            ("Generate Report", "report.png"),
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
        self.content_area.addWidget(DashboardTab())
        self.content_area.addWidget(FileOpenerTab())
        self.content_area.addWidget(ReportGeneratorTab())
        self.content_area.addWidget(SettingsTab())
        content_layout.addWidget(self.content_area)

        main_layout.addWidget(content_widget)

        # Connect buttons to switch pages
        for i, btn in enumerate(self.nav_buttons):
            btn.clicked.connect(lambda checked, index=i: self.switch_page(index))

    def switch_page(self, index):
        self.content_area.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
