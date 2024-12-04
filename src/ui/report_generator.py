from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget,QMessageBox, QVBoxLayout, QDialog,QFormLayout, QLineEdit, QPushButton, QDateEdit,QMainWindow, QTabWidget,QApplication, QLabel, QFrame, QScrollArea, QHBoxLayout, QTableWidget, QFileDialog,QTableWidgetItem, QHeaderView)
from PyQt6.QtGui import QFont,QColor,QBrush
from PyQt6.QtCore import QDate, Qt
from ..apps.report.controllers import *
import sys
from ..utils.CA_Statement_Analyzer import CABankStatement
from ..utils.json_logic import *
import random
import string
from .case_dashboard import CaseDashboard
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, pyqtSlot, QObject,QTimer
from ..utils.ner_model import pdf_to_name
from PyQt6.QtGui import QMovie
import time
from ..utils.refresh import add_pdf_extraction
from ..utils.json_logic import get_process_df

class WebBridge(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    @pyqtSlot(str)
    def caseIdClicked(self, case_id):
        self.parent.handle_case_id(case_id)

    @pyqtSlot(str, str)
    def uploadAdditionalPdf(self, row, case_id):
        self.parent.handle_upload_additional_pdf(row, case_id)

    @pyqtSlot(str)
    def log(self, message):
        print("JavaScript Log:", message)

class CustomWebPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        # print(f"JS Console ({level}): {message} [Line {lineNumber}] [{sourceID}]")
        print(f"JS Console conntected")



# Report Generator
class ReportGeneratorTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_files = []  # Store selected files
        self.case_id = "CA_ID_"+''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
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
        
        self.case_id_widget = QLineEdit()
        self.case_id_widget.setText(str(self.case_id))
        self.case_id_widget.setReadOnly(True)
        self.case_id_widget.setPlaceholderText("Auto-generate ID")
        self.case_id_widget.setStyleSheet("""
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
        case_id_layout.addWidget(self.case_id_widget)
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
                        color: blue;
                        cursor: pointer;
                        text-decoration: underline;
                    }
                    .search-container {
                        margin: 20px 0;
                        padding: 10px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }
                    .search-input {
                        width: 300px;
                        padding: 10px;
                        border: 2px solid #3498db;
                        border-radius: 5px;
                        font-size: 14px;
                        outline: none;
                        transition: border-color 0.3s;
                    }
                    .search-input:focus {
                        border-color: #2980b9;
                    }
                    .pagination {
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        margin-top: 20px;
                        gap: 10px;
                    }
                    .pagination button {
                        padding: 8px 16px;
                        background-color: #3498db;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        font-weight: bold;
                    }
                    .pagination button:disabled {
                        background-color: #bdc3c7;
                        cursor: not-allowed;
                    }
                    .pagination span {
                        font-weight: bold;
                        color: #333333;
                    }
                    .no-results {
                        text-align: center;
                        padding: 20px;
                        color: #666;
                        font-style: italic;
                    }
                </style>
                <script>
                    let bridge = null;
                    let initialized = false;
                    let filteredData = [];
                    const rowsPerPage = 10;
                    let currentPage = 1;

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
                    
                    function uploadAdditionalPdf(row, caseId) {
                        if (bridge) {
                            bridge.log("Uploading PDF for case: " + caseId);
                            bridge.uploadAdditionalPdf(row, caseId);
                        }
                    }
                    
                    function handleSearch() {
                        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
                        
                        filteredData = window.tableData.filter(report => {
                            return report.date.toLowerCase().includes(searchTerm) ||
                                report.case_id.toLowerCase().includes(searchTerm) ||
                                report.report_name.toLowerCase().includes(searchTerm);
                        });
                        currentPage = 1;
                        updateTable();
                    }

                    function updateTable(data) {
                        if (!initialized) {
                            bridge.log("Table update called before initialization");
                            return;
                        }

                        if (data) {
                            window.tableData = data;
                            filteredData = [...data];
                        }
                        const totalPages = Math.ceil(filteredData.length / rowsPerPage);
                        const start = (currentPage - 1) * rowsPerPage;
                        const end = start + rowsPerPage;
                        const pageData = filteredData.slice(start, end);
                        
                        const tbody = document.getElementById('tableBody');
                        tbody.innerHTML = '';

                        if (filteredData.length === 0) {
                            tbody.innerHTML = `
                                <tr>
                                    <td colspan="5" class="no-results">No matching results found</td>
                                </tr>
                            `;
                        } else {
                            pageData.forEach((report, index) => {
                                const row = document.createElement('tr');
                                row.innerHTML = `
                                    <td>${start +index + 1}</td>
                                    <td>${report.date}</td>
                                    <td class="case-id" onclick="caseIdClicked('${report.case_id}')">${report.case_id}</td>
                                    <td>${report.report_name}</td>
                                    <td>
                                        <button class="upload-btn" onclick="uploadAdditionalPdf(${index}, '${report.case_id}')">
                                            Add PDF
                                        </button>
                                    </td>
                                `;
                                tbody.appendChild(row);
                            });
                        }
                        document.getElementById('pageInfo').textContent = filteredData.length > 0 ? 
                            `Page ${currentPage} of ${totalPages}` : '';
                        document.getElementById('prevBtn').disabled = currentPage === 1;
                        document.getElementById('nextBtn').disabled = currentPage === totalPages || filteredData.length === 0;
                    }
                    function nextPage() {
                        const totalPages = Math.ceil(filteredData.length / rowsPerPage);
                        if (currentPage < totalPages) {
                            currentPage++;
                            updateTable();
                        }
                    }

                    function previousPage() {
                        if (currentPage > 1) {
                            currentPage--;
                            updateTable();
                        }
                    }
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
                    function updateTableData(data) {
                        if (!initialized) {
                            bridge.log("Table update called before initialization");
                            return;
                        }
                        bridge.log("Updating table with data: " + JSON.stringify(data));
                        tableData = data;
                        filteredData = [...tableData];
                        updateTable();
                    }

                </script>
            </head>
            <body>
                <div class="search-container">
                    <input type="text" 
                        id="searchInput" 
                        class="search-input" 
                        placeholder="Search..."
                        oninput="handleSearch()">
                </div>
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
                <div class="pagination">
                    <button id="prevBtn" onclick="previousPage()">Previous</button>
                    <span id="pageInfo"></span>
                    <button id="nextBtn" onclick="nextPage()">Next</button>
                </div>
            </body>
            </html>
            """
            
            # Load the HTML content
            self.web_view.setHtml(html_content)
            self.web_view.minimumHeight = 1000
            
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
 
    def handle_case_id(self, case_id):
        # Create and configure the spinner
        # spinner_label = QLabel(self)
        # spinner_movie = QMovie("assets/spinner.gif")
        # spinner_label.setMovie(spinner_movie)
        # spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # # Style and size the spinner
        # spinner_label.setFixedSize(100, 100)
        # spinner_label.setStyleSheet("""
        #     QLabel {
        #         background-color: rgba(255, 255, 255, 200);
        #         border-radius: 10px;
        #     }
        # """)
        
        # # Center the spinner in the parent widget
        # spinner_label.move(
        #     (self.width() - spinner_label.width()) // 2,
        #     (self.height() - spinner_label.height()) // 2
        # )
        
        # # Show the spinner and start animation
        # spinner_label.show()
        # spinner_movie.start()
        
        # Create the dialog first but don't show it yet
        self.new_window = QDialog(self)
        self.new_window.setWindowTitle(f"Case Dashboard - Case {case_id}")
        self.new_window.setModal(False)
        self.new_window.setWindowFlags(
            self.new_window.windowFlags() |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        self.new_window.setMinimumSize(1000, 800)
        
        try:
            # Create a layout for the dialog
            layout = QVBoxLayout()
            self.new_window.setLayout(layout)
            
            # Create the case dashboard with a loading callback
            case_dashboard = CaseDashboard(case_id=case_id)
            layout.addWidget(case_dashboard)
            self.new_window.showMaximized()
            # # Add a method to the case dashboard to signal when loading is complete
            # def on_dashboard_ready():
            #     # Stop and cleanup the spinner
            #     spinner_label.movie().stop()
            #     spinner_label.hide()
            #     spinner_label.deleteLater()
                
            #     # Show the window now that data is loaded
            #     layout.addWidget(case_dashboard)
            #     self.new_window.showMaximized()
            
            # # Connect the loading complete signal if CaseDashboard has one
            # if hasattr(case_dashboard, 'loading_complete'):
            #     case_dashboard.loading_complete.connect(on_dashboard_ready)
            # else:
            #     # If CaseDashboard doesn't have a loading signal, 
            #     # we'll need to modify CaseDashboard to add it
            #     print("Warning: CaseDashboard should implement loading_complete signal")
            #     on_dashboard_ready()
                
        except Exception as e:
            # Handle any errors and clean up
            print(e)
            print(f"Error creating case dashboard: {str(e)}")
            # spinner_label.movie().stop()
            # spinner_label.hide()
            # spinner_label.deleteLater()
            self.new_window.deleteLater()
            # QMessageBox.critical(
            #     self,
            #     "Error",
            #     f"Failed to open case dashboard: {str(e)}",
            # )
            msg_box = QMessageBox(self)
            msg_box.setStyleSheet("""
                
                QMessageBox QLabel {
                    color: black;
                }
            """)
            msg_box.setWindowTitle("Warning")
            msg_box.setText(f"Failed to open case dashboard: {str(e)}")
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.exec()
            
    def handle_upload_additional_pdf(self, row, case_id):
        file_names, _ = QFileDialog.getOpenFileNames(
            self,
            "Upload PDF Report",
            "",
            "Supported Files (*.pdf *.xlsx *.xls);;PDF Files (*.pdf);;Excel Files (*.xlsx *.xls)"
        )
        
        if file_names:
            try:
                # Add your file handling logic here
                print(f"Uploading PDF for Case ID: {case_id}")
                print(f"Selected file: {file_names}")

                pdf_paths = file_names
                passwords = [""]
                start_date = [""]
                end_date = [""]
            
                bank_names = []
                # For each path in pdf_paths, assign a unique name as A,B,C etc
                for i in range(len(pdf_paths)):
                    bank_names.append(chr(65 + i))
                    # if not password_provided:
                    #     password.append("")
                    # if not start_date_provided:
                    #     start_date.append("")
                    # if not end_date_provided:
                    #     end_date.append("")

                process_df = get_process_df(case_id)


                ner_results = {
                    "Name": [],
                    "Acc Number": []
                }

                # Process PDFs with NER
                for pdf in pdf_paths:
                    result = pdf_to_name(pdf)
                    for entity in result:
                        if entity["label"] == "PER":
                            ner_results["Name"].append(entity["text"])
                        elif entity["label"] == "ACC_NO":
                            ner_results["Acc Number"].append(entity["text"])
                            
                print("Ner results after additional pdf ", ner_results)
                case_data = load_case_data(case_id)

                # case_data["file_names"] =+ pdf_paths
                
                for file in pdf_paths:
                    case_data["file_names"].append(file)

                # Add new data to the existing dictionary
                for key, value in ner_results.items():
                    if key in case_data["individual_names"]:
                        case_data["individual_names"][key].extend(value)  # Append the new list to the existing list
                    else:
                        case_data["individual_names"][key] = value  # Add the new key-value pair if the key doesn't exist                print("case data",case_data)

                response = add_pdf_extraction(bank_names,pdf_paths,passwords,start_date,end_date,case_id,process_df)
                data = load_result(case_id)
                existing_keys = list(data["single_df"].keys())
                
                print("response_single_df ", response["single_df"])

                for key,value in response["single_df"].items():
                   
                    next_letter = chr(65 + len(existing_keys)) 
                    next_key = f"{next_letter}{len(existing_keys)}"
                    print("next key - ",next_key)
                    data["single_df"][next_key] = value
                
                data["cummalative_df"] = response["cummalative_df"]

               
                save_result(case_id,data)
                update_case_data(case_id, case_data)
                
                success_message = f'<p style="color: black;">PDF successfully uploaded for Case ID: {case_id}</p>'
                QMessageBox.information(
                    self,
                    "Success",
                    success_message
                )
                
            except Exception as e:
                print(e)
                msg_box = QMessageBox(self)
                msg_box.setStyleSheet("""
                    
                    QMessageBox QLabel {
                        color: black;
                    }
                """)
                msg_box.setWindowTitle("Warning")
                msg_box.setText(f"Failed to upload PDF: {str(e)}")
                msg_box.setIcon(QMessageBox.Icon.Critical)
                msg_box.exec()

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

    def submit_form_spinner(self):
            # Create and configure spinner
            self.spinner_label = QLabel(self)
            self.spinner_movie = QMovie("assets/spinner.gif")
            self.spinner_label.setMovie(self.spinner_movie)
            self.spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.spinner_label.setFixedSize(100, 100)
            self.spinner_label.setStyleSheet("""
                QLabel {
                    background-color: rgba(255, 255, 255, 200);
                    border-radius: 10px;
                }
            """)

            # Center the spinner in the parent widget
            self.spinner_label.move(
                (self.width() - self.spinner_label.width()) // 2,
                (self.height() - self.spinner_label.height()) // 2,
            )

            # Show and start spinner
            self.spinner_label.show()
            self.spinner_movie.start()

            # Create a QTimer to process the form in the next event loop iteration
            # start the timer
            QTimer.singleShot(100, self.process_form)
            
    
    def process_form(self):
        start = time.time()

        try:
            # Get the form data
            CA_ID = self.case_id
            pdf_paths = self.selected_files
            password = self.password.text()
            
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

            # Check if start_date is same as today
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
            for pdf in pdf_paths:
                result = pdf_to_name(pdf)
                for entity in result:
                    if entity["label"] == "PER":
                        ner_results["Name"].append(entity["text"])
                    elif entity["label"] == "ACC_NO":
                        ner_results["Acc Number"].append(entity["text"])
                        
            print("Ner results", ner_results)
            # Process bank statements

            # Check by account number that the bank statement is already processed or not
            # get all the account numbers from the json
            cases = load_all_case_data()
            for case in cases:
                acc_numbers = case["individual_names"]["Acc Number"]
                for acc_number in acc_numbers:
                    if acc_number in ner_results["Acc Number"]:
                        print("Bank statement with account number", acc_number, "is already processed, refer case ID - ", case["case_id"])
                        # For error message
                        msg_box = QMessageBox(self)
                        msg_box.setStyleSheet("""
                         
                            QMessageBox QLabel {
                                color: black;
                            }
                        """)
                        msg_box.setWindowTitle("Warning")
                        case_id = case["case_id"]
                        msg_box.setText(f"Bank statement with account number {acc_number} is already processed earlier, please refer case ID - {case_id}")
                        msg_box.setIcon(QMessageBox.Icon.Warning)
                        msg_box.exec()

            converter = CABankStatement(bank_names, pdf_paths, password, start_date, end_date, CA_ID, progress_data)
            result = converter.start_extraction()

            # Save the results
            save_case_data(CA_ID, pdf_paths, start_date, end_date, ner_results)
            save_result(CA_ID, result)

            # Update the table
            self.create_recent_reports_table()

            # For success message
            msg_box = QMessageBox(self)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                }
                QMessageBox QLabel {
                    color: black;
                }
            """)
            msg_box.setWindowTitle("Success")
            msg_box.setText("Form submitted and processed successfully!")
            msg_box.setIcon(QMessageBox.Icon.NoIcon)
            msg_box.exec()

        except Exception as e:
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
            self.password.setText("")
            self.start_date.setDate(QDate.currentDate())
            self.end_date.setDate(QDate.currentDate())
            self.case_id = "CA_ID_"+''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
            self.case_id.setText(str(self.case_id))

            end = time.time()
            print("Time taken to process the form", end-start)

            self.update_table_data()

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