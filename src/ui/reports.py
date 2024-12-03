import sys
import os
from typing import List, Dict

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, 
    QPushButton, QFileDialog, QMessageBox, QGraphicsDropShadowEffect, QToolButton
)
from PyQt6.QtCore import Qt, QSize, QUrl
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap
from PyQt6.QtWebEngineWidgets import QWebEngineView

from ..utils.json_logic import load_all_case_data, load_case_data



class ModernStyledTableWidget(QTableWidget):
    def __init__(self, columns: List[str], parent=None):
        super().__init__(parent)
        self.setup_ui(columns)

    def setup_ui(self, columns: List[str]):
        # Configure table
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)

        # Modern styling
        self.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 12px;
                alternate-background-color: #f0f4f8;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #34495e;
            }
            QTableWidget::item {
                border-bottom: 1px solid #ecf0f1;
                color: #34495e;
            }
             QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        # Hover and selection effects
        self.setAlternatingRowColors(True)


class ReportsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title with shadow effect
        title = QLabel("Select a Case to download reports")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        
        # Add shadow to title
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 2)
        title.setGraphicsEffect(shadow)
        
        layout.addWidget(title)

        # Create reports table
        self.reports_table = ModernStyledTableWidget([
            "Sr No.", "Date", "Case ID", "Report Name", "Actions"
        ])
        self.populate_reports_table()
        
        # Connect row click
        self.reports_table.cellClicked.connect(self.show_case_individuals)

        layout.addWidget(self.reports_table)
        self.setLayout(layout)

    def populate_reports_table(self):
        recent_reports = load_all_case_data()
        self.reports_table.setRowCount(len(recent_reports))
        
        for row, report in enumerate(recent_reports):
            # Standard columns
            for col, key in enumerate(["Sr No.", "Date", "Case ID", "Report Name"]):
                value = str(row + 1) if key == "Sr No." else report.get(key.lower().replace(" ", "_"), "")
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.reports_table.setItem(row, col, item)
            
            # Action button
            label = QLabel(f'<a href="#">View Details</a>')
            label.setStyleSheet("a { color: #3498db; } a:hover { color: #2980b9; }")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setOpenExternalLinks(False)  # Disable opening links in browser
            label.mousePressEvent = lambda event, r=row: self.show_case_individuals(r,0)  # Attach row click handler
            self.reports_table.setCellWidget(row, 4, label)

    def show_case_individuals(self, row, column):
        case_id = self.reports_table.item(row, 2).text()
        individuals_dialog = IndividualsDialog(case_id, parent=self)
        individuals_dialog.exec()


class IndividualsDialog(QDialog):
    def __init__(self, case_id, parent=None):
        super().__init__(parent)
        self.case_id = case_id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Individuals in Case {self.case_id}")
        self.setMinimumSize(900, 600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout()

        # Header section
        header_layout = QHBoxLayout()
        title = QLabel(f"Case {self.case_id} - Individual Details")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title)
        layout.addLayout(header_layout)

        # Individuals Table
        self.individuals_table = ModernStyledTableWidget([
            "Sr No.", "Individual Name", "Account Number", "Actions"
        ])
        self.populate_individuals_table()
        
        layout.addWidget(self.individuals_table)

        self.setLayout(layout)

    def populate_individuals_table(self):
        case_data = load_case_data(self.case_id)
        names = case_data['individual_names']['Name']
        acc_numbers = case_data['individual_names']['Acc Number']
        
        self.individuals_table.setRowCount(len(names))

        for row in range(len(names)):
            # Serial Number
            serial_item = QTableWidgetItem(str(row + 1))
            serial_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.individuals_table.setItem(row, 0, serial_item)

            # Name
            name_item = QTableWidgetItem(names[row])
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.individuals_table.setItem(row, 1, name_item)

            # Account Number
            acc_item = QTableWidgetItem(str(acc_numbers[row]))
            acc_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.individuals_table.setItem(row, 2, acc_item)

            # Actions Button
            # download_btn = QPushButton("Download Report")
            # download_btn.setStyleSheet("""
            #     QPushButton {
            #         background-color: #2ecc71;
            #         color: white;
            #         border: none;
            #         padding: 5px 10px;
            #         border-radius: 5px;
            #     }
            #     QPushButton:hover {
            #         background-color: #27ae60;
            #     }
            # """)
            # download_btn.clicked.connect(
            #     lambda checked, n=names[row], a=acc_numbers[row]: 
            #     self.download_individual_report(n, a)
            # )
            # self.individuals_table.setCellWidget(row, 4, download_btn)
            label = QLabel(f'<a href="#">Download Report</a>')
            label.setStyleSheet("QLabel { color: #3498db; } QLabel:hover { color: #2980b9; }")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setOpenExternalLinks(False)  # Disable opening links in browser
            label.mousePressEvent = lambda checked, n=names[row], a=acc_numbers[row]:self.download_individual_report(n, a)   # Attach row click handler
            self.individuals_table.setCellWidget(row, 3, label)

    def download_individual_report(self, name, acc_number):
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Individual Report", 
            f"{name}_{acc_number}_report.pdf", 
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(f"Report for {name} (Account: {acc_number})\n")
                
                QMessageBox.information(
                    self, 
                    "Report Downloaded", 
                    f"Report for {name} has been saved to {file_path}"
                )
            except Exception as e:
                QMessageBox.warning(
                    self, 
                    "Download Failed", 
                    f"Could not save report: {str(e)}"
                )

# Example usage
if __name__ == '__main__':
    app = QApplication(sys.argv)
    reports_tab = ReportsTab()
    reports_tab.show()
    sys.exit(app.exec())