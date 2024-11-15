from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
import sys
import json

class IncomeSummaryDashboard(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("Income Summary Dashboard")
        self.setGeometry(100, 100, 1200, 900)
        
        # Set the provided income data
        self.data = data
        self.months = list(self.data.keys())
        
        # Create the main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Web view to render HTML content
        self.web = QWebEngineView()
        layout.addWidget(self.web)
        
        # Initialize the dashboard with the first month
        self.update_dashboard(self.months[0])

    def get_highest_category(self, selected_month):
        """Return the category with the highest income for the selected month."""
        try:
            if not self.data[selected_month]:
                return "No data", 0
            
            max_category = max(self.data[selected_month].items(), key=lambda x: x[1])
            return max_category[0], max_category[1]
        except Exception as e:
            print(f"Error getting highest category: {e}")
            return "Error", 0

    def update_dashboard(self, selected_month):
        """Generate and display the HTML content for the selected month."""
        try:
            selected_data = self.data[selected_month]
            
            # Calculate metrics
            total_income = sum(selected_data.values())
            top_category, top_amount = self.get_highest_category(selected_month)
            
            # HTML content with modern dashboard styling
            html_content = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Income Summary Dashboard</title>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.7.0/chart.min.js"></script>
                <style>
                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    }}
                    body {{
                        background-color: #f5f5f5;
                        padding: 20px;
                    }}
                    .dashboard {{
                        max-width: 1200px;
                        margin: auto;
                    }}
                    .header {{
                        background-color: #fff;
                        padding: 20px;
                        border-radius: 10px;
                        margin-bottom: 20px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        text-align: center;
                    }}
                    .metrics-grid {{
                        display: grid;
                        grid-template-columns: repeat(2, 1fr);
                        gap: 20px;
                        margin-bottom: 20px;
                    }}
                    .metric-card {{
                        background: #fff;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        text-align: center;
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
                        display: flex;
                        justify-content: center;
                        margin-bottom: 20px;
                    }}
                    .radio-group label {{
                        margin: 0 10px;
                        cursor: pointer;
                    }}
                </style>
            </head>
            <body>
                <div class="dashboard">
                    <div class="radio-group">
                        {' '.join([f'<label><input type="radio" name="month" value="{month}"{" checked" if month == selected_month else ""}> {month}</label>' for month in self.months])}
                    </div>
                    
                    <div class="header">
                        <h1>Income Summary for <span id="selectedMonth">{selected_month}</span></h1>
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
                    const incomeData = {json.dumps(self.data)};
                    const colors = {{
                        'Salary Received': '#10B981',
                        'Debtors Amount': '#6366F1',
                        'Bank Interest Received': '#F59E0B',
                        'Rent Received': '#D946EF',
                        'Other Income': '#0EA5E9',
                        'Total Income': '#34D399'
                    }};
                    
                    let myChart = null;
                    
                    function updateDashboard(selectedMonth) {{
                        const selectedData = incomeData[selectedMonth];
                        
                        // Update header
                        document.getElementById('selectedMonth').textContent = selectedMonth;
                        
                        // Update metrics
                        const totalIncome = Object.values(selectedData).reduce((a, b) => a + b, 0);
                        document.getElementById('totalIncome').textContent = `₹${{totalIncome.toLocaleString('en-IN', {{minimumFractionDigits: 2, maximumFractionDigits: 2}})}}`;
                        
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
    data = {
        'Jan-2023': {'Salary Received': 50000, 'Debtors Amount': 20000},
        'Feb-2023': {'Salary Received': 52000, 'Debtors Amount': 18000, 'Other Income': 4000},
        # Add more monthly data as needed
    }
    window = IncomeSummaryDashboard(data)
    window.show()
    sys.exit(app.exec())
