from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from modules.dashboard_stats import get_report_count, get_recent_reports, get_monthly_report_count
import json
from datetime import datetime, timedelta

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
                <div class="stat-value">42</div>
                <div class="stat-label">Active Users</div>
            </div>
        </div>
        '''

    def get_table_html(self, recent_reports):
        return f'''
        <div class="section">
            <div class="section-title">Recent Reports</div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Report Name</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([f'<tr><td>{row["date"]}</td><td>{row["name"]}</td><td>{row["status"]}</td></tr>' for row in recent_reports])}
                    </tbody>
                </table>
            </div>
        </div>
        '''

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
        
        # Get data
        recent_reports = get_recent_reports()
        
        # Process reports data - now with both daily and monthly views
    
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

        # Combine all HTML components
        html_content = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/hammer.js/2.0.8/hammer.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-zoom/2.0.1/chartjs-plugin-zoom.min.js"></script>
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
       
        web_view.setHtml(html_content)
        layout.addWidget(web_view)
        self.setLayout(layout)

    def update_stats(self):
        self.init_ui()