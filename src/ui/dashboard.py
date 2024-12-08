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
from ui.main_dashboard_components.recent_reports import RecentReportsTable
from PyQt6.QtWidgets import QScrollArea,QWidget
from ui.signals.global_signals import global_signal_manager


class WebBridge(QObject):
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
        global_signal_manager.update_table.connect(self.update_recent_report_table)
        self.init_ui()

    def init_ui(self):
        # Create the main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Create a widget to hold all sections
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)

        # Dashboard Section - Stats Cards
        stats_frame = self.create_stats_section()
        content_layout.addWidget(stats_frame)

        # Recent Reports Section
        reports_frame = self.create_recent_reports_section()
        content_layout.addWidget(reports_frame)

        # Report Trends Section
        chart_frame = self.create_chart_section()
        content_layout.addWidget(chart_frame)

        # Create a scroll area for the entire content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)

        # Add the scroll area to the main layout
        main_layout.addWidget(scroll_area)

        # Set the main layout for the widget
        self.setLayout(main_layout)

    def create_section_frame(self, title, content_widget):
        # Create a frame for each section with a title
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 5px;
                margin-bottom: 5px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # Add title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Add content
        layout.addWidget(content_widget)
        
        return frame

    def create_stats_section(self):
        # Create the Web Engine view for Stats HTML content
        dashboard_web_view = QWebEngineView()
        dashboard_html = self.get_stats_card_html()
        dashboard_web_view.setHtml(dashboard_html)
        dashboard_web_view.setMinimumHeight(150)  

        # Wrap in a frame with title
        return self.create_section_frame('Dashboard Statistics', dashboard_web_view)

    def create_recent_reports_section(self):
        # Create the recent reports table view
        self.recent_reports_table = RecentReportsTable()
        recent_reports_web_view = self.recent_reports_table.get_web_view()
        recent_reports_web_view.setMinimumHeight(200)  # Default minimum height

        def adjust_height(size):
            if size and size.isValid():
                new_height = int(size.height())
                print(f"Adjusting height to: {new_height}")
                if new_height > 0:  # Only set a positive height
                    recent_reports_web_view.setFixedHeight(new_height)
            else:
                print("Received invalid size:", size)

        def on_load_finished():
            print("loadFinished called")
            recent_reports_web_view.page().toHtml(lambda html: print(f"HTML Content Length: {len(html)}"))  # Debug HTML content length
            size = recent_reports_web_view.page().contentsSize()
            print(f"loadFinished contents size: {size}")
            adjust_height(size)

        # Connect signals
        recent_reports_web_view.page().contentsSizeChanged.connect(adjust_height)
        recent_reports_web_view.page().loadFinished.connect(on_load_finished)

        # Retry logic to handle delayed rendering
        def retry_adjust_height():
            size = recent_reports_web_view.page().contentsSize()
            print(f"Retrying height adjustment. Current size: {size}")
            adjust_height(size)

        # Retry after a delay to handle larger tables
        QTimer.singleShot(1500, retry_adjust_height)

        # Wrap in a frame with title
        return self.create_section_frame('Recent Reports', recent_reports_web_view)
    
    
    def create_chart_section(self):
        # Create the chart WebEngine view
        chart_web_view = QWebEngineView()
        chart_data = self.get_chart_data()
        chart_html = self.get_chart_html(chart_data)
        chart_web_view.setHtml(chart_html)
        # chart_web_view.setFixedHeight(500)
        chart_web_view.setMinimumHeight(500)

        # Wrap in a frame with title
        return self.create_section_frame('Report Trends', chart_web_view)

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
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
            }}
            .stats-container {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background: white;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .stat-value {{
                font-size: 36px;
                font-weight: bold;
                color: #3498db;
                margin: 10px 0;
            }}
            .stat-label {{
                font-size: 14px;
                color: #7f8c8d;
            }}
            @media screen and (max-width: 768px) {{
                .stats-container {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
        '''

    def get_chart_html(self, chart_data):
        return f'''
        <style>
        .chart-container {{
                height: 400px;
                position: relative;
            }}
            @media screen and (max-width: 768px) {{
                .stats-container {{
                    grid-template-columns: 1fr;
                }}
            }}
            .chart-controls {{
                text-align: right;
                margin: 10px 0;
            }}
            .chart-controls button {{
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                margin: 0 5px;
                cursor: pointer;
                transition: background-color 0.3s ease;
                
            }}
            .chart-controls button:hover {{
                background-color: #2980b9;
            }}
        </style>
        <div class="section">
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
            let currentView = 'daily';
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
                                text: currentView === 'daily' ? 'Daily Report Trends' : 'Monthly Report Trends'
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
                const data = view === 'daily' ? dailyData : monthlyData;
                initChart(data);
            }}

            function resetZoom() {{
                if (myChart) {{
                    myChart.resetZoom();
                }}
            }}

            // Initialize with daily view
            initChart(dailyData);
        </script>
        '''

    def get_chart_data(self):
        recent_reports = get_recent_reports()
    
        if not recent_reports:
            return {
                'daily': {'labels': [], 'datasets': []},
                'monthly': {'labels': [], 'datasets': []}
            }
        
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

        dates = sorted(status_by_date.keys())
        unique_statuses = set()
        for data in status_by_date.values():
            unique_statuses.update(data.keys())

        # Calculate monthly totals
        monthly_report_data = {}
        for date, statuses in status_by_date.items():
            month = date[:7]  # Get YYYY-MM
            if month not in monthly_report_data:
                monthly_report_data[month] = 0
            monthly_report_data[month] += sum(statuses.values())  # Sum all statuses for this date

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

        return chart_data

    def update_recent_report_table(self):
        self.recent_reports_table.update_table_data()

