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
from .json_logic import load_all_case_data, load_case_data
from ..ui.case_dashboard_components.name_manager import SimilarNameGroups

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


class NameManagerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title with shadow effect
        title = QLabel("Select a Case to View Similar Names Groups")
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
            label = QLabel(f'<a href="#">View Groups</a>')
            label.setStyleSheet("a { color: #3498db; } a:hover { color: #2980b9; }")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setOpenExternalLinks(False)
            
            # Create a closure to capture the correct row
            def create_click_handler(current_row):
                def handler(event):
                    self.show_similar_names_groups(current_row)
                return handler
            
            label.mousePressEvent = create_click_handler(row)
            self.reports_table.setCellWidget(row, 4, label)

    def show_similar_names_groups(self, row):
        """Open GroupSelector for the specific case ID in full screen"""

        # Ensure the dialog is stored as an instance attribute
        case_id = self.reports_table.item(row, 2).text()
        print("case_id name manager",case_id)

        self.similar_names_dialog = SimilarNameGroups(case_id, parent=self)
        
        # Set the window to full screen and keep a reference
        self.similar_names_dialog.showMaximized()
        
        # Ensure the dialog doesn't get garbage collected
        self.similar_names_dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)





# Example usage
if __name__ == '__main__':
    app = QApplication(sys.argv)
    reports_tab = NameManagerTab()
    reports_tab.show()
    sys.exit(app.exec())