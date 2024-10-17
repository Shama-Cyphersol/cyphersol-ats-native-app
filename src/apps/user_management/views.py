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