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
from PyQt6.QtWidgets import QApplication, QWidget, QFrame, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QStackedWidget, QDialog, QFormLayout, QLineEdit, QPushButton, QLabel, QVBoxLayout, QMessageBox, QTableWidget,QHeaderView,QTableWidgetItem,QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from .controllers import *
from PyQt6.QtGui import QFont, QColor
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
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Dashboard Overview")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)

        # Stats overview
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        self.report_count_widget = self.create_stat_widget("Cases", get_report_count())
        stats_layout.addWidget(self.report_count_widget)

        self.monthly_report_widget = self.create_stat_widget("Pending Cases", get_monthly_report_count())
        stats_layout.addWidget(self.monthly_report_widget)

        self.active_users_widget = self.create_stat_widget("Closed Cases", 42)  # Dummy data
        stats_layout.addWidget(self.active_users_widget)

        layout.addLayout(stats_layout)

        # Recent Reports Table
        layout.addWidget(self.create_section_title("Recent Reports"))
        layout.addWidget(self.create_recent_reports_table())

        # Monthly Trend Chart (placeholder)
        layout.addWidget(self.create_section_title("Monthly Report Trend"))
        layout.addWidget(self.create_placeholder_chart())

        self.setLayout(layout)

    def create_stat_widget(self, label, value):
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        layout = QVBoxLayout(widget)
        
        value_label = QLabel(str(value))
        value_label.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("color: #3498db;")
        
        desc_label = QLabel(label)
        desc_label.setFont(QFont("Arial", 14))
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("color: #7f8c8d;")
        
        layout.addWidget(value_label)
        layout.addWidget(desc_label)
        
        self.add_shadow(widget)
        return widget

    def create_section_title(self, title):
        label = QLabel(title)
        label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        label.setStyleSheet("color: #2c3e50; margin-top: 20px;")
        return label

    def create_recent_reports_table(self):
        table = QTableWidget(5, 3)
        table.setHorizontalHeaderLabels(["Case ID","Date", "Report Name"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 10px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border: none;
                padding: 8px;
            }
        """)

        recent_reports = get_recent_reports()
        for row, report in enumerate(recent_reports):
            table.setItem(row, 0, QTableWidgetItem(str(report['id'])))
            table.setItem(row, 1, QTableWidgetItem(report['date']))
            table.setItem(row, 2, QTableWidgetItem(report['name']))
            # table.setItem(row, 2, QTableWidgetItem(report['status']))

        self.add_shadow(table)
        return table

    def create_placeholder_chart(self):
        chart = QLabel("Monthly Trend Chart Placeholder")
        chart.setStyleSheet("""
            background-color: white;
            border-radius: 10px;
            padding: 40px;
            font-size: 18px;
            color: #7f8c8d;
        """)
        chart.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_shadow(chart)
        return chart

    def add_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 0)
        widget.setGraphicsEffect(shadow)

    def update_stats(self):
        self.report_count_widget.findChild(QLabel).setText(str(get_report_count()))
        self.monthly_report_widget.findChild(QLabel).setText(str(get_monthly_report_count()))
        # Update other stats and table data as needed


    def view_more_info(self):
        print("Viewing more information...")
        # Logic to display more information can be added here