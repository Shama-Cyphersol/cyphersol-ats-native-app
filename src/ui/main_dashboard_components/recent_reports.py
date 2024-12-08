from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QWidget,QMessageBox, QVBoxLayout, QDialog,QFormLayout, QLineEdit, QPushButton, QDateEdit,QMainWindow, QTabWidget,QApplication, QLabel, QFrame, QScrollArea, QHBoxLayout, QTableWidget, QFileDialog,QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import QDate, Qt
# from apps.report.controllers import *
import sys
from ...utils.json_logic import *
import random
import string
from ..case_dashboard import CaseDashboard
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, pyqtSlot, QObject,QTimer
from src.utils.pdf_to_name_and_accno import pdf_to_name_and_accno
from PyQt6.QtGui import QMovie
import time
from ...utils.refresh import add_pdf_extraction
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot, QUrl
import json
from utils.pdf_to_name import extract_entities

class WebBridge(QObject):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    @pyqtSlot(str)
    def caseIdClicked(self, case_id):
        self.parent.handle_case_id(case_id)

    @pyqtSlot(str, str)
    def uploadAdditionalPdf(self, row, case_id):
        self.parent.handle_upload_additional_pdf(row, case_id)

    @pyqtSlot(str, str)
    def deleteCase(self, row, case_id):
        self.parent.handle_delete_case(row, case_id)

    @pyqtSlot(str)
    def log(self, message):
        print("JavaScript Log:", message)

class CustomWebPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        print(f"JS Console: {message}")

