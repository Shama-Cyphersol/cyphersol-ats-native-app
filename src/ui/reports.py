from PyQt6.QtWidgets import QApplication, QVBoxLayout,QMessageBox, QDialog, QFileDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import pyqtSlot, QObject
from ..utils.json_logic import load_all_case_data, load_case_data


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
        for i, report in enumerate(reports_data):
            rows += f"""
                <tr>
                    <td>{i + 1}</td>
                    <td>{report.get('date', '')}</td>
                    <td>{report.get('case_id', '')}</td>
                    <td>{report.get('report_name', '')}</td>
                    <td><button onclick="qtWidget.viewDetails('{report.get('case_id', '')}')">View Details</button></td>
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
