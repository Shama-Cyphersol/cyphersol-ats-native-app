from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QPalette, QColor
import sys
import pandas as pd
import json

class SummaryParticular(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("Financial Analytics Dashboard")
        self.data = data
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create tab widget for different views
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Create tabs for different chart types
        self.create_transactions_tab(tab_widget, data)
        # self.create_data_table_summaryParticular(layout, data)
        self.create_data_table_summaryParticular(layout, data)
        
    def create_transactions_tab(self, tab_widget, data):
        transactions_widget = QWidget()
        layout = QVBoxLayout(transactions_widget)
        
        web_view = QWebEngineView()
        web_view.setFixedHeight(600)
        layout.addWidget(web_view)
        
        # Extract the months and transaction data for the chart
        months = data.columns[1:-1].tolist()  # Exclude 'Particulars' and 'Total' columns
        credit_data = data[data['Particulars'] == 'Total Amount of Credit Transactions'].iloc[0, 1:-1].tolist()
        debit_data = data[data['Particulars'] == 'Total Amount of Debit Transactions'].iloc[0, 1:-1].tolist()
        
        # Convert data to JSON format for JavaScript
        months_json = json.dumps(months)
        credit_json = json.dumps(credit_data)
        debit_json = json.dumps(debit_data)
        
        # HTML content with Chart.js using real data
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.7.0/chart.min.js"></script>
            <style>
                body {{ background-color: #f5f5f5; }}
                .chart-container {{ 
                    background-color: white;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
            </style>
        </head>
        <body>
            <div class="chart-container">
                <canvas id="transactionsChart"></canvas>
            </div>
            <script>
                const transactionData = {{
                    labels: {months_json},
                    datasets: [{{
                        label: 'Credit Transactions',
                        data: {credit_json},
                        backgroundColor: 'rgba(76, 175, 80, 0.5)',
                        borderColor: '#4CAF50',
                        borderWidth: 1
                    }},
                    {{
                        label: 'Debit Transactions',
                        data: {debit_json},
                        backgroundColor: 'rgba(244, 67, 54, 0.5)',
                        borderColor: '#F44336',
                        borderWidth: 1
                    }}]
                }};

                new Chart('transactionsChart', {{
                    type: 'bar',
                    data: transactionData,
                    options: {{
                        responsive: true,
                        plugins: {{
                            title: {{
                                display: true,
                                text: 'Monthly Transaction Analysis',
                                font: {{ size: 16 }}
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                stacked: false
                            }},
                            x: {{
                                stacked: false
                            }}
                        }}
                    }}
                }});
            </script>
        </body>
        </html>
        """
        
        web_view.setHtml(html_content)
        tab_widget.addTab(transactions_widget, "Transactions")

    def create_data_table_summaryParticular(self, layout, data):
        # Extract months, credit data, and debit data
        months = data.columns[1:-1].tolist()  # Exclude 'Particulars' and 'Total' columns
        credit_data = data[data['Particulars'] == 'Total Amount of Credit Transactions'].iloc[0, 1:-1].tolist()
        debit_data = data[data['Particulars'] == 'Total Amount of Debit Transactions'].iloc[0, 1:-1].tolist()

        # Prepare the data for the table
        table_data = []
        for i, month in enumerate(months):
            table_data.append({
                'month': month,
                'credit': f"₹{float(credit_data[i]):,.2f}",
                'debit': f"₹{float(debit_data[i]):,.2f}"
            })

        # Generate HTML content with a table structure
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
         
            <title>Summary Particular Data Table</title>

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
                    margin-left: 30px;
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
                <div class="table-header">Monthly Transaction Analysis Table</div>
                <table>
                    <thead>
                        <tr>
                            <th>Month</th>
                            <th>Credit Transactions</th>
                            <th>Debit Transactions</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody">
                    </tbody>
                </table>
                </div>
            
            
            <div class="pagination">
                <button id="prevBtn" onclick="previousPage()">Previous</button>
                    <span id="pageInfo"></span>
                <button id="nextBtn" onclick="nextPage()">Next</button>
            </div>
        </div>
            
            <!-- Include DataTables JavaScript -->
            <script src="https://cdn.datatables.net/v/dt/dt-1.13.1/datatables.min.js"></script>
            
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
                                <td>${{row.month}}</td>
                                <td>${{row.credit}}</td>
                                <td>${{row.debit}}</td>
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

                // Initial table load
                updateTable();

            </script>
        </body>
        </html>
        """
        
        web_view = QWebEngineView()
        web_view.setHtml(html_content)
        web_view.setMinimumHeight(700)  # Set minimum height for the table
        layout.addWidget(web_view)
