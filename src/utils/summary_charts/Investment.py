import sys
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSizePolicy
from PyQt6.QtWebEngineWidgets import QWebEngineView
import pandas as pd

class InvestmentChart(QMainWindow):
    def __init__(self, data):
        super().__init__()
        
        # Transaction data
        self.data = data
        print(self.data.head())

        # Process data for monthly aggregation
        self.data['Month-Year'] = self.data['Value Date'].dt.to_period('M')
        monthly_investments = self.data.groupby('Month-Year')['Debit'].sum().reset_index()
        monthly_investments['Month-Year'] = monthly_investments['Month-Year'].astype(str)

        # Prepare lists for plotting
        self.dates = self.data['Value Date'].dt.strftime('%Y-%m-%d').tolist()
        self.investments = self.data['Debit'].tolist()
        self.months = monthly_investments['Month-Year'].tolist()
        self.monthly_totals = monthly_investments['Debit'].tolist()

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create and configure QWebEngineView
        self.browser = QWebEngineView()
        self.browser.setFixedHeight(800)
        self.browser.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.browser)
        self.show_charts()
        
        self.create_data_table_investments(layout)

    def show_charts(self):
        html_content = self.create_charts_html(self.dates, self.investments, self.months, self.monthly_totals)
        self.browser.setHtml(html_content)

    def create_charts_html(self, dates, investments, months, monthly_totals):
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
                    height: 45vh;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div id="lineChart"></div>
            <script>
                var dates = {json.dumps(dates)};
                var investments = {json.dumps(investments)};

                var lineTrace = {{
                    x: dates,
                    y: investments,
                    mode: 'lines+markers',
                    name: 'Daily Investments',
                    marker: {{ color: 'blue' }},
                    line: {{ color: 'blue' }}
                }};

                var lineLayout = {{
                    title: 'Daily Investment Transactions',
                    xaxis: {{ title: 'Date' }},
                    yaxis: {{ title: 'Investment Amount (₹)' }},
                    legend: {{ orientation: 'h', y: 1.2 }},
                    margin: {{ t: 40, l: 80, r: 40, b: 60 }},
                    autosize: true
                }};

                var config = {{ responsive: true }};

                Plotly.newPlot('lineChart', [lineTrace], lineLayout, config);
            </script>

            <div id="barChart"></div>
            <script>
                var months = {json.dumps(months)};
                var monthlyTotals = {json.dumps(monthly_totals)};

                var barTrace = {{
                    x: months,
                    y: monthlyTotals,
                    type: 'bar',
                    name: 'Monthly Investments',
                    marker: {{ color: 'orange' }}
                }};

                var barLayout = {{
                    title: 'Total Investments by Month',
                    xaxis: {{ title: 'Month-Year' }},
                    yaxis: {{ title: 'Total Investment Amount (₹)' }},
                    legend: {{ orientation: 'h', y: 1.2 }},
                    margin: {{ t: 40, l: 60, r: 40, b: 60 }},
                    autosize: true
                }};

                Plotly.newPlot('barChart', [barTrace], barLayout, config);

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
    
    def create_data_table_investments(self, layout):
        web_view = QWebEngineView()
        
        # Prepare table data
        table_data = []
        for _, row in self.data.iterrows():
            table_data.append({
                'date': row["Value Date"].strftime("%d-%m-%Y"),
                'description': row["Description"][:50] + "...",
                'debit': f"₹{float(row['Debit']):,.2f}",
                'balance': f"₹{float(row['Balance']):,.2f}",
                'category': row["Category"]
            })

        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Investment Transactions Data</title>
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
            </style>
        </head>
        <body>
            <div class="table-container">
                <div class="table-header">Investment Transactions Data</div>
                <table>
                    <thead>
                        <tr>
                            <th>Value Date</th>
                            <th class="description-column">Description</th>
                            <th>Investment Amount</th>
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
                const totalPages = Math.ceil(data.length / rowsPerPage);

                function updateTable() {{
                    const start = (currentPage - 1) * rowsPerPage;
                    const end = start + rowsPerPage;
                    const pageData = data.slice(start, end);
                    
                    const tableBody = document.getElementById('tableBody');
                    tableBody.innerHTML = '';
                    
                    pageData.forEach(row => {{
                        const tr = `
                            <tr>
                                <td>${{row.date}}</td>
                                <td class="description-column">${{row.description}}</td>
                                <td>${{row.debit}}</td>
                                <td>${{row.balance}}</td>
                                <td>${{row.category}}</td>
                            </tr>
                        `;
                        tableBody.innerHTML += tr;
                    }});
                    
                    document.getElementById('pageInfo').textContent = `Page ${{currentPage}} of ${{totalPages}}`;
                    document.getElementById('prevBtn').disabled = currentPage === 1;
                    document.getElementById('nextBtn').disabled = currentPage === totalPages;
                }}

                function nextPage() {{
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

                updateTable();
            </script>
        </body>
        </html>
        '''
        
        web_view.setHtml(html_content)
        web_view.setMinimumHeight(600)
        layout.addWidget(web_view)