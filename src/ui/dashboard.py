from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame,
                             QTableWidget, QTableWidgetItem,QDialog, QHeaderView, QGraphicsDropShadowEffect)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
from modules.dashboard_stats import get_report_count, get_recent_reports, get_monthly_report_count
from .case_dashboard import CaseDashboard
from utils.json_logic import *

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

        self.active_users_widget = self.create_stat_widget("Example", 42)  # Dummy data
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
            
        # Create the table widget with 3 columns
        if not hasattr(self, 'table'):

            self.table = QTableWidget()
            self.table.setColumnCount(4)
            self.table.verticalHeader().setVisible(False)

            self.table.setHorizontalHeaderLabels(["Sr no.","Date","Case ID", "Report Name"])
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.table.setStyleSheet("""
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
                QCheckBox {
                    margin-left: 5px;
                }
                QTableWidget::setItem {
                    text-align: center;  /* Center text in cells */
                }
                QTableWidget::item {
                    color: black;
                    padding: 5px;
                }
            """)
            self.table.cellClicked.connect(self.case_id_clicked)

        recent_reports = load_all_case_data()
        self.table.setRowCount(len(recent_reports))
        # Populate the table with data
        for row, report in enumerate(recent_reports):

            # Serial Number column
            serial_number_item = QTableWidgetItem(str(row + 1))
            serial_number_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            serial_number_item.setFlags(serial_number_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, serial_number_item)

            # Date column
            date_item = QTableWidgetItem(report['date'])
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            date_item.setFlags(date_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, date_item)

            # Case ID column
            case_id_item = QTableWidgetItem(str(report['case_id']))
            case_id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            case_id_item.setFlags(case_id_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, case_id_item)

            # Report Name column
            report_name_item = QTableWidgetItem(report['report_name'])
            report_name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            report_name_item.setFlags(report_name_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 3, report_name_item)

        return self.table
    
        
    def case_id_clicked(self, row, column):
        # if column == 2:
        case_id = self.table.item(row, 2).text() # getting 2nd col as it contains the case_id
        print("Case ID clicked: ", case_id)
        cash_flow_network = CaseDashboard(case_id=case_id)
            # Create a new dialog and set the CashFlowNetwork widget as its central widget
        self.new_window = QDialog(self)
        self.new_window.setWindowTitle(f"Case Dashboard - Case {case_id}")
        self.new_window.setModal(False)  # Set the dialog as non-modal
        self.new_window.showMaximized()
        self.new_window.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint)
        self.new_window.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint)
        self.new_window.setWindowFlag(Qt.WindowType.WindowCloseButtonHint)

        # Set the minimum size of the dialog
        self.new_window.setMinimumSize(1000, 800)  # Set the minimum width and height

        # Create a layout for the dialog and add the CashFlowNetwork widget
        layout = QVBoxLayout()
        layout.addWidget(cash_flow_network)
        self.new_window.setLayout(layout)

        # Show the new window
        self.new_window.show()

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