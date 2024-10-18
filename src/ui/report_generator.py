from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QDateEdit, QCheckBox,
                             QLabel, QFrame, QScrollArea, QHBoxLayout)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QDate, Qt
from modules.report_generator import generate_report

class ReportGeneratorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title = QLabel("Generate Report")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        main_layout.addWidget(title)

        # Form frame
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)

        # Scroll area for form
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
        """)
        form_layout.addWidget(scroll_area)

        # Form container
        form_container = QWidget()
        scroll_area.setWidget(form_container)
        form_container_layout = QFormLayout(form_container)
        form_container_layout.setSpacing(20)

        # Report Name
        self.report_name = QLineEdit()
        self.report_name.setPlaceholderText("Enter report name...")
        self.style_input(self.report_name)
        form_container_layout.addRow(self.create_label("Report Name:"), self.report_name)

        # Auto Date
        date_layout = QHBoxLayout()
        self.auto_date = QCheckBox("Use current date")
        self.auto_date.setStyleSheet("QCheckBox { font-size: 16px; }")
        self.auto_date.stateChanged.connect(self.toggle_date_input)
        date_layout.addWidget(self.auto_date)

        # Date Input
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.style_input(self.date_input)
        date_layout.addWidget(self.date_input)
        form_container_layout.addRow(self.create_label("Report Date:"), date_layout)

        # Add more form fields here as needed

        main_layout.addWidget(form_frame)

        # Generate Button
        self.generate_button = QPushButton("Generate Report")
        self.generate_button.clicked.connect(self.on_generate)
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 15px 30px;
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        main_layout.addWidget(self.generate_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

    def create_label(self, text):
        label = QLabel(text)
        label.setFont(QFont("Arial", 16))
        label.setStyleSheet("color: #2c3e50;")
        return label

    def style_input(self, widget):
        widget.setStyleSheet("""
            QLineEdit, QDateEdit {
                padding: 12px;
                font-size: 16px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
        """)

    def toggle_date_input(self, state):
        self.date_input.setEnabled(not state)

    def on_generate(self):
        name = self.report_name.text()
        date = self.date_input.date().toString("yyyy-MM-dd") if not self.auto_date.isChecked() else "auto"
        generate_report(name, date)
        # You might want to show a success message or update some status here
