from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QDialog,QFormLayout, QLineEdit, QPushButton, QDateEdit,QMainWindow, QTabWidget,QApplication, QLabel, QFrame, QScrollArea, QHBoxLayout, QTableWidget, QFileDialog,QTableWidgetItem, QHeaderView)
from PyQt6.QtGui import QFont,QColor,QBrush
from PyQt6.QtCore import QDate, Qt
from apps.report.controllers import *
import sys
from utils.CA_Statement_Analyzer import CABankStatement
from utils.json_logic import *
import random
import string
from .case_dashboard import CaseDashboard
from utils.pdf_processor import PDFProcessor

# Report Generator
class ReportGeneratorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_files = []  # Store selected files
        self.ca_id = "CA_ID_"+''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        self.tab_widget = QWidget()
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
        self.case_id.setText(str(self.ca_id))
        self.case_id.setReadOnly(True)
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
        self.file_display.mousePressEvent = lambda e: self.browse_files()

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
        self.end_date.setDisplayFormat("dd/MM/yyyy")  # Set display format
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
        main_layout.addWidget(self.tab_widget)

        self.setLayout(main_layout)
        self.setWindowTitle('Styled PyQt6 App')

    def create_section_title(self, text):
        section_title = QLabel(text)
        section_title.setFont(QFont("Helvetica", 18, QFont.Weight.Bold))
        section_title.setStyleSheet("color: #34495e; margin-top: 20px;")
        return section_title
    
    def create_recent_reports_table(self):
            
        # Create the table widget with 3 columns
        if not hasattr(self, 'table'):

            self.table = QTableWidget()
            self.table.setColumnCount(4)
            
            self.table.setHorizontalHeaderLabels(["Case ID", "Report Name","Start Date","End Date"])
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
            self.table.cellClicked.connect(self.on_table_click)

        recent_reports = load_all_case_data()
        self.table.setRowCount(len(recent_reports))
        # Populate the table with data
        for row, report in enumerate(recent_reports):
        
            case_id_item = QTableWidgetItem(str(report['case_id']))
            case_id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # font = QFont("Arial", 10)
            # font.setUnderline(True)
            # case_id_item.setFont(font)
            case_id_item.setFlags(case_id_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, case_id_item)

            report_name_item = QTableWidgetItem(report['report_name'])
            report_name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # make it read only
            report_name_item.setFlags(report_name_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, report_name_item)

            start_date_item = QTableWidgetItem(report['start_date'])
            start_date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            start_date_item.setFlags(start_date_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, start_date_item)

            end_date_item = QTableWidgetItem(report['end_date'])
            end_date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            end_date_item.setFlags(end_date_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 3, end_date_item)


        return self.table
    
    def on_table_click(self, row, col):
        # Get the case ID from the first column
        case_id = self.table.item(row, 0).text()
        print("Case ID clicked: ", case_id)
        
        # Create and show the case dashboard
        self.case_dashboard = CaseDashboard(case_id)
        self.case_dashboard.show()

    def browse_files(self,event=None):
        if isinstance(event, bool):  # If called from button click
            pass
        elif event is not None:  # If called from mouse click
            event.accept()

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
        CA_ID = self.ca_id
        pdf_paths = self.selected_files
        password = self.password.text()
        
        # Get dates from the form
        start_date = [self.start_date.date().toString("dd-MM-yyyy")] if self.start_date.date() else ["-"]
        end_date = [self.end_date.date().toString("dd-MM-yyyy")] if self.end_date.date() else ["-"]

        print("\n=== Starting PDF Processing ===")
        print(f"Processing files: {pdf_paths}")

        try:
            # Initialize the PDF processor
            print("\n1. Initializing PDF Processor...")
            processor = PDFProcessor(model_path="src/models/output_ner_model")
            
            processed_results = []
            entities_data = {"Name": [], "Acc Number": []}
            
            # Process each PDF file
            for pdf_path in pdf_paths:
                print(f"\n2. Processing file: {pdf_path}")
                result = processor.process_single_pdf(pdf_path)
                processed_results.append(result)
                print(f"3. Processing result: {result}")
                
                if not result.error:
                    print("4. Extracted entities:")
                    for entity in result.entities:
                        print(f"   - {entity.label}: {entity.text}")
                        # Changed PER to PERSON for consistency
                        if entity.label == "PER":  # or entity.label == "PERSON":
                            if entity.text not in entities_data["Name"]:
                                entities_data["Name"].append(entity.text)
                                print(f"     Added person: {entity.text}")
                        elif entity.label == "ACC NO":  # or entity.label == "ACCOUNT_NUMBER":
                            if entity.text not in entities_data["Acc Number"]:
                                entities_data["Acc Number"].append(entity.text)
                                print(f"     Added account: {entity.text}")
                else:
                    print(f"   Error processing file: {result.error}")

            # If no entities found, add default values
            if not entities_data["Name"]:
                entities_data["Name"] = ["Unknown"]
            if not entities_data["Acc Number"]:
                entities_data["Acc Number"] = ["Not Found"]

            print("\n5. Final extracted entities:")
            print(f"   Names: {entities_data['Name']}")
            print(f"   Accounts: {entities_data['Acc Number']}")

            # Save results
            print("\n6. Saving results...")
            save_ner_results(CA_ID, processed_results)
            save_case_data(
                case_id=CA_ID,
                file_names=pdf_paths,
                start_date=start_date,
                end_date=end_date,
                individual_names=entities_data
            )
            print("7. Results saved successfully")

        except Exception as e:
            print(f"\nERROR in submit_form: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(traceback.format_exc())
            return

        print("\n=== PDF Processing Complete ===\n")


    def create_label(self, text):
        label = QLabel(text)
        label.setFont(QFont("Arial", 14))
        label.setStyleSheet("""
            QLabel {
                color: #34495e;
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