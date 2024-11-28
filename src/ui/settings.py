from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QLabel
from ..modules.license_manager import get_license_info

class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        form_layout = QFormLayout()
        self.username = QLineEdit()
        self.email = QLineEdit()
        self.license_status = QLabel()
        self.license_expiry = QLabel()

        form_layout.addRow("Username:", self.username)
        form_layout.addRow("Email:", self.email)
        form_layout.addRow("License Status:", self.license_status)
        form_layout.addRow("License Expiry:", self.license_expiry)

        layout.addLayout(form_layout)
        self.setLayout(layout)

        self.update_license_info()

    def update_license_info(self):
        license_info = get_license_info()
        self.license_status.setText(license_info['status'])
        self.license_expiry.setText(license_info['expiry'])
