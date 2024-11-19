
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QGraphicsDropShadowEffect, QScrollArea, QDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from .case_dashboard import CaseDashboard
from utils.json_logic import load_all_case_data


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
