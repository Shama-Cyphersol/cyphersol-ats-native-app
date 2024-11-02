from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame,
                             QTableWidget, QTableWidgetItem, QHeaderView, QGraphicsDropShadowEffect,
                             QScrollArea, QDialog, QComboBox, QPushButton)
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt
import pandas as pd
import os
from utils.json_logic import *
from .individual_dashboard import IndividualDashboard

class CaseDashboard(QWidget):
    def __init__(self, case_id):
        super().__init__()
        self.case_id = case_id
        self.case = load_case_data(case_id)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("background-color: #f5f6fa;")
        
        main_layout = QVBoxLayout(self)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_widget.setStyleSheet("background-color: #ffffff; border-radius: 10px; padding: 10px;")

        # Title
        title = QLabel("Case Dashboard Overview")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #34495e; margin-bottom: 15px;")
        content_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # Individual Table
        content_layout.addWidget(self.create_section_title("Individual Person Table"))
        content_layout.addWidget(self.create_dummy_data_table_individual())

        # Entity Table
        content_layout.addWidget(self.create_section_title("Entity Table"))
        content_layout.addWidget(self.create_dummy_data_table_entity())

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def create_section_title(self, title):
        label = QLabel(title)
        label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        label.setStyleSheet("color: #34495e; margin-top: 20px;")
        return label

    def create_dummy_data_table_individual(self):
        data = []
        for i in range(len(self.case["file_names"])):
            data.append({"ID": i+1, "Name": self.case["file_names"][i], "Start Date": "-", "End Date": "-"})

        headers = ["ID","Name", "Start Date", "End Date"]
        table_widget = PaginatedTableWidget(headers, data, rows_per_page=5,case_id=self.case_id)
        self.add_shadow(table_widget)
        return table_widget

    def create_dummy_data_table_entity(self):
        headers = ["Entity ID", "Entity Name", "Status"]
        data = [{"Entity ID": i + 1, "Entity Name": f"Entity {chr(65 + i)}", "Status": "Active" if i % 2 == 0 else "Inactive"} for i in range(10)]
        table_widget = PaginatedTableWidget(headers, data, rows_per_page=5)
        self.add_shadow(table_widget)
        return table_widget

    def add_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(2, 2)
        widget.setGraphicsEffect(shadow)

    def on_cell_click(self, row, column):
        # Open a new window with the details of the clicked item
        dialog = QDialog(self)
        dialog.setWindowTitle("Entry Details")
        dialog_layout = QVBoxLayout(dialog)
        entry_label = QLabel(f"Details for Entry {row + 1}")
        entry_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        dialog_layout.addWidget(entry_label)

        dialog.setLayout(dialog_layout)
        dialog.exec()

class PaginatedTableWidget(QWidget):
    def __init__(self, headers, data, rows_per_page=5,case_id=None):
        super().__init__()
        self.headers = headers
        self.data = data
        self.rows_per_page = rows_per_page
        self.current_page = 0
        self.case_id = case_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget(self.rows_per_page, len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Calculate exact height needed for 10 rows plus header
        
      

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ecf0f1;
                border-radius: 8px;
                color: #2c3e50;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border: none;
                margin: 10px;
            }
            QTableWidget::item {
                padding: 10px;
            }
        """)

        pagination_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.previous_page)
        self.prev_button.setStyleSheet(self.button_styles())
        
        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setStyleSheet("color: #34495e; font-weight: bold; font-size: 14px;")
        
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setStyleSheet(self.button_styles())

        pagination_layout.addStretch()
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_button)
        pagination_layout.addStretch()

        layout.addWidget(self.table)
        layout.addLayout(pagination_layout)

        # Connect cell click signal
        self.table.cellClicked.connect(self.on_cell_click)

        self.update_table()

    def button_styles(self):
        return """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 5px;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """

    def update_table(self):
        start_idx = self.current_page * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, len(self.data))

        self.table.clearContents()
        self.table.setRowCount(self.rows_per_page)

        for row, item in enumerate(self.data[start_idx:end_idx]):
            for col, key in enumerate(self.headers):
                self.table.setItem(row, col, QTableWidgetItem(str(item[key])))

        total_pages = (len(self.data) + self.rows_per_page - 1) // self.rows_per_page
        self.page_label.setText(f"Page {self.current_page + 1} of {total_pages}")
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < total_pages - 1)

    def next_page(self):
        self.current_page += 1
        self.update_table()

    def previous_page(self):
        self.current_page -= 1
        self.update_table()

    def change_rows_per_page(self, value):
        self.rows_per_page = int(value)
        self.current_page = 0
        
        # Recalculate height
        header_height = self.table.horizontalHeader().height()
        row_height = 35
        total_height = header_height + (row_height * self.rows_per_page)
        
        # Update table size
        self.table.setRowCount(self.rows_per_page)
        self.table.setFixedHeight(total_height)
        
        # Reset row heights
        for i in range(self.rows_per_page):
            self.table.setRowHeight(i, row_height)
            
        self.update_table()

    def on_cell_click(self, row, column):
        start_idx = self.current_page * self.rows_per_page
        actual_row = start_idx + row
        
        if actual_row < len(self.data):
            if column == 1:
                name = self.data[actual_row]["Name"]
                print(f"Clicked on name: {name}")

                cash_flow_network = IndividualDashboard(case_id=self.case_id,name=name)
                # Create a new dialog and set the CashFlowNetwork widget as its central widget
                self.new_window = QDialog(self)
                self.new_window.setModal(False)  # Set the dialog as non-modal

                # Set the minimum size of the dialog
                # self.new_window.setMinimumSize(1000, 800)  # Set the minimum width and height
                # make the dialog full screen
                self.new_window.showMaximized()
                # show minimize and resize option on the Qdialog window
                self.new_window.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint)
                self.new_window.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint)
                self.new_window.setWindowFlag(Qt.WindowType.WindowCloseButtonHint)
                

                # Create a layout for the dialog and add the CashFlowNetwork widget
                layout = QVBoxLayout()
                layout.addWidget(cash_flow_network)
                self.new_window.setLayout(layout)

                # Show the new window
                self.new_window.show()