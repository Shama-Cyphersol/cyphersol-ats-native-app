from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QTableWidget, QFileDialog, QTableWidgetItem,
                             QHBoxLayout, QLabel, QLineEdit, QHeaderView, QFrame, QScrollArea)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
import pandas as pd
from modules.excel_handler import read_excel

class FileOpenerTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title = QLabel("File Opener")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)

        # File selection area
        file_frame = QFrame()
        file_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        file_layout = QHBoxLayout(file_frame)

        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("Select an Excel file...")
        self.file_path_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                font-size: 16px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
        """)
        file_layout.addWidget(self.file_path_input)

        self.open_button = QPushButton("Browse")
        self.open_button.clicked.connect(self.open_file)
        self.open_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px 20px;
                font-size: 16px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        file_layout.addWidget(self.open_button)

        layout.addWidget(file_frame)

        # Table for displaying Excel data
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        table_layout = QVBoxLayout(table_frame)

        table_label = QLabel("Excel Content")
        table_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        table_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        table_layout.addWidget(table_label)

        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border: none;
                padding: 8px;
            }
            QTableWidget::item {
                color: black;
                font-size: 14px;
            }
        """)
        table_layout.addWidget(self.table)

        layout.addWidget(table_frame)
        self.setLayout(layout)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx *.xls)")
        if file_name:
            self.file_path_input.setText(file_name)
            df = read_excel(file_name)
            self.display_data(df)

    def display_data(self, df):
        self.table.setRowCount(df.shape[0])
        self.table.setColumnCount(df.shape[1])
        self.table.setHorizontalHeaderLabels(df.columns)

        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iloc[row, col]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
