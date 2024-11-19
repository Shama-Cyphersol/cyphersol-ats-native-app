from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget,QMessageBox, QVBoxLayout, QDialog,QFormLayout, QLineEdit, QPushButton, QDateEdit,QMainWindow, QTabWidget,QApplication, QLabel, QFrame, QScrollArea, QHBoxLayout, QTableWidget, QFileDialog,QTableWidgetItem, QHeaderView)
from PyQt6.QtGui import QFont,QColor,QBrush
from PyQt6.QtCore import QDate, Qt
from apps.report.controllers import *
import sys
from utils.CA_Statement_Analyzer import CABankStatement
from utils.json_logic import *
import random
import string
from .case_dashboard import CaseDashboard
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, pyqtSlot, QObject,QTimer


class WebBridge(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    @pyqtSlot(str)
    def caseIdClicked(self, case_id):
        self.parent.handle_case_id_clicked(case_id)

    @pyqtSlot(str, str)
    def uploadPdf(self, row, case_id):
        self.parent.handle_upload_pdf(row, case_id)

    @pyqtSlot(str)
    def log(self, message):
        print("JavaScript Log:", message)

class CustomWebPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print(f"JS Console ({level}): {message} [Line {lineNumber}] [{sourceID}]")


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
        if not hasattr(self, 'web_view'):
            # Create web view and custom page
            self.web_view = QWebEngineView()
            self.web_page = CustomWebPage(self.web_view)
            self.web_view.setPage(self.web_page)
            
            # Create and set up web channel
            self.channel = QWebChannel()
            self.web_page.setWebChannel(self.channel)
            
            # Create bridge and register it with the channel
            self.bridge = WebBridge(self)
            self.channel.registerObject('bridge', self.bridge)

            # HTML content with modern styling and QWebChannel integration
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 20px;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        background-color: white;
                        border-radius: 10px;
                        overflow: hidden;
                        box-shadow: 0 0 20px rgba(0,0,0,0.1);
                    }
                    th {
                        background-color: #3498db;
                        color: white;
                        font-weight: bold;
                        padding: 12px;
                        text-align: center;
                    }
                    td {
                        padding: 10px;
                        text-align: center;
                        border-bottom: 1px solid #eee;
                    }
                    tr:hover {
                        background-color: #f5f5f5;
                    }
                    .upload-btn {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        padding: 5px 15px;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 12px;
                    }
                    .upload-btn:hover {
                        background-color: #2980b9;
                    }
                    .case-id {
                        color: black;
                        cursor: pointer;
                        text-decoration: none;
                    }
                </style>
                <script>
                    let bridge = null;
                    let initialized = false;

                    function initWebChannel() {
                        return new Promise((resolve) => {
                            if (typeof qt !== 'undefined') {
                                new QWebChannel(qt.webChannelTransport, function(channel) {
                                    bridge = channel.objects.bridge;
                                    bridge.log("WebChannel initialized");
                                    resolve();
                                });
                            } else {
                                setTimeout(initWebChannel, 100);
                            }
                        });
                    }

                    function caseIdClicked(caseId) {
                        if (bridge) {
                            bridge.log("Clicking case ID: " + caseId);
                            bridge.caseIdClicked(caseId);
                        }
                    }
                    
                    function uploadPdf(row, caseId) {
                        if (bridge) {
                            bridge.log("Uploading PDF for case: " + caseId);
                            bridge.uploadPdf(row, caseId);
                        }
                    }
                    
                    function updateTable(data) {
                        if (!initialized) {
                            bridge.log("Table update called before initialization");
                            return;
                        }
                        bridge.log("Updating table with data: " + JSON.stringify(data));
                        
                        const tbody = document.getElementById('tableBody');
                        tbody.innerHTML = '';
                        
                        data.forEach((report, index) => {
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${index + 1}</td>
                                <td>${report.date}</td>
                                <td class="case-id" onclick="caseIdClicked('${report.case_id}')">${report.case_id}</td>
                                <td>${report.report_name}</td>
                                <td>
                                    <button class="upload-btn" onclick="uploadPdf(${index}, '${report.case_id}')">
                                        Add PDF
                                    </button>
                                </td>
                            `;
                            tbody.appendChild(row);
                        });
                    }

                    // Initialize when the document is loaded
                    document.addEventListener('DOMContentLoaded', async function() {
                        try {
                            await initWebChannel();
                            initialized = true;
                            bridge.log("Page fully initialized");
                            window.updateTableData && window.updateTableData();
                        } catch (error) {
                            console.error("Initialization error:", error);
                        }
                    });
                </script>
            </head>
            <body>
                <table>
                    <thead>
                        <tr>
                            <th>Sr no.</th>
                            <th>Date</th>
                            <th>Case ID</th>
                            <th>Report Name</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody">
                    </tbody>
                </table>
            </body>
            </html>
            """
            
            # Load the HTML content
            self.web_view.setHtml(html_content)
            
            # Wait for the page to load before updating table data
            def check_initialization():
                self.web_page.runJavaScript(
                    'typeof initialized !== "undefined" && initialized',
                    lambda result: self.update_table_data() if result else QTimer.singleShot(100, check_initialization)
                )
            
            # Start checking for initialization
            QTimer.singleShot(100, check_initialization)
            
            return self.web_view

    def update_table_data(self):
        recent_reports = load_all_case_data()
        json_data = json.dumps(recent_reports)
        
        # Store data in JavaScript and call updateTable
        js_code = f"""
            window.tableData = {json_data};
            if (typeof updateTable === 'function') {{
                updateTable(window.tableData);
            }} else {{
                window.updateTableData = function() {{
                    updateTable(window.tableData);
                }};
            }}
        """
        self.web_page.runJavaScript(js_code)

    def handle_case_id_clicked(self, case_id):
        print("Case ID clicked: ", case_id)
        cash_flow_network = CaseDashboard(case_id=case_id)
        
        # Create a new dialog
        self.new_window = QDialog(self)
        self.new_window.setWindowTitle(f"Case Dashboard - Case {case_id}")
        self.new_window.setModal(False)
        self.new_window.showMaximized()
        
        # Set window flags
        self.new_window.setWindowFlags(
            self.new_window.windowFlags() |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        # Set minimum size
        self.new_window.setMinimumSize(1000, 800)
        
        # Create layout and add widget
        layout = QVBoxLayout()
        layout.addWidget(cash_flow_network)
        self.new_window.setLayout(layout)
        
        # Show the window
        self.new_window.show()

    def handle_upload_pdf(self, row, case_id):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Upload PDF Report",
            "",
            "Supported Files (*.pdf *.xlsx *.xls);;PDF Files (*.pdf);;Excel Files (*.xlsx *.xls)"
        )
        
        if file_name:
            try:
                # Add your file handling logic here
                print(f"Uploading PDF for Case ID: {case_id}")
                print(f"Selected file: {file_name}")
                
                success_message = f'<p style="color: black;">PDF successfully uploaded for Case ID: {case_id}</p>'
                QMessageBox.information(
                    self,
                    "Success",
                    success_message
                )
            except Exception as e:
                error_message = f"Failed to upload PDF: {str(e)}"
                QMessageBox.critical(
                    self,
                    "Error",
                    error_message
                )

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
        password = self.password.text()
        print("password",password)

        password_provided = False
        start_date_provided = False
        end_date_provided = False

        if password == "": 
            password = [""]
        else:
            password_provided = True
            password = [password]

        start_date = self.start_date.date().toString("dd-MM-yyyy")
        end_date = self.end_date.date().toString("dd-MM-yyyy")

        # check if start_date is same as today
        if start_date == QDate.currentDate().toString("dd-MM-yyyy"):
            start_date = [""]
        else:
            start_date_provided = True
            start_date = [start_date]

        if end_date == QDate.currentDate().toString("dd-MM-yyyy"):
            end_date = [""]
        else:
            end_date_provided = True
            end_date = [end_date]
        

        bank_names = []
        # for each path in pdf_paths, assign a unique name as A,B,C etc
        for i in range(len(pdf_paths)):
            bank_names.append(chr(65 + i))
            if password_provided == False:
                password.append("")
            if start_date_provided == False:
                start_date.append("")
            if end_date_provided == False:
                end_date.append("")

        print ("CA_ID",CA_ID)
        print ("pdf_paths",pdf_paths)
        print ("passwords",password)
        print ("start_date",start_date)
        print ("end_date",end_date)
        print ("bank_names",bank_names)


        progress_data = {
            'progress_func': lambda current, total, info: print(f"{info} ({current}/{total})"),
            'current_progress': 10,
            'total_progress': 100
        }

        print("progress_data",progress_data)


        converter = CABankStatement(bank_names, pdf_paths, password, start_date, end_date, CA_ID, progress_data)
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
        self.create_recent_reports_table()


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