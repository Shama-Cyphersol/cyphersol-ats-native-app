from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel,QFrame
from PyQt6.QtGui import QPixmap
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt,QSize
from .dashboard import DashboardTab
from .report_generator import ReportGeneratorTab
from .settings import SettingsTab
from .reports import ReportsTab
from .name_manager import NameManagerTab
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup
import pandas as pd
from core.db import Database
from sqlalchemy.sql import text  # Import the text function

class AnimatedToggle(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def enterEvent(self, event):
        QPropertyAnimation(self, b"maximumWidth", startValue=self.width(), endValue=self.width() + 10, duration=200).start()

    def leaveEvent(self, event):
        QPropertyAnimation(self, b"maximumWidth", startValue=self.width(), endValue=self.width() - 10, duration=200).start()

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
                color: #252525;
                font-weight: 400;
                border: none;  
                padding: 12px 20px;
                text-align: left;
                font-size: 18px;
                margin: 2px 10px;
                outline: none;
                border-left: 3px solid transparent;
                border-radius: 5px;
     
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                color: #3498db;

            }
            QPushButton:checked {
                background-color: #e0e7ff;
                color: #3498db;
                border-left: 3px solid #3498db;
            }
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        # Show the window maximized

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
        # Enhanced Sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setStyleSheet("""
            #sidebar {
                background-color: white;
                border-right: 1px solid #e0e0e0;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.sidebar.setFixedWidth(300)
        sidebar_layout = QVBoxLayout(self.sidebar)
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
            ("Reports", "report.png"),
            ("Name Manager", "name_manager.png"),
            ("Settings", "settings.png"),
            ("Logout", "logout.png"),
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

        main_layout.addWidget(self.sidebar)

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
        
        self.showMaximized()


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
        # Create a parallel animation group for simultaneous animations
        anim_group = QParallelAnimationGroup()

        # Fade out current widget
        fade_out = QPropertyAnimation(self.content_area.currentWidget(), b"windowOpacity")
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setDuration(200)
        fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim_group.addAnimation(fade_out)

        # Switch to the new page
        self.content_area.setCurrentIndex(index)

        # Fade in new widget
        fade_in = QPropertyAnimation(self.content_area.currentWidget(), b"windowOpacity")
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setDuration(200)
        fade_in.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim_group.addAnimation(fade_in)

        # Start the animation group
        anim_group.start()

        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

        # Sidebar highlight animation
        highlight = QPropertyAnimation(self.nav_buttons[index], b"maximumWidth")
        highlight.setStartValue(self.nav_buttons[index].width())
        highlight.setEndValue(self.nav_buttons[index].width() + 20)
        highlight.setDuration(300)
        highlight.setEasingCurve(QEasingCurve.Type.OutElastic)
        highlight.start()

 