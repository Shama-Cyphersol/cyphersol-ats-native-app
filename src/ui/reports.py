from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QDialog, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from .case_dashboard import CaseDashboard
from utils.json_logic import load_all_case_data, load_case_data

class IndividualsDialog(QDialog):
    def __init__(self, case_id, parent=None):
        super().__init__(parent)
        self.case_id = case_id
        self.init_ui()

    def init_ui(self):
        # Set up dialog properties
        self.setWindowTitle(f"Individuals in Case {self.case_id}")
        self.setMinimumSize(800, 600)

        # Main layout
        layout = QVBoxLayout()

        # Title
        title = QLabel(f"Individuals in Case {self.case_id}")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)

        # Create table for individuals
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Sr no.", "Individual Name", "Account Number"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        
        # Style the table
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
        """)

        # Load case data
        case_data = load_case_data(self.case_id)
        names = case_data['individual_names']['Name']
        acc_numbers = case_data['individual_names']['Acc Number']
        
        # Set row count
        self.table.setRowCount(len(names))

        for row in range(len(names)):
            # Serial Number
            serial_number = QTableWidgetItem(str(row + 1))
            serial_number.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            serial_number.setFlags(serial_number.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, serial_number)

            # Individual Name
            name_item = QTableWidgetItem(names[row])
            print(names[row])
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            name_item.setFlags(name_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, name_item)

            # Account Number
            acc_item = QTableWidgetItem(str(acc_numbers[row]))
            acc_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            acc_item.setFlags(acc_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, acc_item)

        self.table.setStyleSheet("color: black;")
        layout.addWidget(self.table)
        self.setLayout(layout)

class ReportsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Reports Overview")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        layout.addWidget(self.create_recent_reports_table())
        self.setLayout(layout)

    def create_recent_reports_table(self):
        # Create the table widget with 4 columns
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.verticalHeader().setVisible(False)

        self.table.setHorizontalHeaderLabels(["Sr no.", "Date", "Case ID", "Report Name"])
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
            QTableWidget::item {
                text-align: center;
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
        # Get the case ID when a case is clicked
        case_id = self.table.item(row, 2).text()
        
        # Open a new dialog with individuals for this case
        individuals_dialog = IndividualsDialog(case_id, parent=self)
        individuals_dialog.exec()