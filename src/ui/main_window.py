from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt,QSize
from .dashboard import DashboardTab
from .report_generator import ReportGeneratorTab
from .settings import SettingsTab
from .reports import ReportsTab
from .name_manager import NameManagerTab
import pandas as pd
from core.db import Database
from sqlalchemy.sql import text  # Import the text function


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CypherSol")
        self.initialize_database()
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
                           
            QMainWindow {
                background-color: #f0f0f0;
            }
                           
            QPushButton {
                background-color: #ffffff;
                color: #2c3e50;
                border: none;  
                padding: 12px 20px;
                text-align: left;
                font-size: 16px;
                margin: 2px 10px;
                outline: none;
                border-left: 3px solid transparent;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                color: #3498db;
            }
            QPushButton:checked {
                background-color: #f0f7ff;
                color: #3498db;
                border-left: 3px solid #3498db;
            }
        
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        # Show the window maximized
        self.showMaximized()

        # Set window flags to allow minimizing and closing
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint)

        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Add footer label
        footer_label = QLabel("© Copyright 2024 CypherSOL Fintech India Pvt Ltd.\nAll Rights Reserved")
        footer_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 11px;
                padding: 20px;
                qproperty-alignment: AlignCenter;
            }
        """)
        footer_label.setWordWrap(True)

        # Sidebar
        sidebar = QWidget()
        sidebar.setStyleSheet("""
            QWidget {
                background-color: white;
            }
        """)
        sidebar.setFixedWidth(300)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(0)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)

        # Cyphersol Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/logo.png")
        scaled_pixmap = logo_pixmap.scaled(200, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setContentsMargins(0, 10, 0, 45)
        sidebar_layout.addWidget(logo_label)

        # Navigation buttons
        self.nav_buttons = []
        button_icons = [
            ("Dashboard", "dashboard.png"),
            ("Generate Report", "generate_report.png"),
            ("Reports", "generate_report.png"),
            ("Name Manager", "generate_report.png"),
            ("Settings", "settings.png"),
            ("Logout", "settings.png"),
        ]

        for text, icon in button_icons:
            btn = QPushButton(" " * 2 +text)
            btn.setIcon(QIcon(f"assets/{icon}"))
            btn.setIconSize(QSize(23, 23))  # Make icons slightly larger
            btn.setCheckable(True)
            btn.setChecked(text == "Dashboard")
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        sidebar_layout.addWidget(footer_label)

        main_layout.addWidget(sidebar)

        # Content area with updated background
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f8f9fa;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)

        self.content_area = QStackedWidget()
        self.content_area.addWidget(DashboardTab())
        self.content_area.addWidget(ReportGeneratorTab())
        self.content_area.addWidget(ReportsTab())
        self.content_area.addWidget(NameManagerTab())
        self.content_area.addWidget(SettingsTab())
        # self.content_area.addWidget(CashFlowNetwork(data=dummy_data_for_network_graph))

        content_layout.addWidget(self.content_area)
        main_layout.addWidget(content_widget)

        # Connect buttons
        for i, btn in enumerate(self.nav_buttons):
            btn.clicked.connect(lambda checked, index=i: self.switch_page(index))

    def initialize_database(self):
        """Initial method to set up or validate the database connection"""
        try:
            db = Database.get_session()
            # Use text() to wrap the raw SQL query
            result = db.execute(text("SELECT datetime('now');")).fetchone()
            if result:
                print("Database connection established successfully.")
            else:
                print("Failed to retrieve data from the database.")
            db.close()  # Always close the session after use
        except Exception as e:
            print(f"Error initializing database: {e}")

    def switch_page(self, index):
        self.content_area.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

 