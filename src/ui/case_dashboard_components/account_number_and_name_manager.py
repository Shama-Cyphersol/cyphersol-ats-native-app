import sys
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QMessageBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot, QTimer
from ...utils.json_logic import load_case_data,update_case_data,get_process_df,update_process_df
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl
from ...utils.refresh import refresh_name_n_acc_number
BLUE_COLOR = "#3498db"  
WHITE_COLOR = "#FFFFFF"
BACKGROUND_COLOR = "#f8fafc"  # Light gray background
HOVER_BLUE = "#3498db"  
TEXT_COLOR = "#1e293b"  # Darker text for better readability
BORDER_COLOR = "#cbd5e1"  # Subtle border color
GROUP_BOX_BG = "#f1f5f9"  # Light background for group boxes
RED_COLOR = "#e74c3c"

class WebBridge(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    @pyqtSlot(str)
    def log(self, message):
        print(f"JS Log: {message}")

    @pyqtSlot(str)
    def handleAction(self, case_id):
        print(f"Action triggered for Case ID: {case_id}")

    @pyqtSlot(str)
    def handle_submit_bridge(self, data):
        self.parent.handle_submit(data)
        


class AccountNumberAndNameManager(QMainWindow):
    def __init__(self, case_id,refresh_case_dashboard):
        super().__init__()
        self.case_id = case_id
        self.refresh_case_dashboard = refresh_case_dashboard
        self.data = load_case_data(case_id)
        
        print("Data:", self.data)

        self.setWindowTitle("PDF Table Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Main widget
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Create web view
        self.web_view = QWebEngineView()
        main_layout.addWidget(self.web_view)

        # Create custom web page and channel
        self.web_page = QWebEnginePage(self.web_view)
        self.web_view.setPage(self.web_page)
        
        # Web channel setup
        self.channel = QWebChannel()
        self.web_page.setWebChannel(self.channel)
        
        # Bridge setup
        self.bridge = WebBridge(self)
        self.channel.registerObject('bridge', self.bridge)

        # Generate HTML content
        html_content = self.generate_html_table()
        
        # Load HTML content
        self.web_view.setHtml(html_content, QUrl.fromLocalFile(sys.path[0] + '/'))
        
        # # submit Button 
        # submit_button_container = QHBoxLayout()
        # submit_button_container.addStretch()
        # submit_button = QPushButton("Make Changes")
        # submit_button.setStyleSheet(f"""
        #     QPushButton {{
        #         background-color: {BLUE_COLOR};
        #         color: {WHITE_COLOR};
        #         border: none;
        #         padding: 10px 20px;
        #         border-radius: 6px;
        #         font-weight: bold;
        #         font-size: 14px;
        #         min-width: 200px;
        #     }}
        #     QPushButton:hover {{
        #         background-color: {HOVER_BLUE};
        #     }}
        #     QPushButton:pressed {{
        #         background-color: {BLUE_COLOR};
        #         transform: translateY(1px);
        #     }}
        #     QPushButton:disabled {{
        #         background-color: #94a3b8;
        #         color: #e2e8f0;
        #     }}
        # """)
        # submit_button.clicked.connect(self.handle_submit)
        # # submit_button_container.addWidget(submit_button)
        # # submit_button_container.addStretch()

        # # Create a layout for the submit button to center it
        # submit_button_layout = QHBoxLayout()
        # submit_button_layout.addStretch()
        # submit_button_layout.addWidget(submit_button)
        # submit_button_layout.addStretch()

        # # Add some bottom padding
        # main_layout.addLayout(submit_button_layout)
        # main_layout.addSpacing(20)  # Add some bottom padding
        

    def generate_html_table(self):
        def generate_html_table_rows():
            rows = []
            for i, (path, name, acc_num) in enumerate(zip(
                self.data['file_names'],
                self.data['individual_names']['Name'], 
                self.data['individual_names']['Acc Number']
            )):
                row = f"""
                <tr>
                    <td>{i+1}</td>
                    <td>{path}</td>
                    <td contenteditable="true" class="editable">{name}</td>
                    <td contenteditable="true" class="editable">{acc_num}</td>
                </tr>
                """
                rows.append(row)
            return ''.join(rows)

        # Prepare data for HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <style>
                 body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    display: flex;
                    flex-direction: column;
                    height: 90vh;
                }}
                .table-container {{
                    flex-grow: 1;
                    overflow-y: auto;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    background-color: white;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    border-radius: 8px;
                    overflow: hidden;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #e0e0e0;
                    text-align:center;
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                    text-transform: uppercase;
                }}
                tr:hover {{
                    background-color: #f1f8ff;
                }}
                .editable {{
                    border: 1px solid #34495e;
                    border-radius: 4px;
                    padding: 5px;
                    transition: all 0.3s ease;
                }}
                .editable:focus {{
                    outline: none;
                    border-color: #2980b9;
                    box-shadow: 0 0 5px rgba(52,152,219,0.5);
                }}
                .submit-container {{
                    display: flex;
                    justify-content: center;
                    padding: 20px 0;
                }}
                #submitButton {{
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 14px;
                    min-width: 200px;
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                }}
                #submitButton:hover {{
                    background-color: #2980b9;
                }}
            </style>
            <script>
                let bridge = null;
                document.addEventListener('DOMContentLoaded', function() {{
                    new QWebChannel(qt.webChannelTransport, function(channel) {{
                        bridge = channel.objects.bridge;
                    }});

                    // Add event listener to submit button
                    document.getElementById('submitButton').addEventListener('click', submitChanges);
                }});

                function handleAction(caseId) {{
                    if (bridge) {{
                        bridge.log("Action for: " + caseId);
                        bridge.handleAction(caseId);
                    }}
                }}

                 function submitChanges() {{
                    let rows = document.querySelectorAll('table tbody tr');
                    let data = [];
                    rows.forEach(row => {{
                        let cells = row.querySelectorAll('td');
                        data.push({{
                            srNo: cells[0].textContent,
                            pdfPath: cells[1].textContent,
                            name: cells[2].textContent,
                            accNumber: cells[3].textContent
                        }});
                    }});
                    
                    if (bridge) {{
                        bridge.handle_submit_bridge(JSON.stringify(data));
                    }}
                }}
            </script>
        </head>
        <body>
             <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Sr No</th>
                            <th>PDF Path</th>
                            <th>Name</th>
                            <th>Account Number</th>
                        </tr>
                    </thead>
                    <tbody>
                        {generate_html_table_rows()}
                    </tbody>
                </table>
            </div>
            <div class="submit-container">
                <button id="submitButton">Make Changes</button>
            </div>
        </body>
        </html>
        """
        return html
    
    def handle_submit(self,data):
        # Show confirmation dialog
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("Confirm Merge")
        msg.setText(f"Are you sure you want to make these changes?\n\n")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet(f"""
         
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 14px;
                padding: 10px;
            }}
            QPushButton {{
                background-color: {BLUE_COLOR};
                color: {WHITE_COLOR};
                border: none;
                padding: 5px 10px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {HOVER_BLUE};
            }}
        """)
        
        reply = msg.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            # Execute JavaScript to retrieve table data
            # self.web_view.page().runJavaScript("""
            #     (function() {
            #         let rows = document.querySelectorAll('table tbody tr');
            #         let data = [];
            #         rows.forEach(row => {
            #             let cells = row.querySelectorAll('td');
            #             data.push({
            #                 srNo: cells[0].textContent,
            #                 pdfPath: cells[1].textContent,
            #                 name: cells[2].textContent,
            #                 accNumber: cells[3].textContent
            #             });
            #         });
            #         return JSON.stringify(data);
            #     })();
            # """, self.process_submitted_data)
            self.process_submitted_data(data)
    
    def process_submitted_data(self, json_data):
        # Parse the JSON data received from JavaScript
        try:
            data = json.loads(json_data)
            # old data
            
            # Update the original data
            updated_names = []
            updated_acc_numbers = []
            
            for row in data:
                updated_names.append(row['name'])
                updated_acc_numbers.append(row['accNumber'])
            
            

            print("Old Data:", self.data)

            # create two dict with old name : new name and old acc number : new acc number
            old_name_new_name = dict(zip(self.data['individual_names']['Name'], updated_names))
            old_acc_num_new_acc_num = dict(zip(self.data['individual_names']['Acc Number'], updated_acc_numbers))

            # remove ones which are same
            old_name_new_name = {k: v for k, v in old_name_new_name.items() if k != v}
            old_acc_num_new_acc_num = {k: v for k, v in old_acc_num_new_acc_num.items() if k != v}

            print("Old Name : New Name", old_name_new_name)
            print("Old Acc Number : New Acc Number", old_acc_num_new_acc_num)

            # Update the original data dictionary
            self.data['individual_names']['Name'] = updated_names
            self.data['individual_names']['Acc Number'] = updated_acc_numbers
            

            response = update_case_data(self.case_id,self.data)
            self.refresh_case_dashboard(new_case_data=self.data,source="AccountNumberAndNameManager")
            print("Updated Data:", self.data)

            process_df = get_process_df(self.case_id)
            new_process_df = refresh_name_n_acc_number(process_df,old_name_new_name)
            update_process_df(self.case_id,new_process_df)

            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.NoIcon)
            msg.setWindowTitle("Success")
            msg.setText("Changes have been saved successfully.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setStyleSheet(f"""
               
                QLabel {{
                    color: {TEXT_COLOR};
                    font-size: 14px;
                    padding: 10px;
                }}
                QPushButton {{
                    background-color: {BLUE_COLOR};
                    color: {WHITE_COLOR};
                    border: none;
                    padding: 5px 10px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 100px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: {HOVER_BLUE};
                }}
            """)
            
            msg.exec()
            # Optional: Show a success message
            # QMessageBox.information(self, "Success", "Changes have been saved successfully.")
        
        except json.JSONDecodeError:
            # QMessageBox.warning(self, "Error", "Failed to parse updated data.")
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error")
            msg.setText("Failed to parse updated data.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setStyleSheet(f"""
               
                QLabel {{
                    color: {TEXT_COLOR};
                    font-size: 14px;
                    padding: 10px;
                }}
                QPushButton {{
                    background-color: {BLUE_COLOR};
                    color: {WHITE_COLOR};
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 100px;
                }}
                QPushButton:hover {{
                    background-color: {HOVER_BLUE};
                }}
            """)
            
            msg.exec()
def main():
    # Sample data
    data = {
        "case_id": "CA_ID_Q7IHPUDFL4S81DU8",
        "file_names": [
            "C:/Users/qures/Downloads/Aiyaz hdf 23.pdf",
            "C:/Users/qures/Downloads/hdfc poojan.pdf",
            "C:/Users/qures/Downloads/aiyaz jupiter.pdf"
        ],
        "start_date": "-",
        "end_date": "-",
        "report_name": "Report_CA_ID_Q7IHPUDFL4S81DU8",
        "individual_names": {
            "Name": [
                "AIYAZ ANWAR QURESHI",
                "POOJAN MANISH VIG",
                "AIYAZ ANWAR QURESHI"
            ],
            "Acc Number": [
                "1637 PLOT NO",
                "50100575475700",
                "77770106311893"
            ]
        },
        "date": "30-11-2024"
    }

    app = QApplication(sys.argv)
    viewer = PDFTableViewer(data)
    viewer.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()