class RecentReportsTable:
    def __init__(self):
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
                    .delete-btn {
                        background-color: red;
                        color: white;
                        border: none;
                        padding: 5px 15px;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 12px;
                    }
                    .delete-btn:hover {
                        background-color: #c0392b;
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
                        return new Promise((resolve, reject) => {
                            if (typeof qt !== 'undefined') {
                                new QWebChannel(qt.webChannelTransport, function(channel) {
                                    try {
                                        bridge = channel.objects.bridge;
                                        bridge.log("WebChannel fully initialized");
                                        resolve();
                                    } catch (error) {
                                        console.error("WebChannel initialization error:", error);
                                        reject(error);
                                    }
                                });
                            } else {
                                console.log("qt is undefined, retrying...");
                                setTimeout(() => initWebChannel().catch(reject), 100);
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
                    function deleteCase(row, caseId) {
                        if (bridge) {
                            // Ask for confirmation before deleting
                            bridge.deleteCase(row, caseId);
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
                                            Add
                                        </button>
                                       <button class="delete-btn" onclick="deleteCase(${index}, '${report.case_id}')">
                                            Delete
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
        self.web_view.minimumHeight= 1000
        
        # Wait for the page to load before updating table data
        def check_initialization():
            self.web_page.runJavaScript(
                'typeof initialized !== "undefined" && initialized',
                lambda result: self.update_table_data() if result else QTimer.singleShot(100, check_initialization)
            )
        
        # Start checking for initialization
        QTimer.singleShot(100, check_initialization)

              
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
        self.new_window = QDialog()
        self.new_window.setStyleSheet("""
                background-color: white;
        """)
        self.new_window.setWindowTitle(f"Case Dashboard - Case {case_id}")
        self.new_window.setModal(False)
        self.new_window.setWindowFlags(
            self.new_window.windowFlags() |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowMaximizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        self.new_window.setMinimumSize(1000, 800)
        
        # try:
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
                
        # except Exception as e:
        #     # Handle any errors and clean up
        #     print(e)
        #     print(f"Error creating case dashboard: {str(e)}")
        #     # spinner_label.movie().stop()
        #     # spinner_label.hide()
        #     # spinner_label.deleteLater()
        #     self.new_window.deleteLater()
        #     # QMessageBox.critical(
        #     #     self,
        #     #     "Error",
        #     #     f"Failed to open case dashboard: {str(e)}",
        #     # )
        #     msg_box = QMessageBox()
        #     msg_box.setStyleSheet("""
                
        #         QMessageBox QLabel {
        #             color: black;
        #         }
        #     """)
        #     msg_box.setWindowTitle("Warning")
        #     msg_box.setText(f"Failed to open case dashboard: {str(e)}")
        #     msg_box.setIcon(QMessageBox.Icon.Warning)
        #     msg_box.exec()

    def update_table_data(self):
        try:
            recent_reports = load_all_case_data()
            
            if not recent_reports:
                print("No reports found!")
                return

            # Convert to JSON safely
            json_data = json.dumps(recent_reports)
            
            # Use JavaScript to update the table
            js_code = f"""
            (function() {{
                updateTableData({json_data});
            }})();
            """
            
            self.web_page.runJavaScript(js_code)
        except Exception as e:
            print(f"Error updating table data: {e}")

    def handle_delete_case(self, row, case_id):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.NoIcon)
        msg.setWindowTitle("Confirm Delete")
        msg.setText(f"Are you sure you want to delete case - {case_id} ?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: white;
            }}
            QMessageBox QLabel {{
                color: #1e293b;
            }}
            QLabel {{
                color: #1e293b;
                font-size: 14px;
                padding: 10px;
            }}
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
        
        reply = msg.exec()
        print("reply",reply)
        if reply == QMessageBox.StandardButton.Yes:
            print(f"Deleting case: {case_id}")
            delete_case_data(case_id)

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.NoIcon)
            msg.setWindowTitle("Success")
            msg.setText(f"Case - {case_id} deleted successfully")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setStyleSheet(f"""
                QMessageBox {{
                    background-color: white;
                }}
                QMessageBox QLabel {{
                    color: #1e293b;
                }}
                QLabel {{
                    color: #1e293b;
                    font-size: 14px;
                    padding: 10px;
                }}
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
            
            msg.exec()
            self.update_table_data()
        
            
    def handle_upload_additional_pdf(self, row, case_id):
        file_names, _ = QFileDialog.getOpenFileNames(
            None,
            "Upload PDF Report",
            "",
            "Supported Files (*.pdf *.xlsx *.xls);;PDF Files (*.pdf);;Excel Files (*.xlsx *.xls)"
        )

        
        
        if file_names:
            self.processing_popup = QMessageBox()
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
                person_count = 0
                for pdf in pdf_paths:
                    person_count+=1
                    result = pdf_to_name_and_accno(pdf)
                    entites = extract_entities(pdf)
                    fetched_name = ""
                    fetched_acc_num = ""

                    print("new ner result Entities:- ", entites)
                    print("old ner results:- ", result)

                    if entites:
                        for entity in entites:
                            if fetched_name=="":
                                fetched_name=entity

                    for entity in result:
                        if fetched_name=="" and entity["label"] == "PER":
                            fetched_name = entity["text"]
                            # ner_results["Name"].append(entity["text"])
                        if fetched_acc_num=="" and  entity["label"] == "ACC_NO":
                            fetched_acc_num = entity["text"]
                            # ner_results["Acc Number"].append(entity["text"])
                    
                    if fetched_name != "":
                        ner_results["Name"].append(fetched_name)
                    else:
                        ner_results["Name"].append(f"Person {person_count}")
                    
                    if fetched_acc_num != "":
                        ner_results["Acc Number"].append(fetched_acc_num)
                    else:
                        ner_results["Acc Number"].append("XXXXXXXXXXX")

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
                
                msg_box = QMessageBox()
                msg_box.setStyleSheet("""
                    QMessageBox {{
                        background-color: white;
                    }}
                    QMessageBox QLabel {{
                        color: black;
                    }}
                """)
                msg_box.setWindowTitle("Success")
                msg_box.setText(f"PDF successfully uploaded for Case ID: {case_id}")
                msg_box.setIcon(QMessageBox.Icon.NoIcon)
                msg_box.exec()

                self.processing_popup.close()
                self.processing_popup.hide()
                
            except Exception as e:
                print(e)
                msg_box = QMessageBox()
                msg_box.setStyleSheet("""
                    QMessageBox {{
                        background-color: white;
                    }}
                    QMessageBox QLabel {{
                        color: black;
                    }}
                """)
                msg_box.setWindowTitle("Warning")
                msg_box.setText(f"Failed to upload PDF: {str(e)}")
                msg_box.setIcon(QMessageBox.Icon.Critical)
                msg_box.exec()

    def get_web_view(self):
        return self.web_view