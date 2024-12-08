from PyQt6.QtWidgets import QApplication, QMainWindow, QComboBox, QVBoxLayout, QWidget, QHBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import sys
from PyQt6.QtGui import QFont
import json
import pandas as pd

class SummaryOtherExpenses(QMainWindow):
    def __init__(self,data):
        super().__init__()
        self.setWindowTitle("Other Expenses Dashboard")
        self.setGeometry(100, 100, 1200, 900)


        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        print("Other expenses Data: \n",data)
        
        # print("Data: \n",data)
        self.months = self.get_months_from_data(data)
        self.data = {}
        for month in self.months:
            month_data = {}
            for _, row in data.iterrows():
                expense_type = row['Other Expenses / Payments']
                amount = row[month]
                if pd.notnull(amount) and amount != 0:
                    month_data[expense_type] = float(amount)
            if month_data:  # Only add months that have data
                self.data[month] = month_data

        # Create the web view
        self.web = QWebEngineView()
        self.web.setFixedHeight(1200)
        layout.addWidget(self.web)

        if self.data:
            first_month = next(iter(self.data))
            self.update_dashboard(first_month)
        
    def get_months_from_data(self, data):
        month_columns = [
            col for col in data.columns
            if pd.to_datetime(col, format='%b-%Y', errors='coerce') is not pd.NaT
        ]
        return month_columns
    
    def get_highest_category(self, selected_months):
        try:
            aggregated_data = {}
            for month in selected_months:
                if month in self.data:
                    for category, amount in self.data[month].items():
                        aggregated_data[category] = aggregated_data.get(category, 0) + amount
            
            if not aggregated_data:
            
                return "No data", 0
            
            max_category = max(aggregated_data.items(), key=lambda x: x[1])
            return max_category[0], max_category[1]
        except Exception as e:
            print(f"Error getting highest category: {e}")
            return "Error", 0
    
    def update_dashboard(self, selected_months):
        try:
            if selected_months not in self.data:
                raise ValueError(f"No data available for {selected_months}")

            # Filter out zero values
            filtered_data = {k: v for k, v in self.data[selected_months].items() if v > 0}
            
            # Calculate metrics
            total_income = sum(filtered_data.values())
            top_category, top_amount = self.get_highest_category(selected_months)

            # Create HTML content with modern dashboard design
            html_content = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Other Expenses Dashboard</title>
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

                    .table-container {{
                        background: white;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        margin-top: 20px;
                        overflow-x: auto;
                    }}
                    .data-table {{
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 10px;
                    }}

                    .data-table th,
                    .data-table td {{
                        padding: 12px;
                        border-bottom: 1px solid #eee;
                        text-align: center !important;  /* Force center alignment */
                    }}
                    
                    .data-table th {{
                        background-color: #3498db;
                        color: white;
                    }}
                    
                    .data-table tr:hover {{
                        background-color: #f5f5f5;
                    }}
                    
                    .chart-container {{
                        background: white;
                        padding: 20px;
                        border-radius: 10px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        height: 500px;
                    }}
                    
                    .checkbox-group {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                        gap: 10px;
                        background: white;
                        padding: 15px;
                        border-radius: 10px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        margin-bottom: 20px;
                    }}
                    
                    .checkbox-group label {{
                        display: flex;
                        align-items: center;
                        padding: 8px;
                        border-radius: 5px;
                        cursor: pointer;
                        transition: background-color 0.2s;
                    }}


                    .table-header {{
                    text-align: center;
                    padding: 10px;
                    color: #2c3e50;
                    font-size: 1.3rem;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                </style>
            </head>
            <body>
                <div class="dashboard">
                <div class="header">
                        <h1>Other Expenses <span id="selectedMonth"></span></h1>
                    </div>
                        <div class="checkbox-group">
                            <label>
                                <input type="checkbox" id="selectAll" value="SelectAll">
                                <span>Select All</span>
                            </label>
                            {' '.join([f'<label><input type="checkbox" class="month-checkbox" value="{month}"><span>{month}</span></label>' for month in self.months if month in self.data])}
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

                    <div class="table-container">
                        <div class="table-header">Detailed Other Expenses Breakdown</div>
                        <table class="data-table" id="incomeTable">
                            <thead>
                                <tr>
                                    <th>Income Category</th>
                                    <th>Amount (₹)</th>
                                    <th>Percentage of Total</th>
                                </tr>
                            </thead>
                            <tbody>
                            </tbody>
                        </table>
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

                    function updateTable(data) {{
                        const tbody = document.querySelector('#incomeTable tbody');
                        tbody.innerHTML = '';
                        
                        const totalIncome = Object.values(data).reduce((a, b) => a + b, 0);
                        
                        // Sort data by amount in descending order
                        const sortedData = Object.entries(data)
                            .sort(([,a], [,b]) => b - a);
                        
                        sortedData.forEach(([category, amount]) => {{
                            const percentage = (amount / totalIncome * 100).toFixed(2);
                            const row = document.createElement('tr');
                            row.innerHTML = `
                                <td>${{category}}</td>
                                <td>₹${{amount.toLocaleString('en-IN', {{minimumFractionDigits: 2, maximumFractionDigits: 2}})}}
                                <td>${{percentage}}%</td>
                            `;
                            tbody.appendChild(row);
                        }});
                    }}
                    
                   function updateDashboard(selectedMonths) {{
                        const monthsArray = Array.isArray(selectedMonths) ? selectedMonths : [selectedMonths];


                        if (monthsArray.length === 0) {{
                        // If no months are selected, clear the dashboard
                        // document.getElementById('selectedMonth').textContent = 'No months selected';
                        document.getElementById('totalIncome').textContent = '₹0.00';
                        document.getElementById('topCategory').textContent = '-';
                        document.getElementById('topAmount').textContent = '₹0.00';
                        updateTable({{}});
                        if (myChart) {{
                            myChart.destroy();
                        }}
                        return;
                    }}
                        
                        const aggregatedData = {{}};
                            monthsArray.forEach(month => {{
                                const monthData = monthsData[month] || {{}};
                                Object.entries(monthData).forEach(([category, amount]) => {{
                                    if (!aggregatedData[category]) {{
                                        aggregatedData[category] = 0;
                                    }}
                                    aggregatedData[category] += amount;
                                }});
                            }});                        
                        // Update metrics
                        const totalIncome = Object.values(aggregatedData).reduce((a, b) => a + b, 0);
                        const topCategory = Object.entries(aggregatedData).reduce((a, b) => a[1] > b[1] ? a : b, ["-", 0]);

                        document.getElementById('totalIncome').textContent = `₹${{totalIncome.toLocaleString('en-IN', {{minimumFractionDigits: 2, maximumFractionDigits: 2 }})}}`;
                        document.getElementById('topCategory').textContent = topCategory[0];
                        document.getElementById('topAmount').textContent = `₹${{topCategory[1].toLocaleString('en-IN', {{minimumFractionDigits: 2, maximumFractionDigits: 2 }})}}`;

                        updateTable(aggregatedData);

                        // Destroy existing chart if it exists
                        if (myChart) {{
                            myChart.destroy();
                        }}
                        
                        // Create new chart
                        const ctx = document.getElementById('pieChart').getContext('2d');
                        myChart = new Chart(ctx, {{
                            type: 'pie',
                            data: {{
                                labels: Object.keys(aggregatedData),
                                datasets: [{{
                                    data: Object.values(aggregatedData),
                                    backgroundColor: Object.keys(aggregatedData).map(key => colors[key] || '#888'),
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
                    document.addEventListener('DOMContentLoaded', function () {{
                        // Automatically check the first checkbox on page load
                        const checkboxes = document.querySelectorAll('.month-checkbox');
                        const selectAllCheckbox = document.getElementById('selectAll');
                        
                        if (checkboxes.length > 0) {{
                            checkboxes[0].checked = true; // Ensure the first checkbox is checked
                        }}

                        // Initialize the dashboard with the first month's data
                        const selectedMonths = Array.from(document.querySelectorAll('.month-checkbox:checked')).map(cb => cb.value);
                        updateDashboard(selectedMonths);

                        // Add change event listeners to all checkboxes
                        checkboxes.forEach(checkbox => {{
                            checkbox.addEventListener('change', function() {{
                             if (!checkbox.checked) {{
                                selectAllCheckbox.checked = false; // Uncheck "Select All" if any individual checkbox is unchecked
                            }}
                                const selectedMonths = Array.from(document.querySelectorAll('.month-checkbox:checked')).map(cb => cb.value);
                                updateDashboard(selectedMonths);
                            }});
                        }});

                        selectAllCheckbox.addEventListener('change', function () {{
                            const isChecked = selectAllCheckbox.checked;
                            checkboxes.forEach(cb => cb.checked = isChecked);
                            const selectedMonths = isChecked ? Array.from(checkboxes).map(cb => cb.value) : [];
                            updateDashboard(selectedMonths);
                        }});
                    }});
                </script>
            </body>
            </html>
            '''
            
            self.web.setHtml(html_content)
            # self.web.setFixedHeight(1200)

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