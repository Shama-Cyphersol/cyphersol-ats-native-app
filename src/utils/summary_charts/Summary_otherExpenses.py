from PyQt6.QtWidgets import QApplication, QMainWindow, QComboBox, QVBoxLayout, QWidget, QHBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import sys
from PyQt6.QtGui import QFont
import json
from datetime import datetime

class OtherExpenses(QMainWindow):
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
        'Bank Charges': 6.72,
        'Utility Bills': 588.82,
        'Withdrawal': 31024.78,
        'POS Txns - Dr': 283.00,
        'UPI-Dr': 13197.00,
        'Loan Given': 500000.00,
        'Suspense - Dr': 216242.00,
        'Total Debit': 761342.32
    },
    'May-2023': {
        'Credit Card Payment': 30114.00,
        'Bank Charges': 21.39,
        'Utility Bills': 4245.64,
        'Subscription / Entertainment': 2000.00,
        'Withdrawal': 10000.00,
        'UPI-Dr': 59843.40,
        'Loan Given': 46000.00,
        'Suspense - Dr': 40933.00,
        'Total Debit': 193157.43
    },
    'Jun-2023': {
        'Bank Charges': 45.42,
        'Utility Bills': 588.82,
        'Subscription / Entertainment': 5605.72,
        'Withdrawal': 10000.00,
        'POS Txns - Dr': 4533.00,
        'UPI-Dr': 11094.00,
        'Suspense - Dr': 48030.32,
        'Total Debit': 79897.28
    },
    'Jul-2023': {
        'Bank Charges': 41.76,
        'Utility Bills': 1829.44,
        'POS Txns - Dr': 3211.00,
        'UPI-Dr': 12493.00,
        'Suspense - Dr': 191094.00,
        'Total Debit': 208669.20
    },
    'Aug-2023': {
        'Bank Charges': 80.82,
        'Utility Bills': 1395.79,
        'Subscription / Entertainment': 1458.64,
        'Food Expenses': 330.00,
        'POS Txns - Dr': 490.00,
        'UPI-Dr': 25180.00,
        'Loan Given': 1010000.00,
        'Suspense - Dr': 111523.90,
        'Total Debit': 1150459.15
    },
    'Sep-2023': {
        'Bank Charges': 47.20,
        'Utility Bills': 3119.72,
        'Online Shopping': 299.00,
        'POS Txns - Dr': 3935.00,
        'UPI-Dr': 28361.46,
        'Suspense - Dr': 110489.00,
        'Total Debit': 146251.38
    },
    'Oct-2023': {
        'Bank Charges': 17.70,
        'POS Txns - Dr': 2834.00,
        'UPI-Dr': 19967.00,
        'Suspense - Dr': 122961.00,
        'Total Debit': 145779.70
    },
    'Nov-2023': {
        'Bank Charges': 23.60,
        'POS Txns - Dr': 10915.00,
        'UPI-Dr': 31815.14,
        'Loan Given': 71834.00,
        'Suspense - Dr': 33886.00,
        'Total Debit': 148473.74
    },
    'Dec-2023': {
        'Credit Card Payment': 10995.00,
        'Bank Charges': 27.72,
        'Online Shopping': 642.00,
        'Withdrawal': 10000.00,
        'UPI-Dr': 67035.11,
        'Loan Given': 71834.00,
        'Suspense - Dr': 56505.00,
        'Total Debit': 217038.83
    },
    'Jan-2024': {
        'Bank Charges': 47.78,
        'Utility Bills': 1428.98,
        'Food Expenses': 481.01,
        'UPI-Dr': 87393.30,
        'Loan Given': 71834.00,
        'Suspense - Dr': 397717.00,
        'Total Debit': 558902.07
    },
    'Feb-2024': {
        'Bank Charges': 39.80,
        'Utility Bills': 1350.10,
        'POS Txns - Dr': 2834.00,
        'UPI-Dr': 40000.00,
        'Loan Given': 71834.00,
        'Suspense - Dr': 186486.00,
        'Total Debit': 302543.90
    },
    'Mar-2024': {
        'Bank Charges': 16.10,
        'Other Expenses': 0.00,
        'Utility Bills': 3156.96,
        'UPI-Dr': 40000.00,
        'Suspense - Dr': 32089.00,
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
                        
				        'Credit Card Payment': '#10B981',
                        'Bank Charges': '#F59E0B',
                        'Other Expenses': '#EC4899',
                        'Utility Bills': '#8B5CF6',
                        'Subscription / Entertainment': '#6366F1',
                        'Food Expenses': '#D946EF',
                        'Online Shopping': '#EF4444',
                        'Withdrawal': '#F97316',
                        'POS Txns - Dr': '#22C55E',
                        'UPI-Dr': '#0EA5E9',
                        'Loan Given': '#A855F7',
                        'Suspense - Dr': '#EAB308',
                        'Total Debit': '#34D399'
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
    window = OtherExpenses()
    window.show()
    sys.exit(app.exec())