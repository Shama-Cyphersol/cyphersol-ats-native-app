from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QDateEdit, QCheckBox, QApplication, QLabel, QFrame, QScrollArea, QHBoxLayout, QTableWidget, QFileDialog,QTableWidgetItem, QHeaderView)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QDate, Qt
from apps.report.controllers import *
import sys

# Report Generator
class ReportGeneratorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_files = []  # Store selected files
        self.init_ui()

    def init_ui(self):
        # Set the main layout of the window
        main_layout = QVBoxLayout()

        title = QLabel("Generate Report")
        title.setFont(QFont("Helvetica", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        main_layout.addWidget(title)

        # Create a frame to hold the form
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #bdc3c7;
                border-radius: 10px;
                padding: 10px;
                background-color: #ffffff; /* Background color of the form */
            }
        """)

        # Create a form layout to hold form fields
        form_layout = QFormLayout()

        # Case ID field (label on top, field below)
        case_id_layout = QVBoxLayout()
        case_id_label = self.create_label("Case ID:")
        case_id_layout.addWidget(case_id_label)
        self.case_id = QLineEdit()
        self.case_id.setPlaceholderText("Auto-generate ID")
        self.case_id.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 16px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                color: #34495e;  /* Text color */
            }
            QLineEdit:focus {
                border: 1px solid #2980b9;  /* Border color when focused */
            }
            QLineEdit::placeholder {
                color: #95a5a6;  /* Placeholder text color */
                font-style: italic;  /* Optional: make placeholder italic */
            }
        """)
        case_id_layout.addWidget(self.case_id)
        form_layout.addRow(case_id_layout)

        # Bank Statement and Password in one row (horizontal layout)
        bp_layout = QHBoxLayout()

        # File input section
        file_input_layout = QVBoxLayout()
        file_label = self.create_label("Bank Statements")
        file_input_layout.addWidget(file_label)

        # Create a horizontal layout for file input and button
        file_selection_layout = QHBoxLayout()
         # File display field
        self.file_display = QLineEdit()
        self.file_display.setReadOnly(True)
        self.file_display.setPlaceholderText("Select PDF or Excel files...")
        self.file_display.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 16px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                color: #34495e;
                background-color: #f5f6fa;
            }
        """)
        # Browse button
        self.browse_button = QPushButton("Browse")
        self.browse_button.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.browse_button.clicked.connect(self.browse_files)

        file_selection_layout.addWidget(self.file_display)
        file_selection_layout.addWidget(self.browse_button)
        file_input_layout.addLayout(file_selection_layout)

        bp_layout.addLayout(file_input_layout)

        # Password field
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setPlaceholderText("Enter Password")
        self.password.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 16px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                color: #34495e;  /* Text color */
            }
            QLineEdit:focus {
                border: 1px solid #2980b9;  /* Border color when focused */
            }
            QLineEdit::placeholder {
                color: #95a5a6;  /* Placeholder text color */
                font-style: italic;  /* Optional: make placeholder italic */
            }
        """)
        bp_layout.addLayout(self.create_labeled_field("Password", self.password))
        form_layout.addRow(bp_layout)

        # Start Date and End Date on one line
        date_layout = QHBoxLayout()
        start_date_layout = QVBoxLayout()
        start_date_label = self.create_label("Start Date")
        start_date_layout.addWidget(start_date_label)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        start_date_calendar_widget = self.start_date.calendarWidget()
        start_date_calendar_widget.setStyleSheet("""
            QCalendarWidget QAbstractItemView:enabled {
                color: black;  /* Date color */
                background-color: white;
            }
        """)
        self.start_date.setDisplayFormat("dd/MM/yyyy")  # Set display format
        # set default date to today
        self.start_date.setDate(QDate.currentDate())
        
        self.start_date.setStyleSheet("""
            QDateEdit {
                padding: 10px;
                font-size: 16px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                color: black;  
            }
            QDateEdit:focus {
                border: 1px solid #2980b9;  
            }
        """)
        start_date_layout.addWidget(self.start_date)

        end_date_layout = QVBoxLayout()
        end_date_label = self.create_label("End Date")
        end_date_layout.addWidget(end_date_label)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        end_date_calendar_widget = self.end_date.calendarWidget()
        end_date_calendar_widget.setStyleSheet("""
            QCalendarWidget QAbstractItemView:enabled {
                color: black;  /* Date color */
                background-color: white;
            }
        """)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setStyleSheet("""
            QDateEdit {
                padding: 10px;
                font-size: 16px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                color: #34495e;  
            }
            QDateEdit:focus {
                border: 1px solid #2980b9;  
            }
        """)
        end_date_layout.addWidget(self.end_date)
        date_layout.addLayout(start_date_layout)
        date_layout.addLayout(end_date_layout)
        form_layout.addRow(date_layout)

        # Submit button 
        button_box_layout = QVBoxLayout()
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.setFixedSize(120, 43) 
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.submit_button.clicked.connect(self.submit_form)
        # button_box_layout.addSpacing(20)  # Add space between form and button
        button_box_layout.addStretch()
        button_box_layout.addWidget(self.submit_button)
        form_layout.addRow(button_box_layout)

        # Add the form layout to the frame
        form_frame.setLayout(form_layout)

        # Add the frame to the main layout
        main_layout.addWidget(form_frame)

        # Add the Recent Reports table below the form
        main_layout.addWidget(self.create_section_title("Recent Reports"))
        main_layout.addWidget(self.create_recent_reports_table())

        # Set the window background and other properties
        self.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 10px;
            }
        """)

        # Set the layout and window title
        self.setLayout(main_layout)
        self.setWindowTitle('Styled PyQt6 App')

    def create_section_title(self, text):
        section_title = QLabel(text)
        section_title.setFont(QFont("Helvetica", 18, QFont.Weight.Bold))
        section_title.setStyleSheet("color: #34495e; margin-top: 20px;")
        return section_title
    
    def create_recent_reports_table(self):
        try:
           # Fetch recent reports
           recent_reports = get_recent_reports()

        # Ensure we have a valid list of reports, otherwise initialize an empty list
           if recent_reports is None:
            recent_reports = []
    
        except Exception as e:
        # Log the exception (you can use logging or print)
            print(f"Error fetching recent reports: {e}")
            recent_reports = []
            
        # Create the table widget with 3 columns
        table = QTableWidget()
        table.setColumnCount(4)
        
        table.setHorizontalHeaderLabels(["Select", "Case ID", "Date", "Report Name"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setStyleSheet("""
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
        """)
        table.setRowCount(len(recent_reports))
        # Populate the table with data
        recent_reports = get_recent_reports()
        for row, report in enumerate(recent_reports):
         # Add a checkbox in the first column
            checkbox_widget = QWidget()
            checkbox = QCheckBox()
            checkbox_layout = QHBoxLayout()
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Align checkbox to center
            
            # Remove any extra spacing in the layout
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.setSpacing(0)
            
            checkbox_widget.setLayout(checkbox_layout)

            table.setCellWidget(row, 0, checkbox_widget)  # Set the checkbox in the first column

        # Add the report data (Case ID, Date, and Report Name)
            case_id_item = QTableWidgetItem(str(report['id']))
            case_id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 1, case_id_item)

            date_item = QTableWidgetItem(report['date'])
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 2, date_item)

            report_name_item = QTableWidgetItem(report['name'])
            report_name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 3, report_name_item)

        return table
    
    def browse_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Bank Statements",
            "",
            "PDF & Excel Files (*.pdf *.xlsx *.xls)"
        )
        if files:
            self.selected_files = files
            # Display number of files selected
            files_text = f"{len(files)} file(s) selected"
            self.file_display.setText(files_text)

    def submit_form(self):
        # Get the form data
        case_id = self.case_id.text()
        files = self.selected_files  # List of selected file paths
        password = self.password.text()
        start_date = self.start_date.date().toString("dd-MM-yyyy")
        end_date = self.end_date.date().toString("dd-MM-yyyy")

        # Print the form data in the terminal
        print(f"Case ID: {case_id}")
        print(f"Selected Files: {files}")
        print(f"Password: {password}")
        print(f"Start Date: {start_date}")
        print(f"End Date: {end_date}")

    def create_label(self, text):
        label = QLabel(text)
        label.setFont(QFont("Arial", 14))
        label.setStyleSheet("""
            QLabel {
                color: #34495e;
                font-size: 14px;
                padding: 0px;
                margin: 0px;
                border: none;
            }
        """)
        return label

    def create_labeled_field(self, label_text, widget):
        layout = QVBoxLayout()
        label = self.create_label(label_text)
        layout.addWidget(label)
        layout.addWidget(widget)
        return layout

def main():
    app = QApplication(sys.argv)
    window = ReportsApp()
    window.resize(600, 400)  # Resize the window to accommodate the form
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()



# File Opener
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


class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()

        # Window title
        self.setWindowTitle("Automatic Activation")

        # Fonts
        title_font = QFont("Arial", 12)
        title_font.setBold(True)

        label_font = QFont("Arial", 10)

        # Main layout
        main_layout = QVBoxLayout()

        # Title label
        title_label = QLabel("Please copy/paste your license information from the registration message:")
        title_label.setFont(label_font)
        title_label.setWordWrap(True)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        # License Name
        license_name_label = QLabel("License Name:")
        license_name_label.setFont(label_font)
        self.license_name_input = QLineEdit()

        # License Key
        license_key_label = QLabel("License Key:")
        license_key_label.setFont(label_font)
        self.license_key_input = QLineEdit()

        # Add fields to form layout
        form_layout.addRow(license_name_label, self.license_name_input)
        form_layout.addRow(license_key_label, self.license_key_input)

        # Activate Button
        activate_button = QPushButton("Activate")
        activate_button.setFont(title_font)
        activate_button.setStyleSheet("background-color: #0078D7; color: white; padding: 8px;")

        # Align button in the center
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(activate_button)
        button_layout.addStretch()

        # Add elements to the main layout
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)

        # Set the layout to the window
        self.setLayout(main_layout)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("Automatic activation")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title_label)

        # Instructions
        instructions_label = QLabel("Please copy/paste your license information from the registration\nmessage:")
        instructions_label.setFont(QFont("Arial", 10))
        layout.addWidget(instructions_label)

        # License Name
        name_layout = QHBoxLayout()
        name_label = QLabel("License Name:")
        name_label.setFont(QFont("Arial", 10))
        name_layout.addWidget(name_label)
        self.name_input = QLineEdit()
        self.name_input.setFont(QFont("Arial", 10))
        self.name_input.setText("Irena Davis")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # License Key
        key_layout = QHBoxLayout()
        key_label = QLabel("License Key:")
        key_label.setFont(QFont("Arial", 10))
        key_layout.addWidget(key_label)
        self.key_input = QLineEdit()
        self.key_input.setFont(QFont("Arial", 10))
        self.key_input.setText("11111-22222-33333-44444-55555-66666")
        key_layout.addWidget(self.key_input)
        layout.addLayout(key_layout)

        # Add stretch to push everything to the top
        layout.addStretch()

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(divider)

        # Buttons
        button_layout = QHBoxLayout()
        help_button = QPushButton("Help")
        back_button = QPushButton("< Back")
        next_button = QPushButton("Next >")
        next_button.setStyleSheet("background-color: #007bff; color: white;")
        cancel_button = QPushButton("Cancel")

        button_layout.addWidget(help_button)
        button_layout.addStretch()
        button_layout.addWidget(back_button)
        button_layout.addWidget(next_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setWindowTitle('License Activation')
        self.setGeometry(100, 100, 400, 250)
