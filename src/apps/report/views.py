from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class ReportsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reports Generation")
        layout = QVBoxLayout()

        label = QLabel("Generate Reports Section")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        button_generate = QPushButton("Generate Report")
        button_generate.clicked.connect(self.generate_report)
        layout.addWidget(button_generate)

        button_back = QPushButton("Back to User Management")
        button_back.clicked.connect(self.back_to_user_management)
        layout.addWidget(button_back)

        # Add some padding and spacing
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        self.setLayout(layout)

    def generate_report(self):
        print("Generating report...")
        # Logic for generating report

    def back_to_user_management(self):
        print("Navigating back to User Management")
        # Logic to navigate back (if needed, currently handled in the sidebar)