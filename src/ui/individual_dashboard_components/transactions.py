from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
import sys
import json
import pandas as pd

class BankTransactionDashboard(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("Bank Transactions Analysis")
        self.resize(1200, 1200)
        self.data = data

        # print("data",self.data.head())

        # Convert date column to datetime if it's not already
        self.data['Value Date'] = pd.to_datetime(self.data['Value Date'])
        
        # Add month column for filtering
        self.data['Month'] = self.data['Value Date'].dt.strftime('%b-%Y')
        self.data['Day'] = self.data['Value Date'].dt.strftime('%d')
        
        # Create daily aggregated data
        daily_data = self.aggregate_daily_data()
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(15, 15, 15, 15)

        # Create web view for charts and table
        self.create_dashboard(layout, daily_data)

    def aggregate_daily_data(self):
        # Create daily aggregates for each month
        daily_data = {}
        
        for month in self.data['Month'].unique():
            month_data = self.data[self.data['Month'] == month]
            
            # Aggregate by day
            daily_agg = month_data.groupby(['Month', 'Day']).agg({
                'Debit': 'sum',
                'Credit': 'sum',
                'Balance': 'last'  # Take the last balance of each day
            }).reset_index()
            
            # Convert Day to integer for proper sorting
            daily_agg['Day'] = daily_agg['Day'].astype(int)
            daily_agg = daily_agg.sort_values('Day')
            
            # Format day for display (add the month name back)
            month_abbr = month.split('-')[0]  # Get month abbreviation from the Month column
            daily_agg['Day_Display'] = daily_agg['Day'].astype(str) + '-' + month_abbr
            
            daily_data[month] = {
                'days': daily_agg['Day_Display'].tolist(),
                'debits': daily_agg['Debit'].tolist(),
                'credits': daily_agg['Credit'].tolist(),
                'balances': daily_agg['Balance'].tolist()
            }
        
        return daily_data

    def create_dashboard(self, layout, daily_data):
        web_view = QWebEngineView()
        
        # Get unique months for radio buttons
        unique_months = sorted(self.data['Month'].unique().tolist())
        
        # Prepare table data grouped by month
        table_data = {}
        for month in unique_months:
            month_data = self.data[self.data['Month'] == month]
            table_data[month] = [
                {
                    'date': row["Value Date"].strftime("%d-%m-%Y"),
                    'description': row["Description"],
                    'debit': f"₹{row['Debit']:.2f}",
                    'credit': f"₹{row['Credit']:.2f}",
                    'balance': f"₹{row['Balance']:.2f}",
                    'category':f"{row['Category']}",
                    'entity':f"{row['Entity']}"
                }
                for _, row in month_data.iterrows()
            ]
        category_data = {}
        for month in unique_months:
            month_data = self.data[self.data['Month'] == month]
            category_data[month] = month_data['Category'].value_counts().to_dict()

        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bank Transaction Dashboard</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.7.0/chart.min.js"></script>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}
                body {{ 
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    flex-direction: column;
                    margin: 0; 
                    padding: 20px; 
                    font-family: Arial, sans-serif;
                    background-color: white;
                    height: auto;
                }}
                .dashboard-container {{
                    padding: 20px;
                    background-color: white;
                    max-width: 1100px;
                    height: auto;
                    margin: 0 auto;
                }}
                .checkbox-group {{
                    text-align: center;
                    margin: 17px 0;
                    padding: 12px;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .checkbox-group label {{
                    margin-right: 8px;
                    font-size: 14px;
                    cursor: pointer;
                    padding: 5px 10px;
                    border-radius: 15px;
                    transition: background-color 0.3s;
                }}

                .chart-container {{
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: 20px;
                    margin-bottom: 20px;
                    height: 400px;
                }}
                .table-container {{
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: 20px;
                    overflow:auto;
                }}
                .table-header {{
                    text-align: center;
                    padding: 10px;
                    color: #2c3e50;
                    font-size: 1.2rem;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .search-container {{
                    margin: 20px 0;
                    padding: 10px;
                }}
                .search-input {{
                    width: 300px;
                    padding: 10px;
                    border: 2px solid #3498db;
                    border-radius: 5px;
                    font-size: 14px;
                    outline: none;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                th, td {{
                    padding: 20px;
                    text-align: center;
                    border-bottom: 1px solid #e2e8f0;
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                }}
                td {{
                    background-color: white;
                    color: black;
                    text-align: center;
                    font-size: 14px;
                    padding: 5px; /* Internal spacing */
                }}
                .description-column {{
                    text-align: center;
                }}
                .pagination {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin-top: 20px;
                    gap: 10px;
                }}
                .pagination button {{
                    padding: 8px 16px;
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                }}
                .pagination button:disabled {{
                    background-color: #bdc3c7;
                }}
                .no-results {{
                        text-align: center;
                        padding: 20px;
                        color: #666;
                        font-style: italic;
                    }}
            </style>
        </head>
        <body>
            <div class="dashboard-container">
                <div class="checkbox-group">
                    <label><input type="checkbox" id="selectAllMonths"><span>Select All</span></label>
                    {" ".join([f'<label><input type="checkbox" name="month" value="{month}" checked><span>{month}</span></label>' for month in unique_months])}
                </div>
                
                <div class="chart-container">
                    <canvas id="balanceChart"></canvas>
                </div>
                
                <div class="chart-container">
                    <canvas id="transactionChart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="categoryChart" width="100" height="100"></canvas>
                </div>
                
                <div class="table-container">
                    <h2 class="table-header">Transaction Details</h2>
                    <div class="search-container">
                        <input type="text" 
                               id="searchInput" 
                               class="search-input" 
                               placeholder="Search transactions...">
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th class="description-column">Description</th>
                                <th>Debit</th>
                                <th>Credit</th>
                                <th>Balance</th>
                                <th>Category</th>
                                <th>Entity</th>
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

            <script>
                // Chart Data
                const dailyData = {json.dumps(daily_data)};
                const tableData = {json.dumps(table_data)};
                const categoryData = {json.dumps(category_data)};
                let selectedMonth = ["{unique_months[0]}"];
                
                // Balance Line Chart
                const balanceCtx = document.getElementById('balanceChart').getContext('2d');
                const balanceChart = new Chart(balanceCtx, {{
                    type: 'line',
                    data: {{
                        labels: dailyData[selectedMonth].days,
                        datasets: [{{
                            label: 'Daily Balance',
                            data: dailyData[selectedMonth].balances,
                            borderColor: '#3498db',
                            backgroundColor: 'rgba(52, 152, 219, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            title: {{
                                display: true,
                                text: 'Daily Account Balance',
                                font: {{ size: 16 }}
                            }},
                            legend: {{ position: 'top' }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                ticks: {{
                                    callback: value => '₹' + value.toLocaleString()
                                }}
                            }}
                        }}
                    }}
                }});

                // Transaction Bar Chart
                const transactionCtx = document.getElementById('transactionChart').getContext('2d');
                const transactionChart = new Chart(transactionCtx, {{
                    type: 'bar',
                    data: {{
                        labels: dailyData[selectedMonth].days,
                        datasets: [
                            {{
                                label: 'Daily Debits',
                                data: dailyData[selectedMonth].debits,
                                backgroundColor: 'rgba(231, 76, 60, 0.7)',
                                borderColor: 'rgb(231, 76, 60)',
                                borderWidth: 1
                            }},
                            {{
                                label: 'Daily Credits',
                                data: dailyData[selectedMonth].credits,
                                backgroundColor: 'rgba(46, 204, 113, 0.7)',
                                borderColor: 'rgb(46, 204, 113)',
                                borderWidth: 1
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            title: {{
                                display: true,
                                text: 'Daily Debit and Credit Transactions',
                                font: {{ size: 16 }}
                            }},
                            legend: {{ position: 'top' }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                ticks: {{
                                    callback: value => '₹' + value.toLocaleString()
                                }}
                            }}
                        }}
                    }}
                }});
                // Pie Chart for Category Distribution
                const categoryCtx = document.getElementById('categoryChart').getContext('2d');
                const categoryChart = new Chart(categoryCtx, {{
                    type: 'pie',
                    data: {{
                        labels: Object.keys(categoryData),
                        datasets: [{{
                            data: Object.values(categoryData),
                            backgroundColor: [
                                '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', 
                                '#1abc9c', '#34495e', '#95a5a6'
                            ],
                            borderColor: '#fff',
                            borderWidth: 1
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            title: {{
                                display: true,
                                text: 'Transaction Distribution by Category',
                                font: {{ size: 16 }}
                            }},
                            legend: {{ position: 'top' }}
                        }}
                    }}
                }});


                // Table functionality
                const rowsPerPage = 10;
                let currentPage = 1;
                let filteredData = [];
                
                function handleSearch() {{
                    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
                    const currentMonthData = tableData[selectedMonth];
                    
                    filteredData = currentMonthData.filter(row => {{
                        return row.date.toLowerCase().includes(searchTerm) ||
                               row.description.toLowerCase().includes(searchTerm) ||
                               row.debit.toLowerCase().includes(searchTerm) ||
                               row.credit.toLowerCase().includes(searchTerm) ||
                               row.balance.toLowerCase().includes(searchTerm) ||
                               row.category.toLowerCase().includes(searchTerm) ||
                               row.entity.toLowerCase().includes(searchTerm);
                    }});
                    
                    currentPage = 1;
                    updateTable();
                }}

                function updateTable() {{
                    const totalPages = Math.ceil(filteredData.length / rowsPerPage);
                    const start = (currentPage - 1) * rowsPerPage;
                    const end = start + rowsPerPage;
                    const pageData = filteredData.slice(start, end);
                    
                    const tableBody = document.getElementById('tableBody');
                    tableBody.innerHTML = '';
                    
                    if(filteredData.length === 0) {{
                        tableBody.innerHTML = '<tr><td colspan="7" class="no-results">No results found.</td></tr>';
                    }}else{{
                        pageData.forEach(row => {{
                            const tr = `
                                <tr>
                                    <td>${{row.date}}</td>
                                    <td class="description-column">${{row.description}}</td>
                                    <td>${{row.debit}}</td>
                                    <td>${{row.credit}}</td>
                                    <td>${{row.balance}}</td>
                                    <td>${{row.category}}</td>
                                    <td>${{row.entity}}</td>
                                </tr>
                            `;
                            tableBody.innerHTML += tr;
                        }});
                    }}
                      
                    document.getElementById('pageInfo').textContent = filteredData.length > 0 ? `Page ${{currentPage}} of ${{totalPages}}` : '';
                    document.getElementById('prevBtn').disabled = currentPage === 1;
                    document.getElementById('nextBtn').disabled = currentPage === totalPages || filteredData.length === 0;
                }}

                function nextPage() {{
                    const totalPages = Math.ceil(filteredData.length / rowsPerPage);
                    if (currentPage < totalPages) {{
                        currentPage++;
                        updateTable();
                    }}
                }}

                function previousPage() {{
                    if (currentPage > 1) {{
                        currentPage--;
                        updateTable();
                    }}
                }}
                
                function updateChartsAndTable() {{
                    // Aggregate data for selected months
                    const aggregatedDays = [];
                    const aggregatedBalances = [];
                    const aggregatedDebits = [];
                    const aggregatedCredits = [];
                    const aggregatedTableData = [];
                    const aggregatedCategoryData = {{}};

                    selectedMonth.forEach(month => {{
                        aggregatedDays.push(...dailyData[month].days);
                        aggregatedBalances.push(...dailyData[month].balances);
                        aggregatedDebits.push(...dailyData[month].debits);
                        aggregatedCredits.push(...dailyData[month].credits);
                        aggregatedTableData.push(...tableData[month]);

                        Object.entries(categoryData[month] || {{}}).forEach(([category, count]) => {{
                            aggregatedCategoryData[category] = (aggregatedCategoryData[category] || 0) + count;
                        }});
                    }});

                    // Update balance chart
                    balanceChart.data.labels = aggregatedDays;
                    balanceChart.data.datasets[0].data = aggregatedBalances;
                    balanceChart.update();

                    // Update transaction chart
                    transactionChart.data.labels = aggregatedDays;
                    transactionChart.data.datasets[0].data = aggregatedDebits;
                    transactionChart.data.datasets[1].data = aggregatedCredits;
                    transactionChart.update();

                    categoryChart.data.labels = Object.keys(aggregatedCategoryData);
                    categoryChart.data.datasets[0].data = Object.values(aggregatedCategoryData);
                    categoryChart.update();

                    // Update table
                    filteredData = aggregatedTableData;
                    currentPage = 1;
                    updateTable();
               }}

                // Initialize table with first month's data
                filteredData = tableData[selectedMonth];
                updateTable();

                function handleMonthSelection() {{
                    const checkboxes = document.querySelectorAll('input[name="month"]:checked');
                    selectedMonth = Array.from(checkboxes).map(cb => cb.value);

                    if (selectedMonth.length === 0) {{
                        document.getElementById('searchInput').value = '';
                        filteredData = [];
                        currentPage = 1;
                        updateTable();
                    }} else {{
                        updateChartsAndTable();
                    }}
                }}

                
                document.getElementById('selectAllMonths').addEventListener('change', function () {{
                  const checkboxes = document.querySelectorAll('input[name="month"]');
                   checkboxes.forEach(cb => cb.checked = this.checked);
                   handleMonthSelection();
                }});
                
                // Add month selection event listener
                document.querySelectorAll('input[name="month"]').forEach(checkbox => {{
                    checkbox.addEventListener('change', function () {{
                       document.getElementById('selectAllMonths').checked = selectedMonth.length === Object.keys(dailyData).length;
                       handleMonthSelection();
                   }});
                }});

                // Add search event listener
                document.getElementById('searchInput').addEventListener('input', handleSearch);
                
                document.addEventListener('DOMContentLoaded', function () {{
                    // Ensure the first checkbox is checked
                    const checkboxes = document.querySelectorAll('input[name="month"]');
                    checkboxes.forEach(checkbox => {{
                        checkbox.checked = selectedMonth.includes(checkbox.value);
                    }});

                    // Set "Select All" checkbox state
                    document.getElementById('selectAllMonths').checked = selectedMonth.length === Object.keys(dailyData).length;

                    // Initialize the charts and table with the first month's data
                    updateChartsAndTable();
               }});
            </script>
        </body>
        </html>
        '''
        
        web_view.setHtml(html_content)
        web_view.setFixedHeight(2300)
        layout.addWidget(web_view)