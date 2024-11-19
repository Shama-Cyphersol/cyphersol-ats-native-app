import sys
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget,QLabel, QWidgetItem,QTableView,QTableWidgetItem,QTableWidget,QHeaderView
from PyQt6.QtWebEngineWidgets import QWebEngineView
import pandas as pd
from PyQt6.QtCore import Qt

class Creditors(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.setGeometry(100, 100, 1200, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Handle empty DataFrame
        if data.empty:
            self.handle_empty_data(layout)
            return

        # Create a QWebEngineView
        self.browser = QWebEngineView()
        
        # Sort data by date
        self.data = data.sort_values(by="Value Date")
        print(self.data.head())

        # Extract data from the DataFrame
        dates = self.data["Value Date"].dt.strftime("%d-%m-%Y").tolist()
        debits = self.data["Debit"].tolist() if "Debit" in self.data.columns else []
        balances = self.data["Balance"].tolist()

        # Create and load the chart
        html_content = self.create_html(dates, debits, balances)
        self.browser.setHtml(html_content)
        self.browser.setFixedHeight(600)

        layout.addWidget(self.browser)
        self.create_data_table_creditor(layout)

    def handle_empty_data(self, layout):
        """Handle case when DataFrame is empty"""
        empty_message = QLabel("No creditor data available to display")
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

    def create_html(self, dates, debits, balances):
        # Create the HTML content with Plotly.js
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body>
            <div id="chart" style="width: 100%; height: 100%;"></div>
            <script>
                var dates = {json.dumps(dates)};
                var debits = {json.dumps(debits)};
                var balances = {json.dumps(balances)};
                
                var trace1 = {{
                    x: dates,
                    y: debits,
                    name: 'Debit Amount',
                    type: 'bar'
                }};
                
                var trace2 = {{
                    x: dates,
                    y: balances,
                    name: 'Balance',
                    type: 'scatter',
                    mode: 'lines+markers',
                    yaxis: 'y2'
                }};
                
                var data = [trace1, trace2];
                
                var layout = {{
                    xaxis: {{
                        title: 'Date',
                        tickformat: "%d-%m-%Y",
                         tickangle: -45,  // Rotate x-axis labels for better readability
                    }},
                    yaxis: {{
                        title: 'Debit Amount',
                    }},
                    yaxis2: {{
                        title: 'Balance',
                        overlaying: 'y',
                        side: 'right',
                    }},
                    barmode: 'group',
                    legend: {{
                        orientation: 'h',
                        x: 0.5,
                        y: 1.15,
                        xanchor: 'center',
                        yanchor: 'bottom'
                    }},
                    margin: {{
                        b: 100  // Increase bottom margin for space below the x-axis
                    }}
                }};
                
                Plotly.newPlot('chart', data, layout);
            </script>
        </body>
        </html>
        """
        return html
    
    def create_data_table_creditor(self, layout):
        web_view = QWebEngineView()
        
        # Prepare table data
        table_data = []
        for _, row in self.data.iterrows():
            table_data.append({
                'date': row["Value Date"].strftime("%d-%m-%Y"),
                'description': row["Description"],
                'debit': f"₹{float(row['Debit']):,.2f}",
                'credit': f"₹{float(row['Credit']):,.2f}",
                'balance': f"₹{float(row['Balance']):,.2f}",
                'category': row["Category"]
            })

        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Creditors Data</title>
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
                    # font-size: 14px;
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
                <div class="table-header">Creditors Data Table</div>
                <div class="search-container">
                    <input type="text" 
                           id="searchInput" 
                           class="search-input" 
                           placeholder="Search transactions..."
                           oninput="handleSearch()"
                    >
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Value Date </span></th>
                            <th class="description-column">Description </span></th>
                            <th>Debit </span></th>
                            <th>Credit </span></th>
                            <th>Balance </span></th>
                            <th>Category </span></th>
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
                               row.debit.toLowerCase().includes(searchTerm) ||
                               row.credit.toLowerCase().includes(searchTerm) ||
                               row.balance.toLowerCase().includes(searchTerm) ||
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
                                <td colspan="6" class="no-results">No matching results found</td>
                            </tr>
                        `;
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