import sys
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSizePolicy, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView
import pandas as pd
from PyQt6.QtCore import Qt


class CashDeposit(QMainWindow):
    def __init__(self, data):
        super().__init__()
        # set window to take up the whole screen

        # Transaction data (this can be replaced with real data as shown in the example dataframe)
        self.data = data
        # print(self.data.head())
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        if self.data.empty:
                self.handle_empty_data(layout)
                return

        # Process data for monthly aggregation
        self.data['Month-Year'] = self.data['Value Date'].dt.to_period('M')
        monthly_deposits = self.data.groupby('Month-Year')['Credit'].sum().reset_index()
        monthly_deposits['Month-Year'] = monthly_deposits['Month-Year'].astype(str)

        # Prepare lists for plotting
        self.dates = self.data['Value Date'].dt.strftime('%Y-%m-%d').tolist()
        self.deposits = self.data['Credit'].tolist()
        self.months = monthly_deposits['Month-Year'].tolist()
        self.monthly_totals = monthly_deposits['Credit'].tolist()

        
        # Create and configure QWebEngineView
        self.browser = QWebEngineView()
        self.browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.browser.setFixedHeight(600)

        layout.addWidget(self.browser)
        self.show_charts()

        self.create_data_table_cashDeposit(layout)

    def handle_empty_data(self, layout):
            """Handle case when DataFrame is empty"""
            # Create and style message for empty data
            empty_message = QLabel("No data available to display")
            empty_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_message.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #666;
                    padding: 20px;
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    margin: 20px;
                }
            """)
            layout.addWidget(empty_message)

    def show_charts(self):
        html_content = self.create_charts_html(self.dates, self.deposits, self.months, self.monthly_totals)
        self.browser.setHtml(html_content)

    def create_charts_html(self, dates, deposits, months, monthly_totals):
        # Create the HTML content with Plotly.js for Line and Bar Charts
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ 
                    margin: 0; 
                    padding: 0; 
                    width: 100%; 
                    height: 100vh; 
                    font-family: Arial, sans-serif; 
                }}
                #lineChart, #barChart {{ 
                    width: 100%; 
                    height: 45vh;  /* Use viewport height */
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <!-- Line Chart for Daily Deposits -->
            <div id="lineChart"></div>
            <script>
                var dates = {json.dumps(dates)};
                var deposits = {json.dumps(deposits)};

                var lineTrace = {{
                    x: dates,
                    y: deposits,
                    mode: 'lines+markers',
                    name: 'Daily Deposits',
                    marker: {{ color: 'blue' }},
                    line: {{ color: 'blue' }}
                }};

                var lineLayout = {{
                    title: 'Daily Cash Deposits Over Time',
                    xaxis: {{ title: 'Date' }},
                    yaxis: {{ title: 'Withdrawal Amount' }},
                    legend: {{ orientation: 'h', y: 1.2 }},
                    margin: {{ t: 40, l: 80, r: 40, b: 60 }},
                    autosize: true
                }};

                var config = {{ responsive: true }};

                Plotly.newPlot('lineChart', [lineTrace], lineLayout, config);
            </script>

            <!-- Bar Chart for Monthly Deposits -->
            <div id="barChart"></div>
            <script>
                var months = {json.dumps(months)};
                var monthlyTotals = {json.dumps(monthly_totals)};

                var barTrace = {{
                    x: months,
                    y: monthlyTotals,
                    type: 'bar',
                    name: 'Monthly Deposits',
                    marker: {{ color: 'orange' }}
                }};

                var barLayout = {{
                    title: 'Total Cash Deposits by Month',
                    xaxis: {{ title: 'Month-Year' }},
                    yaxis: {{ title: 'Total Withdrawal Amount' }},
                    legend: {{ orientation: 'h', y: 1.2 }},
                    margin: {{ t: 40, l: 60, r: 40, b: 60 }},
                    autosize: true
                }};

                Plotly.newPlot('barChart', [barTrace], barLayout, config);

                // Add window resize handler
                window.addEventListener('resize', function() {{
                    Plotly.relayout('lineChart', {{
                        'xaxis.autorange': true,
                        'yaxis.autorange': true
                    }});
                    Plotly.relayout('barChart', {{
                        'xaxis.autorange': true,
                        'yaxis.autorange': true
                    }});
                }});
            </script>
        </body>
        </html>
        """
        return html
    
    def create_data_table_cashDeposit(self, layout):
        web_view = QWebEngineView()
        
        # Prepare table data
        table_data = []
        for _, row in self.data.iterrows():
            table_data.append({
                'date': row["Value Date"].strftime("%d-%m-%Y"),
                'description': row["Description"][:50] + "...",  # Truncate long descriptions
                'credit': f"{float(row['Credit']):,.2f}",
                'balance': f"{float(row['Balance']):,.2f}",
                'category': row["Category"]
            })

        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Cash Deposit Data</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}
            .table-container {{
                    margin: 20px;
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    overflow: hidden;
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
                    margin: 20px;
                    padding: 10px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                .search-input {{
                    width: 300px;
                    padding: 10px;
                    border: 2px solid #3498db;
                    border-radius: 5px;
                    font-size: 14px;
                    outline: none;
                    transition: border-color 0.3s;
                }}
                .search-input:focus {{
                    border-color: #2980b9;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }}
                
                th, td {{
                    padding: 12px;
                    text-align: center;
                    border-bottom: 1px solid #e2e8f0;
                }}
                
                th {{
                    background-color: #3498db;
                    color: white;
                    font-weight: bold;
                    position: sticky;
                    top: 0;
                    padding: 6px;
                }}
                tr:hover {{
                    background-color: #f5f5f5;
                }}
            .description-column {{
                    text-align: left;
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
                    font-weight: bold;
                }}
            .pagination button:disabled {{
                    background-color: #bdc3c7;
                    cursor: not-allowed;
                }}
            .pagination span {{
                    font-weight: bold;
                    color: #333333;
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
            <div class="table-container">
                <div class="table-header">Cash Deposit Data Table</div>
                <div class="search-container">
                    <input type="text" 
                           id="searchInput" 
                           class="search-input" 
                           placeholder="Search..."
                           oninput="handleSearch()"
                    >
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Value Date</th>
                            <th class="description-column">Description</th>
                            <th>Credit</th>
                            <th>Balance</th>
                            <th>Category</th>
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
            
            <script>
                const rowsPerPage = 10;
                let currentPage = 1;
                const data = {json.dumps(table_data)};
                let filteredData = [...data];
                

                function handleSearch() {{
                    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
                    
                    filteredData = data.filter(row => {{
                        return row.date.toLowerCase().includes(searchTerm) ||
                               row.description.toLowerCase().includes(searchTerm) ||
                               row.credit.toLowerCase().replace(",","").includes(searchTerm) ||
                               row.balance.toLowerCase().replace(",","").includes(searchTerm) ||
                               row.category.toLowerCase().includes(searchTerm);
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
                    

                    if (filteredData.length === 0) {{
                        tableBody.innerHTML = `
                            <tr>
                                <td colspan="5" class="no-results">No matching results found</td>
                            </tr>
                        `;
                    }}else{{
                        pageData.forEach(row => {{
                            const tr = `
                                <tr>
                                    <td>${{row.date}}</td>
                                    <td class="description-column">${{row.description}}</td>
                                    <td>${{row.credit}}</td>
                                    <td>${{row.balance}}</td>
                                    <td>${{row.category}}</td>
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

                // Initial table load
                updateTable();
            </script>
        </body>
        </html>
        '''
        
        web_view.setHtml(html_content)
        web_view.setMinimumHeight(800)  # Set minimum height for the table
        layout.addWidget(web_view)