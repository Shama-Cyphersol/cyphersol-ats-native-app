from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame,
                             QTableWidget, QTableWidgetItem, QHeaderView, QGraphicsDropShadowEffect)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
from modules.dashboard_stats import get_report_count, get_recent_reports, get_monthly_report_count

class DashboardTab(QWidget):
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

        self.report_count_widget = self.create_stat_widget("Total Reports", get_report_count())
        stats_layout.addWidget(self.report_count_widget)

        self.monthly_report_widget = self.create_stat_widget("Monthly Reports", get_monthly_report_count())
        stats_layout.addWidget(self.monthly_report_widget)

        self.active_users_widget = self.create_stat_widget("Active Users", 42)  # Dummy data
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
        table.setHorizontalHeaderLabels(["Date", "Report Name", "Status"])
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
            table.setItem(row, 0, QTableWidgetItem(report['date']))
            table.setItem(row, 1, QTableWidgetItem(report['name']))
            table.setItem(row, 2, QTableWidgetItem(report['status']))

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