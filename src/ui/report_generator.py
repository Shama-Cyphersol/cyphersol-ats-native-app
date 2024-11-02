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
        table = QTableWidget()
        table.setColumnCount(4)
        
        table.setHorizontalHeaderLabels(["Case ID", "Report Name","Start Date","End Date"])
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
            QTableWidget::item {
                color: black;
                padding: 5px;
            }
        """)
        recent_reports = load_all_case_data()
        table.setRowCount(len(recent_reports))
        # Populate the table with data
        for row, report in enumerate(recent_reports):
        
            case_id_item = QTableWidgetItem(str(report['case_id']))
            case_id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # font = QFont("Arial", 10)
            # font.setUnderline(True)
            # case_id_item.setFont(font)
            case_id_item.setFlags(case_id_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 0, case_id_item)

            report_name_item = QTableWidgetItem(report['report_name'])
            report_name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # make it read only
            report_name_item.setFlags(report_name_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 1, report_name_item)

            start_date_item = QTableWidgetItem(report['start_date'])
            start_date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            start_date_item.setFlags(start_date_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 2, start_date_item)

            end_date_item = QTableWidgetItem(report['end_date'])
            end_date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            end_date_item.setFlags(end_date_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            table.setItem(row, 3, end_date_item)

        self.recent_reports_table = table
        table.cellClicked.connect(self.case_id_clicked)

        return table
    
    
    def case_id_clicked(self, row, column):
        if column == 0:
            case_id = self.recent_reports_table.item(row, column).text()
            print("Case ID clicked: ", case_id)
            cash_flow_network = CaseDashboard(case_id=case_id)
             # Create a new dialog and set the CashFlowNetwork widget as its central widget
            self.new_window = QDialog(self)
            self.new_window.setWindowTitle(f"Case Dashboard - Case {case_id}")
            self.new_window.setModal(False)  # Set the dialog as non-modal
            self.new_window.showMaximized()
            self.new_window.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint)
            self.new_window.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint)
            self.new_window.setWindowFlag(Qt.WindowType.WindowCloseButtonHint)

            # Set the minimum size of the dialog
            self.new_window.setMinimumSize(1000, 800)  # Set the minimum width and height

            # Create a layout for the dialog and add the CashFlowNetwork widget
            layout = QVBoxLayout()
            layout.addWidget(cash_flow_network)
            self.new_window.setLayout(layout)

            # Show the new window
            self.new_window.show()

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
        pdf_paths = self.selected_files  # List of selected file paths
        # passwords = self.password.text()
        passwords = []
        # start_date = self.start_date.date().toString("dd-MM-yyyy")
        # end_date = self.end_date.date().toString("dd-MM-yyyy")
        start_date = [""]
        end_date = [""]

        bank_names = []
        # for each path in pdf_paths, assign a unique name as A,B,C etc
        for i in range(len(pdf_paths)):
            bank_names.append(chr(65 + i))
            passwords.append("")
            start_date.append(start_date[0])
            end_date.append(end_date[0])


        print ("CA_ID",CA_ID)
        print ("pdf_paths",pdf_paths)
        print ("passwords",passwords)
        print ("start_date",start_date)
        print ("end_date",end_date)
        print ("bank_names",bank_names)


        progress_data = {
            'progress_func': lambda current, total, info: print(f"{info} ({current}/{total})"),
            'current_progress': 10,
            'total_progress': 100
        }

        print("progress_data",progress_data)


        converter = CABankStatement(bank_names, pdf_paths, passwords, start_date, end_date, CA_ID, progress_data)
        result = converter.start_extraction()
        # single_df = result["single_df"]
        # cummalative_df = result["cummalative_df"]

        # # Saving all df as Excel
        # for key,value in single_df["A0"]["data"].items():
        #     try:
        #         value.to_excel("src/data/"+key+".xlsx")
        #     except:
        #         print("Was not able to save excel for as it may not be a df - ",key,"Type =  ",type(value))
        #         pass
        individual_names = result["cummalative_df"]["name_acc_df"].to_dict("list")

        save_case_data(CA_ID, pdf_paths, start_date, end_date,individual_names)
        save_result(CA_ID,result)

        print("Successfully saved case data and result")

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