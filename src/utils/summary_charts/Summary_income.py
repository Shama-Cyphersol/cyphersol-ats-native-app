from PyQt6.QtWidgets import QApplication, QMainWindow, QComboBox, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import sys
import json
from datetime import datetime

class Income(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Income Distribution Dashboard")
        self.setGeometry(100, 100, 1200, 900)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.months = ['Apr-2023', 'May-2023', 'Jun-2023', 'Jul-2023', 'Aug-2023', 
                      'Sep-2023', 'Oct-2023', 'Nov-2023', 'Dec-2023', 'Jan-2024', 
                      'Feb-2024', 'Mar-2024']
        
        self.data = {
            'Apr-2023': {
                'Salary Received': 0.00,
                'Debtors Amount': 331727.00,
                'UPI-Cr': 36349.00,
                'Suspense - Cr': 455000.00
            },
            'May-2023': {
                'Salary Received': 0.00,
                'Debtors Amount': 0.00,
                'UPI-Cr': 411743.73,
                'Loans Received': 10.00,
                'Suspense - Cr': 410000.00,
            },
            'Jun-2023': {
                'Salary Received': 0.00,
                'Debtors Amount': 0.00,
                'Cash Deposits': 250000.00,
                'UPI-Cr': 194500.00
            },
            'Jul-2023': {
                'Debtors Amount': 1088851.68,
                'UPI-Cr': 236800.00,
                'Suspense - Cr': 200000.00
            },
            'Aug-2023': {
                'Debtors Amount': 485000.00,
                'Cash Deposits': 22000.00,
                'UPI-Cr': 198502.00,
                'Suspense - Cr': 685192.90
            },
            'Sep-2023': {
                'Cash Deposits': 240000.00,
                'UPI-Cr': 51130.00
            },
            'Oct-2023': {
                'Debtors Amount': 115000.00,
                'UPI-Cr': 165600.00
            },
            'Nov-2023': {
                'Debtors Amount': 575000.00,
                'UPI-Cr': 276821.00,
                'Suspense - Cr': 545000.00
            },
            'Dec-2023': {
                'Salary Received': 20000.00,
                'Debtors Amount': 41002.00,
                'UPI-Cr': 705500.00,
                'Suspense - Cr': 175000.00
            },
            'Jan-2024': {
                'Debtors Amount': 40000.00,
                'UPI-Cr': 1083001.00,
                'Refund/Reversal': 62.00,
                'Suspense - Cr': 225000.00
            },
            'Feb-2024': {
                'Debtors Amount': 60001.00,
                'UPI-Cr': 78038.00
            },
            'Mar-2024': {
                'Debtors Amount': 347873.00,
                'UPI-Cr': 336066.00,
                'Bounce Transaction': 250118.00,
                'Refund/Reversal': 199.00,
                'Suspense - Cr': 770000.00
            }
        }

        # Create the web view
        self.web = QWebEngineView()
        layout.addWidget(self.web)
        
        # Initialize the dashboard with the first month
        self.update_dashboard(self.months[0])
    
    def get_highest_category(self, selected_month):
        try:
            if not self.data[selected_month]:
                return "No data", 0
            
            max_category = max(self.data[selected_month].items(), key=lambda x: x[1])
            return max_category[0], max_category[1]
        except Exception as e:
            print(f"Error getting highest category: {e}")
            return "Error", 0
    
    def update_dashboard(self, selected_month):
        try:
            # Filter out zero values
            filtered_data = {k: v for k, v in self.data[selected_month].items() if v > 0}
            
            # Calculate metrics
            total_income = sum(filtered_data.values())
            top_category, top_amount = self.get_highest_category(selected_month)
            
            # Create HTML content with modern dashboard design
            html_content = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Income Distribution Dashboard</title>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.7.0/chart.min.js"></script>
                <style>
                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    }}
                    
                    body {{
                        background-color: #f0f2f5;
                        padding: 20px;
                    }}
                    
                    .dashboard {{
                        max-width: 1200px;
                        margin: 0 auto;
                    }}
                    
                    .header {{
                        background: white;
                        padding: 20px;
                        border-radius: 10px;
                        margin-bottom: 20px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    
                    .metrics-grid {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                        gap: 20px;
                        margin-bottom: 20px;
                    }}
                    
                    .metric-card {{
                        background: white;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    
                    .metric-title {{
                        color: #666;
                        font-size: 0.9em;
                        margin-bottom: 8px;
                    }}
                    
                    .metric-value {{
                        font-size: 1.5em;
                        font-weight: bold;
                        color: #333;
                    }}
                    
                    .chart-container {{
                        background: white;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        height: 500px;
                    }}
                    
                    .radio-group {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                        gap: 10px;
                        background: white;
                        padding: 15px;
                        border-radius: 10px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        margin-bottom: 20px;
                    }}
                    
                    .radio-group label {{
                        display: flex;
                        align-items: center;
                        padding: 8px;
                        border-radius: 5px;
                        cursor: pointer;
                        transition: background-color 0.2s;
                    }}
                    
                    .radio-group label:hover {{
                        background-color: #f0f2f5;
                    }}
                    
                    .radio-group input[type="radio"] {{
                        margin-right: 8px;
                        cursor: pointer;
                    }}
                    
                    .radio-group input[type="radio"]:checked + span {{
                        color: #3B82F6;
                        font-weight: 600;
                    }}
                </style>
            </head>
            <body>
                <div class="dashboard">
                    <div class="radio-group">
                        {' '.join([f'<label><input type="radio" name="month" value="{month}"{" checked" if month == selected_month else ""}><span>{month}</span></label>' for month in self.months])}
                    </div>
                    
                    <div class="header">
                        <h1>Income Distribution for <span id="selectedMonth">{selected_month}</span></h1>
                    </div>
                    
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-title">Total Income</div>
                            <div class="metric-value" id="totalIncome">₹{total_income:,.2f}</div>
                        </div>
                        
                        <div class="metric-card">
                            <div class="metric-title">Top Income Category</div>
                            <div class="metric-value" id="topCategory">{top_category}</div>
                            <div id="topAmount">₹{top_amount:,.2f}</div>
                        </div>
                    </div>
                    
                    <div class="chart-container">
                        <canvas id="pieChart"></canvas>
                    </div>
                </div>
                
                <script>
                    const monthsData = {json.dumps(self.data)};
                    const colors = {{
                        'Salary Received': '#FF5733',
                        'Debtors Amount': '#33FF57',
                        'UPI-Cr': '#3357FF',
                        'Suspense - Cr': '#FF33A5',
                        'Loans Received': '#FF8F33',
                        'Cash Deposits': '#33FFF5',
                        'Refund/Reversal': '#8C33FF',
                        'Bounce Transaction': '#FF3333',
                    }};
                    
                    let myChart = null;  // Global chart instance
                    
                    function updateDashboard(selectedMonth) {{
                        const selectedData = monthsData[selectedMonth];
                        
                        // Update header
                        document.getElementById('selectedMonth').textContent = selectedMonth;
                        
                        // Update metrics
                        const totalIncome = Object.values(selectedData).reduce((a, b) => a + b, 0);
                        document.getElementById('totalIncome').textContent = `₹${{totalIncome.toLocaleString('en-IN', {{minimumFractionDigits: 2, maximumFractionDigits: 2}})}}`
                        
                        const topCategory = Object.entries(selectedData).reduce((a, b) => a[1] > b[1] ? a : b);
                        document.getElementById('topCategory').textContent = topCategory[0];
                        document.getElementById('topAmount').textContent = `₹${{topCategory[1].toLocaleString('en-IN', {{minimumFractionDigits: 2, maximumFractionDigits: 2}})}}`;
                        
                        // Destroy existing chart if it exists
                        if (myChart) {{
                            myChart.destroy();
                        }}
                        
                        // Create new chart
                        const ctx = document.getElementById('pieChart').getContext('2d');
                        myChart = new Chart(ctx, {{
                            type: 'pie',
                            data: {{
                                labels: Object.keys(selectedData),
                                datasets: [{{
                                    data: Object.values(selectedData),
                                    backgroundColor: Object.keys(selectedData).map(key => colors[key] || '#888'),
                                    borderWidth: 2,
                                    borderColor: '#ffffff'
                                }}]
                            }},
                            options: {{
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: {{
                                    legend: {{
                                        position: 'right',
                                        labels: {{
                                            padding: 20,
                                            font: {{
                                                size: 12,
                                                family: "'Segoe UI', sans-serif"
                                            }}
                                        }}
                                    }},
                                    tooltip: {{
                                        callbacks: {{
                                            label: function(context) {{
                                                const value = context.raw;
                                                return `₹${{value.toLocaleString('en-IN', {{minimumFractionDigits: 2, maximumFractionDigits: 2}})}}`;
                                            }}
                                        }}
                                    }}
                                }},
                                layout: {{
                                    padding: 20
                                }}
                            }}
                        }});
                    }}
                    
                    // Initialize chart with first month
                    updateDashboard('{selected_month}');
                    
                    // Add event listeners to radio buttons
                    document.querySelectorAll('input[name="month"]').forEach(radio => {{
                        radio.addEventListener('change', function() {{
                            updateDashboard(this.value);
                        }});
                    }});
                </script>
            </body>
            </html>
            '''
            
            self.web.setHtml(html_content)
        except Exception as e:
            print(f"Error updating dashboard: {e}")
            error_html = f'''
            <!DOCTYPE html>
            <html>
            <body>
                <h1>Error updating dashboard</h1>
                <p>{str(e)}</p>
            </body>
            </html>
            '''
            self.web.setHtml(error_html)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Income()
    window.show()
    sys.exit(app.exec())