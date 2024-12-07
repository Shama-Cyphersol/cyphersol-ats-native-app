from PyQt6.QtWidgets import QApplication, QVBoxLayout,QMessageBox, QDialog, QFileDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import pyqtSlot, QObject
from ..utils.json_logic import load_all_case_data, load_case_data, get_process_df
from ..utils.refresh import create_excel_with_sheets
import os

class ReportsTab(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reports")
        self.setMinimumSize(900, 600)

        # Layout
        layout = QVBoxLayout()
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        self.setLayout(layout)

        # Set up QWebChannel
        self.channel = QWebChannel()
        self.channel.registerObject("qtWidget", self)  # Expose this object to JS
        self.web_view.page().setWebChannel(self.channel)

        # Load Reports Table
        self.load_reports_table()

    def load_reports_table(self):
        # Generate HTML for reports table
        reports_data = load_all_case_data()
        html = self.generate_reports_html(reports_data)
        self.web_view.setHtml(html)

    def generate_reports_html(self, reports_data):
        # Include the WebChannel setup in the HTML
        rows = ""
        # for i, report in enumerate(reports_data):
        #     rows += f"""
        #         <tr>
        #             <td>{i + 1}</td>
        #             <td>{report.get('date', '')}</td>
        #             <td>{report.get('case_id', '')}</td>
        #             <td>{report.get('report_name', '')}</td>
        #             <td><button onclick="qtWidget.viewDetails('{report.get('case_id', '')}')">View Details</button></td>
        #         </tr>
        #     """

        for i, report in enumerate(reports_data):
            rows += f"""
                <tr>
                    <td>{i + 1}</td>
                    <td>{report.get('date', '')}</td>
                    <td>{report.get('case_id', '')}</td>
                    <td>{report.get('report_name', '')}</td>
                    <td><button onclick="qtWidget.downloadAllinOneReport('{report.get('case_id', '')}')">Download Report</button></td>
                </tr>
            """

        html = f"""
            <html>
            <head>
                <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
                <script>
                    var qtWidget;
                    new QWebChannel(qt.webChannelTransport, function(channel) {{
                        qtWidget = channel.objects.qtWidget;
                    }});
                </script>
                <style>
                    body {{
                            font-family: Arial, sans-serif;
                            margin: 20px;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        background-color: white;
                        border-radius: 10px;
                        overflow: hidden;
                        box-shadow: 0 0 20px rgba(0,0,0,0.1);
                    }}
                    th {{
                        background-color: #3498db;
                        color: white;
                        font-weight: bold;
                        padding: 12px;
                        text-align: center;
                    }}
                    td {{
                        padding: 10px;
                        text-align: center;
                        border-bottom: 1px solid #eee;
                    }}
                    tr:hover {{
                        background-color: #f5f5f5;
                    }}
                    button {{
                        background-color: #3498db;
                        color: white;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 5px;
                        cursor: pointer;
                    }}
                    button:hover {{
                        background-color: #2980b9;
                    }}
                </style>
            </head>
            <body>
                <h1>Select a Case to download reports</h1>
                <table>
                    <thead>
                        <tr>
                            <th>Sr No.</th>
                            <th>Date</th>
                            <th>Case ID</th>
                            <th>Report Name</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </body>
            </html>
        """
        return html

    @pyqtSlot(str)
    def viewDetails(self, case_id):
        # Generate and load individuals table for the clicked case_id
        case_data = load_case_data(case_id)
        html = self.generate_individuals_html(case_id, case_data)
        self.web_view.setHtml(html)
    
    @pyqtSlot(str)
    def downloadAllinOneReport(self, case_id):
        folder_path = os.path.join(os.path.dirname(__file__),"..","data","reports")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = os.path.join(folder_path, f"case_{case_id}_report.xlsx")

        # check if the file already exists or not 
        if not os.path.exists(file_path):
            self.create_all_in_one_report(case_id, file_path)

        # make that file downloadable
        save_file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save  Report", 
            file_path, 
            "Excel Files (*.xlsx);"
        )
        if save_file_path:
            try:
                with open(file_path, 'rb') as f:
                    with open(save_file_path, 'wb') as f2:
                        f2.write(f.read())
                        
                msg_box = QMessageBox(self)
                msg_box.setStyleSheet("""
                    QMessageBox QLabel {
                        color: black;
                    }
                """)
                msg_box.setWindowTitle("Success")
                msg_box.setText(f"Report for case {case_id} has been saved to {save_file_path}")
                msg_box.setIcon(QMessageBox.Icon.NoIcon)
                msg_box.exec()
              
            except Exception as e:

                msg_box = QMessageBox(self)
                msg_box.setStyleSheet("""
                    QMessageBox QLabel {
                        color: black;
                    }
                """)
                msg_box.setWindowTitle("Download Failed")
                msg_box.setText(f"Could not save report: {str(e)}")
                msg_box.setIcon(QMessageBox.Icon.Warning)
                msg_box.exec()


    def create_all_in_one_report(self, case_id,file_path):
        # Generate and load individuals table for the clicked case_id
        process_df = get_process_df(case_id)
        create_excel_with_sheets(process_df,file_path)

    def generate_individuals_html(self, case_id, case_data):
        rows = ""
        for i, (name, acc) in enumerate(zip(case_data['individual_names']['Name'], case_data['individual_names']['Acc Number'])):
            rows += f"""
                <tr>
                    <td>{i + 1}</td>
                    <td>{name}</td>
                    <td>{acc}</td>
                    <td><button onclick="qtWidget.downloadReport('{name}', '{acc}')">Download Report</button></td>
                </tr>
            """

        html = f"""
            <html>
            <head>
                <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
                <script>
                    var qtWidget;
                    new QWebChannel(qt.webChannelTransport, function(channel) {{
                        qtWidget = channel.objects.qtWidget;
                    }});

                    function goBack() {{
                        qtWidget.goBack();
                    }}
                </script>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 20px;
                    }}
                    table {{
                        width: 100%;
                        border-collapse: collapse;
                        background-color: white;
                        border-radius: 10px;
                        overflow: hidden;
                        box-shadow: 0 0 20px rgba(0,0,0,0.1);
                    }}
                    th {{
                        background-color: #3498db;
                        color: white;
                        font-weight: bold;
                        padding: 12px;
                        text-align: center;
                    }}
                    td {{
                        padding: 10px;
                        text-align: center;
                        border-bottom: 1px solid #eee;
                    }}
                    tr:hover {{
                        background-color: #f5f5f5;
                    }}
                    button {{
                        background-color: #3498db;
                        color: white;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 5px;
                        cursor: pointer;
                    }}
                    .back-button {{
                        background-color: #3498db;
                        color: white;
                        border: none;
                        padding: 5px 20px;
                        margin:10px;
                        border-radius: 5px;
                        cursor: pointer;
                    }}
                    button:hover {{
                        background-color: #2980b9;
                    }}
                </style>
            </head>
            <body>
                <h2>Individuals in Case {case_id}</h2>
                <button class="back-button" onclick="goBack()">Back</button>
                <table>
                    <thead>
                        <tr>
                            <th>Sr No.</th>
                            <th>Individual Name</th>
                            <th>Account Number</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </body>
            </html>
        """
        return html
    
    @pyqtSlot()
    def goBack(self):
        self.load_reports_table()


    @pyqtSlot(str, str)
    def downloadReport(self, name, acc_number):
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Individual Report", 
            f"{name}_{acc_number}_report.pdf", 
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(f"Report for {name} (Account: {acc_number})\n")
                
                QMessageBox.information(
                    self, 
                    "Report Downloaded", 
                    f"Report for {name} has been saved to {file_path}"
                )
            except Exception as e:
                QMessageBox.warning(
                    self, 
                    "Download Failed", 
                    f"Could not save report: {str(e)}"
                )

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = ReportsTab()
    window.show()
    sys.exit(app.exec())
