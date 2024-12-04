from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from modules.dashboard_stats import *
import json
from PyQt6.QtWidgets import (QWidget,QMessageBox, QVBoxLayout, QDialog,QFormLayout, QLineEdit, QPushButton, QDateEdit,QMainWindow, QTabWidget,QApplication, QLabel, QFrame, QScrollArea, QHBoxLayout, QTableWidget, QFileDialog,QTableWidgetItem, QHeaderView)
from .case_dashboard import CaseDashboard
from PyQt6.QtCore import QDate, Qt
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSlot, QTimer
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebChannel import QWebChannel
from utils.json_logic import *


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
        # print(f"JS Console ({level}): {message} [Line {lineNumber}] [{sourceID}]")
        print(f"JS Console conntected")

class DashboardTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def get_stats_card_html(self):
        return f'''
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-value">{get_report_count()}</div>
                <div class="stat-label">Total Reports</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{get_monthly_report_count()}</div>
                <div class="stat-label">Monthly Reports</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{get_count_of_statement()}</div>
                <div class="stat-label">Total Statements</div>
            </div>
        </div>
        '''

    def get_table_html(self, recent_reports):
        html_content = '''
        <!DOCTYPE html>
        <html>
        <head>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <style>
                .table-container {
                    margin: 20px;
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                }
                .table-header {
                    text-align: center;
                    padding: 10px;
                    color: #2c3e50;
                    font-size: 1.2rem;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                .search-container {
                    margin: 10px;
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
                    position: sticky;
                    top: 0;
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
                let tableData = [];
                const rowsPerPage = 10;
                let currentPage = 1;
                let filteredData = [];

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
                                <td>${start + index + 1}</td>
                                <td>${report.date}</td>
                                <td class="case-id" onclick="caseIdClicked('${report.case_id}')">${report.case_id}</td>
                                <td>${report.report_name}</td>
                                <td>
                                    <button class="upload-btn" onclick="uploadPdf(${index}, '${report.case_id}')">
                                        Add 
                                    </button>
                                </td>
                            `;
                            tbody.appendChild(row);
                        });
                    }

                    document.getElementById('pageInfo').textContent = filteredData.length > 0 ? `Page ${currentPage} of ${totalPages}` : '';
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
            <div class="section">
                <div class="section-title">Recent Reports</div>
                <div class="table-container">
                   
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
                </div>
            </div>
        </body>
        </html>
        '''
        return html_content
    
    def update_table_data(self):
        try:
            recent_reports = self.get_recent_reports()  # Make sure this function exists
            self.initialize_table_data(recent_reports)
        except Exception as e:
            print(f"Error updating table data: {str(e)}")


    def get_chart_html(self, chart_data):
        return f'''
        <div class="section">
            <div class="section-title">Report Trends</div>
            <div class="chart-controls">
                <button onclick="toggleView('monthly')">Monthly View</button>
                <button onclick="toggleView('daily')">Daily View</button>
                <button onclick="resetZoom()">Reset</button>
            </div>
            
            <div class="chart-container">
                <canvas id="reportsChart"></canvas>
            </div>
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/hammer.js/2.0.8/hammer.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-zoom/2.0.0/chartjs-plugin-zoom.min.js"></script>

        <script>
            const dailyData = {json.dumps(chart_data['daily'])};
            const monthlyData = {json.dumps(chart_data['monthly'])};
            let currentView = 'monthly';
            let myChart;

            function initChart(data) {{
                const ctx = document.getElementById('reportsChart').getContext('2d');
                if (myChart) {{
                    myChart.destroy();
                }}
                
                myChart = new Chart(ctx, {{
                    type: 'line',
                    data: data,
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {{
                            mode: 'index',
                            intersect: false,
                        }},
                        plugins: {{
                            legend: {{
                                position: 'top'
                            }},
                            title: {{
                                display: true,
                                text: currentView === 'monthly' ? 'Monthly Report Trends' : 'Daily Report Trends'
                            }},
                            zoom: {{
                                limits: {{
                                    y: {{min: 0}},
                                }},
                                pan: {{
                                    enabled: true,
                                    mode: 'xy',
                                }},
                                zoom: {{
                                    wheel: {{
                                        enabled: true,
                                    }},
                                    pinch: {{
                                        enabled: true
                                    }},
                                    mode: 'xy',
                                    drag: {{
                                        enabled: true,
                                        backgroundColor: 'rgba(52, 152, 219, 0.3)',
                                        borderColor: 'rgb(52, 152, 219)',
                                        borderWidth: 1,
                                    }},
                                }}
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: 'Number of Reports'
                                }}
                            }},
                            x: {{
                                title: {{
                                    display: true,
                                    text: currentView === 'monthly' ? 'Month' : 'Date'
                                }},
                                ticks: {{
                                    maxRotation: 45,
                                    minRotation: 45
                                }}
                            }}
                        }}
                    }}
                }});
            }}

            function toggleView(view) {{
                currentView = view;
                const data = view === 'monthly' ? monthlyData : dailyData;
                initChart(data);
            }}

            function resetZoom() {{
                if (myChart) {{
                    myChart.resetZoom();
                }}
            }}

            // Initialize with monthly view
            initChart(monthlyData);
        </script>
        '''


    def get_styles(self):
        return '''
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f6fa;
                overflow: auto;
            }
            .dashboard-container {
                max-width: 100%;
                height: full;
                margin: 0 auto;
            }
            .title {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 20px;
            }
            .stats-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: white;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .stat-value {
                font-size: 36px;
                font-weight: bold;
                color: #3498db;
                margin: 10px 0;
            }
            .stat-label {
                font-size: 14px;
                color: #7f8c8d;
            }
            .section {
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .section-title {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 20px;
                text-align: bottom;
            }
            .table-container {
                overflow-x: auto;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            th, td {
                padding: 12px;
                text-align: center;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #3498db;
                color: white;
            }
            tr:hover {
                background-color: #f5f6fa;
            }
            .chart-container {
                height: 400px;
                position: relative;
            }
            @media screen and (max-width: 768px) {
                .stats-container {
                    grid-template-columns: 1fr;
                }
            }
            .chart-controls {
                text-align: right;
                margin: 10px 0;
            }
            .chart-controls button {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                margin: 0 5px;
                cursor: pointer;
                transition: background-color 0.3s ease;
                
            }
            .chart-controls button:hover {
                background-color: #2980b9;
            }
        '''

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        web_view = QWebEngineView()
        
        # Create and set up web channel
        self.web_page = CustomWebPage(web_view)
        web_view.setPage(self.web_page)
        
        self.channel = QWebChannel()
        self.web_page.setWebChannel(self.channel)
        
        # Create bridge and register it with the channel
        self.bridge = WebBridge(self)
        self.channel.registerObject('bridge', self.bridge)
        
        # Get data
        recent_reports = get_recent_reports()
        
        # Process reports data for both daily and monthly views
        status_by_date = {}
        for report in recent_reports:
            date = report.get("date", "Unknown")
            status = report["status"]
            
            if date not in status_by_date:
                status_by_date[date] = {}
            
            if status in status_by_date[date]:
                status_by_date[date][status] += 1
            else:
                status_by_date[date][status] = 1

        # Calculate monthly totals
        monthly_report_data = {}
        for date, statuses in status_by_date.items():
            month = date[:7]  # Get YYYY-MM
            if month not in monthly_report_data:
                monthly_report_data[month] = 0
            monthly_report_data[month] += sum(statuses.values())

        # Prepare chart data for both views
        chart_data = {
            'daily': {
                'labels': list(status_by_date.keys()),
                'datasets': [{
                    'label': 'Daily Reports',
                    'data': [sum(statuses.values()) for statuses in status_by_date.values()],
                    'borderColor': '#1abc9c',
                    'backgroundColor': 'rgba(26, 188, 156, 0.2)',
                    'tension': 0.4,
                    'fill': True
                }]
            },
            'monthly': {
                'labels': list(monthly_report_data.keys()),
                'datasets': [{
                    'label': 'Monthly Reports',
                    'data': list(monthly_report_data.values()),
                    'borderColor': '#3498db',
                    'backgroundColor': 'rgba(52, 152, 219, 0.2)',
                    'tension': 0.4,
                    'fill': True
                }]
            }
        }

        # Combine all HTML components
        html_content = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>{self.get_styles()}</style>
        </head>
        <body>
            <div class="dashboard-container">
                <div class="title">Dashboard Overview</div>
                {self.get_stats_card_html()}
                {self.get_table_html(recent_reports)}
                {self.get_chart_html(chart_data)}
            </div>
        </body>
        </html>
        '''

        # Load the HTML content
        web_view.setHtml(html_content)
        
        # Wait for the page to load before updating table data
        def check_initialization():
            self.web_page.runJavaScript(
                'typeof initialized !== "undefined" && initialized',
                lambda result: self.update_table_data() if result else QTimer.singleShot(100, check_initialization)
            )
        
        # Start checking for initialization
        QTimer.singleShot(100, check_initialization)
        
        layout.addWidget(web_view)
        self.setLayout(layout)

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
        case_dashboard = CaseDashboard(case_id=case_id)
        
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
        layout.addWidget(case_dashboard)
        self.new_window.setLayout(layout)
        
        self.new_window.showMaximized()
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

    def update_stats(self):
        self.init_ui()