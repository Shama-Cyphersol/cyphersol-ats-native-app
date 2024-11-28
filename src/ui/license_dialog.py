from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, 
                             QLineEdit, QPushButton, QLabel, QMessageBox)
from PyQt6.QtCore import Qt
from ..utils.license_verifier import LicenseVerifier
import logging

logger = logging.getLogger(__name__)

class LicenseDialog(QDialog):
    def __init__(self, parent=None, config_path=None, test_mode=False):
        super().__init__(parent)
        self.license_verifier = LicenseVerifier(config_path)
        self.test_mode = test_mode
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("License Verification")
        self.setModal(True)
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Create input fields
        self.username_input = QLineEdit()
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        self.license_key_input = QLineEdit()
        
        # Add fields to form layout
        form_layout.addRow("Username:", self.username_input)
        form_layout.addRow("First Name:", self.first_name_input)
        form_layout.addRow("Last Name:", self.last_name_input)
        form_layout.addRow("License Key:", self.license_key_input)
        
        # Create verify button
        verify_button = QPushButton("Verify License")
        verify_button.clicked.connect(self.verify_license)
        
        # Add layouts to main layout
        layout.addLayout(form_layout)
        layout.addWidget(verify_button)
        
        self.setLayout(layout)
        
        # If in test mode, pre-fill with test credentials
        if self.test_mode:
            self.username_input.setText("1-bd7c6c56")
            self.license_key_input.setText("SOMEX4Y4ZLicenseKEY1732686454")
            self.first_name_input.setText("Test")
            self.last_name_input.setText("User")
        
    def verify_license(self):
        try:
            result = self.license_verifier.validate_offline_license(
                license_key=self.license_key_input.text(),
                username=self.username_input.text()
            )
            
            if result["verified"]:
                QMessageBox.information(
                    self,
                    "Success",
                    "License verified successfully!\nWelcome to the dashboard."
                )
                self.accept()  # Close dialog and return success
            else:
                QMessageBox.warning(
                    self,
                    "Verification Failed",
                    f"License verification failed: {result['message']}"
                )
                
        except Exception as e:
            logger.error(f"Error during license verification: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"An error occurred during verification: {str(e)}"
            )
