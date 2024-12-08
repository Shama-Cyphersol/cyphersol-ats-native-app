from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QDialogButtonBox, QComboBox,QCompleter, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget,QMessageBox, QVBoxLayout, QDialog,QFormLayout, QLineEdit, QPushButton, QDateEdit,QMainWindow, QTabWidget,QApplication, QLabel, QFrame, QScrollArea, QHBoxLayout, QTableWidget, QFileDialog,QTableWidgetItem, QHeaderView)
from PyQt6.QtGui import QFont,QColor,QBrush
from PyQt6.QtCore import QDate, Qt
from apps.report.controllers import *
import sys
from utils.CA_Statement_Analyzer import CABankStatement
from utils.json_logic import *
# from src.utils.pdf_to_name_and_accno import pdf_to_name_and_accno
import time
from ui.main_dashboard_components.recent_reports import RecentReportsTable
from utils.name_merge import *
from utils.pdf_to_name import extract_entities
from utils.account_number_ifsc_extraction import extract_accno_ifsc
from ui.signals.global_signals import global_signal_manager



class UnitDialog(QDialog):
    def __init__(self, existing_units, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add New Unit")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Unit name input
        self.unit_input = QLineEdit()
        self.unit_input.setPlaceholderText("Enter new unit name")
        color_black_styles = "color: #34495e;"
        self.unit_input.setStyleSheet(color_black_styles)
        label = QLabel("Unit Name:")
        label.setStyleSheet(color_black_styles)
        layout.addWidget(label)
        layout.addWidget(self.unit_input)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
    def get_unit_name(self):
        return self.unit_input.text().strip()
    

# Report Generator
class ReportGeneratorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_files = []  # Store selected files
        self.case_id = ""
        self.units = fetch_units()
        serial_number = get_last_serial_number()
        self.selectd_unit = ""
        self.serial_number = self.process_serial_number(serial_number)
        self.tab_widget = QWidget()
        global_signal_manager.update_table.connect(self.update_recent_report_table)

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
            background-color: #ffffff;
            border: 1px solid #bdc3c7;
            border-radius: 10px;
            padding: 20px;
            }
            QLabel {
                color: #34495e;
                font-size: 14px;
                margin-bottom: 5px;
            }
        """)

        # Create a form layout to hold form fields
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(20)

        # Uniform input style
        input_style = """
            QLineEdit, QComboBox, QDateEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                color: #34495e;
                background-color: #f8f9fa;
            }
            QComboBox QAbstractItemView {
                background-color: #f8f9fa;
                color: #34495e;
            }

            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 1px solid #3498db;
                outline: none;
            }
            QLineEdit::placeholder, QComboBox::placeholder {
                color: #95a5a6;
                font-style: italic;
            }
        """

        first_row_layout = QHBoxLayout()
        first_row_layout.setSpacing(10)  # Add consistent spacing between elements

        # Unit Dropdown with Add Button
        unit_layout = QVBoxLayout()
        # unit_label = QLabel("Unit")
        unit_label = self.create_label("Unit")
        # unit_label.setStyleSheet("margin-bottom: 5px; color: #34495e;")
        unit_dropdown_layout = QHBoxLayout()
        self.unit_dropdown = QComboBox()
        self.unit_dropdown.addItems(self.units)
        self.unit_dropdown.setEditable(True)
        self.unit_dropdown.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.unit_dropdown.setStyleSheet(input_style)
        self.unit_dropdown.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                
        # Completer for unit dropdown
        completer = QCompleter(self.units)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.unit_dropdown.setCompleter(completer)
                
        # Add button to create new unit
        self.add_unit_btn = QPushButton("+")
        self.add_unit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white !important;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.add_unit_btn.clicked.connect(self.add_new_unit)
                
        unit_dropdown_layout.addWidget(self.unit_dropdown)
        unit_dropdown_layout.addWidget(self.add_unit_btn)
        unit_layout.addWidget(unit_label)
        unit_layout.addLayout(unit_dropdown_layout)
        unit_layout.setSpacing(3)
        first_row_layout.addLayout(unit_layout, 1)  # Add stretch factor

        # Serial Number
        serial_layout = QVBoxLayout()
        # serial_label = QLineEdit("Serial Number")
        serial_label = self.create_label("Serial Number")
        self.custom_serial_number = QLineEdit()
        self.custom_serial_number.setPlaceholderText("Enter custom text")
        self.custom_serial_number.setText(self.serial_number)
        self.custom_serial_number.setStyleSheet(input_style)
        self.custom_serial_number.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        serial_layout.addWidget(serial_label)
        serial_layout.addWidget(self.custom_serial_number)
        serial_layout.setSpacing(5)
        first_row_layout.addLayout(serial_layout, 1)  # Add stretch factor

        # Case ID
        case_id_layout = QVBoxLayout()
        # case_id_label = QLineEdit("Case ID")
        case_id_label = self.create_label("Case ID")
        # case_id_label.setStyleSheet("margin-bottom: 5px; color: #34495e;")
        self.case_id_widget = QLineEdit()
        self.case_id_widget.setText(str(self.case_id))
        self.case_id_widget.setReadOnly(True)
        self.case_id_widget.setPlaceholderText("Auto-generate ID")
        self.case_id_widget.setStyleSheet(input_style + """
            QLineEdit {
                background-color: #f1f2f6;
                color: #7f8c8d;
            }
        """)
        self.case_id_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        case_id_layout.addWidget(case_id_label)
        case_id_layout.addWidget(self.case_id_widget)
        case_id_layout.setSpacing(5)
        first_row_layout.addLayout(case_id_layout, 1)  # Add stretch factor

        form_layout.addRow(first_row_layout)

        self.unit_dropdown.currentTextChanged.connect(self.update_case_id)
        self.custom_serial_number.textChanged.connect(self.update_case_id)
        
        # Initial case ID generation
        self.update_case_id()

        form_layout.addRow(case_id_layout)

        # Bank Statement and Password in one row (horizontal layout)
        bp_layout = QHBoxLayout()

        # File input section
        file_input_layout = QVBoxLayout()
        file_label = self.create_label("Bank Statements")
        # file_label.setStyleSheet("QLabel{margin-bottom: 10px;}")
        # file_label.setStyleSheet("margin-bottom: 5px;")
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
                width: 50vw;
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

        # # Password field
        # self.password = QLineEdit()
        # self.password.setEchoMode(QLineEdit.EchoMode.Password)
        # self.password.setPlaceholderText("Enter Password")
        # self.password.setStyleSheet("""
        #     QLineEdit {
        #         padding: 10px;
        #         font-size: 16px;
        #         border: 1px solid #bdc3c7;
        #         border-radius: 5px;
        #         color: #34495e;  /* Text color */
        #     }
        #     QLineEdit:focus {
        #         border: 1px solid #2980b9;  /* Border color when focused */
        #     }
        #     QLineEdit::placeholder {
        #         color: #95a5a6;  /* Placeholder text color */
        #         font-style: italic;  /* Optional: make placeholder italic */
        #     }
        # """)
        # bp_layout.addLayout(self.create_labeled_field("Password", self.password))
        form_layout.addRow(bp_layout)

        # # Start Date and End Date on one line
        # date_layout = QHBoxLayout()
        # start_date_layout = QVBoxLayout()
        # start_date_label = self.create_label("Start Date")
        # start_date_layout.addWidget(start_date_label)

        # self.start_date = QDateEdit()
        # self.start_date.setCalendarPopup(True)
        # start_date_calendar_widget = self.start_date.calendarWidget()
        # start_date_calendar_widget.setStyleSheet("""
        #     QCalendarWidget QAbstractItemView:enabled {
        #         color: black;  /* Date color */
        #         background-color: white;
        #     }
        # """)
        # self.start_date.setDisplayFormat("dd/MM/yyyy")  # Set display format
        # # set default date to today
        # self.start_date.setDate(QDate.currentDate())
        
        # self.start_date.setStyleSheet("""
        #     QDateEdit {
        #         padding: 10px;
        #         font-size: 16px;
        #         border: 1px solid #bdc3c7;
        #         border-radius: 5px;
        #         color: black;  
        #     }
        #     QDateEdit:focus {
        #         border: 1px solid #2980b9;  
        #     }
        # """)
        # start_date_layout.addWidget(self.start_date)

        # end_date_layout = QVBoxLayout()
        # end_date_label = self.create_label("End Date")
        # end_date_layout.addWidget(end_date_label)

        # self.end_date = QDateEdit()
        # self.end_date.setCalendarPopup(True)
        # end_date_calendar_widget = self.end_date.calendarWidget()
        # end_date_calendar_widget.setStyleSheet("""
        #     QCalendarWidget QAbstractItemView:enabled {
        #         color: black;  /* Date color */
        #         background-color: white;
        #     }
        # """)
        # self.end_date.setDisplayFormat("dd/MM/yyyy")  # Set display format
        # self.end_date.setDate(QDate.currentDate())
        # self.end_date.setStyleSheet("""
        #     QDateEdit {
        #         padding: 10px;
        #         font-size: 16px;
        #         border: 1px solid #bdc3c7;
        #         border-radius: 5px;
        #         color: #34495e;  
        #     }
        #     QDateEdit:focus {
        #         border: 1px solid #2980b9;  
        #     }
        # """)
        # end_date_layout.addWidget(self.end_date)
        # date_layout.addLayout(start_date_layout)
        # date_layout.addLayout(end_date_layout)
        # form_layout.addRow(date_layout)

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
        self.submit_button.clicked.connect(self.submit_form_spinner)
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
    
    # Generate Case ID method
    def generate_case_id(self):
        # Get selected unit
        unit = self.unit_dropdown.currentText().lower().replace(" ", "_")
        # Generate random 4 digits
        # random_digits = ''.join(random.choices(string.digits, k=4))
        serial_number = self.custom_serial_number.text()
        self.serial_number = serial_number
        self.selectd_unit = unit
        # Combine to create case ID
        case_id = f"ATS_{unit}_{serial_number}"
        return case_id
    
    # Update case ID when unit or custom text changes
    def update_case_id(self):
        self.case_id_widget.setText(self.generate_case_id())
        self.case_id = self.case_id_widget.text()
        
    def process_serial_number(self, serial_number):
        sr_no = str(serial_number)
        while len(sr_no) < 5:
            sr_no = '0' + sr_no
        
        return sr_no

    def add_new_unit(self):
        # Open dialog to add new unit
        dialog = UnitDialog(self.units, self)

        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_unit = dialog.get_unit_name()
            
            # Check if unit already exists (case-insensitive)
            existing_units_lower = [u.lower() for u in self.units]
            if new_unit.lower() not in existing_units_lower and new_unit:
                # Add to units list
                self.units.append(new_unit)
                
                # Update dropdown
                self.unit_dropdown.addItem(new_unit)
                
                # Set the newly added unit as current
                self.unit_dropdown.setCurrentText(new_unit)

                add_unit(new_unit)
            elif not new_unit:
                # Show error if empty unit name
                QMessageBox.warning(self, "Invalid Input", "Unit name cannot be empty.")
            else:
                # Show error if unit already exists
                QMessageBox.warning(self, "Duplicate Unit", "This unit already exists.")
        
        dialog.deleteLater()

    def create_section_title(self, text):
        section_title = QLabel(text)
        section_title.setFont(QFont("Helvetica", 18, QFont.Weight.Bold))
        section_title.setStyleSheet("color: #34495e; margin-top: 20px;")
        return section_title

    def create_recent_reports_table(self):
        if not hasattr(self, 'recent_reports_table'):
            self.recent_reports_table = RecentReportsTable()
        
        return self.recent_reports_table.get_web_view()

    def update_table_data(self):
        if hasattr(self, 'recent_reports_table'):
            self.recent_reports_table.update_table_data()
  
    def browse_files(self,event=None):
        if isinstance(event, bool):  # If called from button click
            pass
        elif event != None:  # If called from mouse click
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

    def submit_form_spinner(self):
            # # Create and configure spinner
            # self.spinner_label = QLabel(self)
            # self.spinner_movie = QMovie("assets/spinner.gif")
            # self.spinner_label.setMovie(self.spinner_movie)
            # self.spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # self.spinner_label.setFixedSize(100, 100)
            # self.spinner_label.setStyleSheet("""
            #     QLabel {
            #         background-color: rgba(255, 255, 255, 200);
            #         border-radius: 10px;
            #     }
            # """)

            # # Center the spinner in the parent widget
            # self.spinner_label.move(
            #     (self.width() - self.spinner_label.width()) // 2,
            #     (self.height() - self.spinner_label.height()) // 2,
            # )

            # # Show and start spinner
            # self.spinner_label.show()
            # self.spinner_movie.start()

            # # Create a QTimer to process the form in the next event loop iteration
            # # start the timer
            # QTimer.singleShot(100, self.process_form)

            # Create a QMessageBox for the "Processing" message
        self.processing_popup = QMessageBox(self)
        self.processing_popup.setWindowTitle("Processing")
        self.processing_popup.setText("Please wait while processing...")
        self.processing_popup.setIcon(QMessageBox.Icon.Information)
        self.processing_popup.setStandardButtons(QMessageBox.StandardButton.NoButton)

        # Set the stylesheet for QMessageBox components
        self.processing_popup.setStyleSheet("""
            QMessageBox {
                background-color: #ecf0f1;
            }
            QMessageBox QLabel {
                color: #1e293b;
                font-size: 14px;
                padding: 10px;
            }
            QMessageBox QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                text-align: center;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #1e90ff;
            }
        """)

        # Show the message box
        self.processing_popup.show()
        QApplication.processEvents()

        self.process_form()

        QApplication.processEvents()
        self.processing_popup.close()
        self.processing_popup.hide()


        # QTimer.singleShot(300, self.process_form_and_close)

    def process_form_and_close(self):
        # Perform your form processing here
        self.process_form()
        
        # Close the processing popup
        self.processing_popup.close()

    def process_form(self):
        start = time.time()

        try:
            # Get the form data
            pdf_paths = self.selected_files
            # password = self.password.text()
            password = [""]
            
            password_provided = False
            start_date_provided = False
            end_date_provided = False

            # if password == "": 
            #     password = [""]
            # else:
            #     password_provided = True
            #     password = [password]

            # start_date =[ self.start_date.date().toString("dd-MM-yyyy")]
            # end_date = self.end_date.date().toString("dd-MM-yyyy")
            start_date = [""]
            end_date = [""]

            # Check if start_date is same as today
            # if start_date == QDate.currentDate().toString("dd-MM-yyyy"):
            #     start_date = [""]
            # else:
            #     start_date_provided = True
            #     start_date = [start_date]

            # if end_date == QDate.currentDate().toString("dd-MM-yyyy"):
            #     end_date = [""]
            # else:
            #     end_date_provided = True
            #     end_date = [end_date]

            bank_names = []
            # For each path in pdf_paths, assign a unique name as A,B,C etc
            for i in range(len(pdf_paths)):
                bank_names.append(chr(65 + i))
                if not password_provided:
                    password.append("")
                if not start_date_provided:
                    start_date.append("")
                if not end_date_provided:
                    end_date.append("")

            progress_data = {
                'progress_func': lambda current, total, info: print(f"{info} ({current}/{total})"),
                'current_progress': 10,
                'total_progress': 100
            }

            ner_results = {
                "Name": [],
                "Acc Number": []
            }

            # Process PDFs with NER
            person_count = 0
            for pdf in pdf_paths:
                person_count+=1
                # result = pdf_to_name_and_accno(pdf)
                fetched_name = ""
                fetched_acc_num = ""

                name_entities = extract_entities(pdf)
                acc_number_ifsc = extract_accno_ifsc(pdf)

                fetched_acc_num=acc_number_ifsc["acc"]

                if name_entities:
                    for entity in name_entities:
                        if fetched_name=="":
                            fetched_name=entity

                if fetched_name != "":
                    ner_results["Name"].append(fetched_name)
                else:
                    ner_results["Name"].append(f"Person {person_count}")
                
                if fetched_acc_num != "":
                    ner_results["Acc Number"].append(fetched_acc_num)
                else:
                    ner_results["Acc Number"].append("XXXXXXXXXXX")
            print("Ner results", ner_results)
            # Process bank statements

            # Check by account number that the bank statement is already processed or not
            # get all the account numbers from the json
            cases = load_all_case_data()
            cases_present_in = []
            for case in cases:
                acc_numbers = case["individual_names"]["Acc Number"]
                for acc_number in acc_numbers:
                    if acc_number in ner_results["Acc Number"]:
                        print("Bank statement with account number", acc_number, "is already processed, refer case ID - ", case["case_id"])
                        cases_present_in.append(case["case_id"])
            
            if len(cases_present_in)>0:
                # For message
                msg_box = QMessageBox(self)
                msg_box.setStyleSheet("""
                    QMessageBox QLabel {
                        color: black;
                    }
                """)
                msg_box.setWindowTitle("Warning")
                case_ids = ", ".join(cases_present_in)
                msg_box.setText(f"Bank statement with account number {acc_number} is already processed earlier, please refer case ID/IDs- {case_ids}")
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.exec()

            converter = CABankStatement(bank_names, pdf_paths, password, start_date, end_date, self.case_id, progress_data,ner_results)
            result = converter.start_extraction()

        
            
            group_of_similar_entities = self.get_similar_names(self.case_id,result)
            len_similar_groups = len(group_of_similar_entities["original_groups"])
            # Save the results
            saved_case_data = save_case_data(self.case_id, pdf_paths, start_date, end_date, ner_results)
            print("Case data saved", saved_case_data)
            save_result(self.case_id, result)
            print("Result saved ")
            update_serial_number_history(self.custom_serial_number.text())
            print("Serial number updated", self.serial_number)

            # Update the table
            self.create_recent_reports_table()
            
            # For success message
            msg_box = QMessageBox(self)
            msg_box.setStyleSheet("""
               QMessageBox {
                    background-color: #ecf0f1;
                }
                QMessageBox QLabel {
                    color: #1e293b;
                    font-size: 14px;
                    padding: 10px;
                }
                QPushButton {{
                    background-color: #3498db;
                    color: #FFFFFF;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 100px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color:#3498db ;
                }}
            """)
            msg_box.setWindowTitle("Success")
            msg_box.setText(f"Form submitted and processed successfully! Found {len_similar_groups} similar groups, please check the case dashboard and merge the similar groups.")
            msg_box.setIcon(QMessageBox.Icon.NoIcon)
            msg_box.exec()

            if len(result["pdf_paths_not_extracted"]) > 0:
                # For error message
                msg_box = QMessageBox(self)
                msg_box.setStyleSheet("""
                    QMessageBox QLabel {
                        color: black;
                    }
                """)
                msg_box.setWindowTitle("Exception")
                pdf_paths = ", ".join(result["pdf_paths_not_extracted"])
                msg_box.setText(f"Following Bank statements are not processed due to some exception - {pdf_paths}")
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.exec()

        except Exception as e:
            
            print("An error occurred while processing:", e) 
            # For error message
            msg_box = QMessageBox(self)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QMessageBox QLabel {
                    color: black;
                }
            """)
            msg_box.setWindowTitle("Error")
            print(e)
            msg_box.setText(f"An error occurred while processing: {str(e)}")
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.exec()

        finally:
            # Always clean up the spinner
            if hasattr(self, 'spinner_movie'):
                self.spinner_movie.stop()
            if hasattr(self, 'spinner_label'):
                self.spinner_label.hide()
                self.spinner_label.deleteLater()
                
            # make the form empty
            self.selected_files = []
            self.file_display.setText("")
            serial_number = get_last_serial_number()
            self.serial_number = self.process_serial_number(serial_number)
            self.custom_serial_number.setText(self.serial_number)
            self.update_case_id()
            
            # self.password.setText("")
            # self.start_date.setDate(QDate.currentDate())
            # self.end_date.setDate(QDate.currentDate())
            # self.case_id = "CA_ID_"+''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
            # self.case_id.setText(str(self.case_id))

            end = time.time()
            print("Time taken to process the form", end-start)

            self.update_table_data()
            global_signal_manager.update_table.emit(self.case_id)



    def create_label(self, text):
        label = QLabel(text)
        label.setFont(QFont("Arial", 14))
        label.setStyleSheet("""
            QLabel {
                color: #34495e;
                padding: 0px;
                margin-bottom: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        return label

    def create_labeled_field(self, label_text, widget):
        layout = QVBoxLayout()
        label = self.create_label(label_text)
        layout.addWidget(label)
        layout.addWidget(widget)
        return layout
    
        
    def get_similar_names(self,case_id,data):
        """Get similar names groups for a given case ID"""
        print("case_id name manager groups",case_id)
        # merged_names_object = find_merge_name_object(case_id)
        # data = load_result(case_id)

        group_of_similar_entities = None

        process_df = data["cummalative_df"]["process_df"]
        unique_values = extract_unique_names_and_entities(process_df)
        similar_groups = group_similar_entities(unique_values)

        obj = {
            "case_id":case_id,
            "original_groups":similar_groups,
            "merged_groups":[],
            "unselected_groups":[],
            "final_merged_status":False
        }

        create_name_merge_object(obj)
        group_of_similar_entities = obj

        return group_of_similar_entities
        
    def update_recent_report_table(self):
            self.recent_reports_table.update_table_data()

