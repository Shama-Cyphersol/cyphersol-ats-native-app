from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QHeaderView, QGraphicsDropShadowEffect,
                             QScrollArea, QDialog, QPushButton, QSplitter, QSizePolicy)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage

from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot, QUrl
import pandas as pd
import os
import json
def create_entity_distribution_chart(result):
    try:
        entity_df = result["cummalative_df"]["entity_df"]
        # Remove rows where Entity is empty
        entity_df = entity_df[entity_df.iloc[:, 0] != ""]
        # Take top 10 entities by frequency
        entity_df_10 = entity_df.nlargest(10, entity_df.columns[1])
        return EntityDistributionChart(data={"piechart_data":entity_df_10,"table_data":entity_df,"all_transactions":result["cummalative_df"]["process_df"]})
    except Exception as e:
        print("Error creating entity distribution chart:", e)
        # Create dummy data if there's an error
        dummy_data = pd.DataFrame({
            'Entity': ['Entity1', 'Entity2', 'Entity3'],
            'Frequency': [10, 8, 6]
        })
        return EntityDistributionChart(data={"piechart_data":dummy_data,"table_data":dummy_data,"all_transactions":pd.DataFrame()})
   

class WebBridge(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_widget = parent

    # @pyqtSlot(int)
    # def adjustHeight(self, height):
    #     self.parent_widget.web.setMinimumHeight(height)


class EntityDistributionChart(QWidget):
    def __init__(self, data):
        super().__init__()
        self.piechart_data = data["piechart_data"]
        self.table_data = data["table_data"]
        self.all_transactions = data["all_transactions"]  # Store transactions DataFrame

        
        self.current_page = 1
        self.rows_per_page = 10
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Create web view
        self.web = QWebEngineView()
        # self.web.setMinimumHeight(1400)
        self.web.setFixedHeight(670)
        layout.addWidget(self.web)
        
        # Create web channel
        self.channel = QWebChannel()

        # Create web bridge
        self.web_bridge = WebBridge(self)

        self.channel.registerObject('pyqtBridge', self.web_bridge)

        self.web_bridge = WebBridge(self)

        # Set up the web page
        self.web_page = QWebEnginePage(self.web)
        self.web_page.setWebChannel(self.channel)
        self.web.setPage(self.web_page)

        # Process data for chart
        piechart_data = {}
        for _, row in self.piechart_data.iterrows():
            piechart_data[str(row.iloc[0])] = int(row.iloc[1])

        # Process data for chart
        table_data = {}
        for _, row in self.table_data.iterrows():
            table_data[str(row.iloc[0])] = int(row.iloc[1])

        # Process transactions data for JavaScript
        transactions_by_entity = {}
        for entity in table_data.keys():
            # Filter transactions for this entity
            entity_transactions = self.all_transactions[
                self.all_transactions['Description'].str.contains(entity, case=False, na=False)
            ].copy()
            
            # Convert to list of dictionaries for JSON serialization
            transactions_list = []
            for _, trans in entity_transactions.iterrows():
                transactions_list.append({
                    'date': trans['Value Date'].strftime('%Y-%m-%d'),
                    'description': trans['Description'],
                    'debit': str(trans['Debit']) if not pd.isna(trans['Debit']) else '',
                    'credit': str(trans['Credit']) if not pd.isna(trans['Credit']) else '',
                    'category': trans['Category']
                })
            transactions_by_entity[entity] = transactions_list
        

        # Generate HTML content
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Entity Distribution</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.7.0/chart.min.js"></script>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    scroll-behavior: smooth;
                }}
                .chart-container {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin: 20px;
                    min-height: 400px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }}
                .header {{
                    text-align: center;
                    padding: 10px;
                    color: #2c3e50;
                    font-size: 1.2em;
                    font-weight: bold;
                }}
                .table-container {{
                    margin: 20px;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: 20px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                    border: 1px solid #e2e8f0; /* Add vertical line between cells */
                }}
                th, td {{
                    padding: 12px;
                    border-bottom: 1px solid #e2e8f0;
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                    font-weight: bold;
                    text-align: center;
                }}
                tr:hover {{
                    background-color: #f8fafc;
                }}
                .table-header {{
                    text-align: center;
                    padding: 10px;
                    color: #2c3e50;
                    font-size: 1.2em;
                    font-weight: bold;
                    margin-bottom: 10px;
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
                    color: #2c3e50;
                }}
                #entityChart {{
                    max-width: 100%;
                    height: 100%;
                }}
                .tr-list td {{
                    width: 50%;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                    text-align: center;
                    cursor: pointer;
                }}
                .key{{
                    border-right: 1px solid #e2e8f0; /* Add vertical line between cells */
                }}
                .amount-cell {{
                    text-align: right;
                }}
                .amount-cell.debit {{
                    color: #e74c3c;
                }}
                .amount-cell.credit {{
                    color: #27ae60;
                }}
                .close-button {{
                    background: #f1f5f9;
                    color: #64748b;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 500;
                    display: flex;
                    align-items: center;
                    gap: 4px;
                    transition: all 0.2s ease;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                    margin-left:auto;
                    margin-bottom: 10px;

                }}

                .close-button:hover {{
                    background: #e2e8f0;
                    color: #475569;
                }}

                .close-button::before {{
                    content: '✕';
                    font-size: 14px;
                    margin-right: 4px;
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
                .search-input:focus {{
                    border-color: #2980b9;
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
            <div class="header">Top 10 Entities by Transaction Frequency</div>
            <div class="chart-container">
                <canvas id="entityChart"></canvas>
            </div>
            
            <div class="table-container">
                <div class="table-header">Complete Entity Frequency List</div>
                <div class="search-container">
                    <input type="text" 
                           id="searchInput" 
                           class="search-input" 
                           placeholder="Search Entities..."
                           oninput="handleSearch()"
                    >
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Entity</th>
                            <th>Frequency</th>
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

            <div id="table-container-nested">
            </div>

            
            <script>
                new QWebChannel(qt.webChannelTransport, function(channel) {{
                    window.pyqtBridge = channel.objects.pyqtBridge;
                }});
                const piechart_data = {json.dumps(piechart_data)};
                const table_data = {json.dumps(table_data)};
                const transactionsByEntity = {json.dumps(transactions_by_entity)};
                let currentTransactionsPage = 1;
                const transactionsPerPage = 10;
                let currentEntityTransactions = [];
                


                const colors = [
                    '#10B981', '#6366F1', '#F59E0B', '#D946EF', '#0EA5E9',
                    '#34D399', '#8B5CF6', '#EC4899', '#F97316', '#14B8A6'
                ];
                
                // Pie Chart
                const ctx = document.getElementById('entityChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'pie',
                    data: {{
                        labels: Object.keys(piechart_data),
                        datasets: [{{
                            data: Object.values(piechart_data),
                            backgroundColor: colors,
                            borderColor: '#ffffff',
                            borderWidth: 2
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
                                    }},
                                    generateLabels: function(chart) {{
                                        const data = chart.data;
                                        const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                                        return data.labels.map((label, i) => {{
                                            const value = data.datasets[0].data[i];
                                            const percentage = ((value / total) * 100).toFixed(1);
                                            return {{
                                                text: `${{label}} (${{percentage}}%)`,
                                                fillStyle: colors[i],
                                                strokeStyle: colors[i],
                                                lineWidth: 0,
                                                hidden: false,
                                                index: i
                                            }};
                                        }});
                                    }}
                                }}
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                        const value = context.raw;
                                        const percentage = ((value / total) * 100).toFixed(1);
                                        return `${{context.label}}: ${{value}} transactions (${{percentage}}%)`;
                                    }}
                                }}
                            }}
                        }},
                        layout: {{
                            padding: 20
                        }},
                        animation: {{
                            animateScale: true,
                            animateRotate: true
                        }}
                    }}
                }});

                // Table Pagination
                const rowsPerPage = 10;
                let currentPage = 1;
                const data = Object.entries(table_data).sort((a, b) => b[1] - a[1]);
                let filteredData = [...data];

                function handleSearch() {{
                    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
                    
                    filteredData = data.filter(row => {{
                        return (row[0] || '').toLowerCase().includes(searchTerm) ||
                               (String(row[1]) || '').toLowerCase().includes(searchTerm);
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
                                <td colspan="2" class="no-results">No matching results found</td>
                            </tr>
                        `;
                    }}else{{
                        pageData.forEach(([entity, frequency]) => {{
                            const row = `
                                <tr class="tr-list" onclick="showTransactionTable('${{entity}}')">
                                    <td class="key">${{entity}}</td>
                                    <td>${{frequency}}</td>
                                </tr>
                            `;
                            tableBody.innerHTML += row;
                        }});
                    }}

                    
                    
                    document.getElementById('pageInfo').textContent = filteredData.length > 0 ? `Page ${{currentPage}} of ${{totalPages}}` : '';
                    document.getElementById('prevBtn').disabled = currentPage === 1;
                    document.getElementById('nextBtn').disabled = currentPage === totalPages || filteredData.length === 0;
                }}

                let currentEntity = '';

                function updateTransactionsTable(entity) {{
                    const transactions = filteredEntityTransactions;
    
                    const start = (currentTransactionsPage - 1) * transactionsPerPage;
                    const end = start + transactionsPerPage;
                    const pageTransactions = transactions.slice(start, end);
                    const totalTransactionsPages = Math.ceil(transactions.length / transactionsPerPage);
                    
                    const transactionTableBody = document.getElementById('transactionTableBody');
                    transactionTableBody.innerHTML = '';
                    
                    if (transactions.length === 0) {{
                        transactionTableBody.innerHTML = `
                            <tr>
                                <td colspan="5" class="no-results">No matching transactions found</td>
                            </tr>
                        `;
                        
                        // Disable pagination buttons
                        document.getElementById('transactionPageInfo').textContent = '';
                        document.getElementById('prevTransactionBtn').disabled = true;
                        document.getElementById('nextTransactionBtn').disabled = true;
                    }} else {{
                        // Populate table with transactions
                        pageTransactions.forEach(t => {{
                            const row = `
                                <tr>
                                    <td>${{t.date}}</td>
                                    <td>${{t.description}}</td>
                                    <td class="amount-cell debit">${{t.debit}}</td>
                                    <td class="amount-cell credit">${{t.credit}}</td>
                                    <td>${{t.category}}</td>
                                </tr>
                            `;
                            transactionTableBody.innerHTML += row;
                        }});
                        
                        // Update pagination
                        document.getElementById('transactionPageInfo').textContent = `Page ${{currentTransactionsPage}} of ${{totalTransactionsPages}}`;
                        document.getElementById('prevTransactionBtn').disabled = currentTransactionsPage === 1;
                        document.getElementById('nextTransactionBtn').disabled = currentTransactionsPage === totalTransactionsPages;
                    }}
                }}

                function adjustWebViewHeight() {{
                    // This will communicate back to PyQt to adjust the height
                    window.pyqtBridge.adjustHeight(2100);
                }}
                function adjustWebViewHeightClose() {{
                    // This will communicate back to PyQt to adjust the height
                    window.pyqtBridge.adjustHeight(1400);
                }}

                function showTransactionTable(entity) {{
                    const transactions = transactionsByEntity[entity] || [];
                    currentEntityTransactions = transactions;
                    currentTransactionsPage = 1;
                    
                    if (transactions.length === 0) {{
                        document.getElementById('table-container-nested').innerHTML = `
                            <div class="table-container">
                                <div class="table-header-container">
                                    <div class="table-header">No transactions found for ${{entity}}</div>
                                    <button class="close-button" onclick="closeTransactionTable()">Close</button>
                                </div>
                            </div>
                        `;
                        return;
                    }}
                    
                    const transactionTableHtml = `
                        <div class="table-container" id="transaction-table-container">
                            <button class="close-button" onclick="closeTransactionTable()">Close</button>
                            <div class="table-header-container">
                                <div class="table-header">Transactions for ${{entity}}</div>
                            </div>
                            <div class="search-container">
                                <input type="text" 
                                    id="transactionSearchInput" 
                                    class="search-input" 
                                    placeholder="Search Transactions..."
                                    oninput="handleTransactionSearch('${{entity}}')"
                                >
                            </div>
                            <table class="transaction-table">
                                <thead>
                                    <tr>
                                        <th>Date</th>
                                        <th>Description</th>
                                        <th>Debit</th>
                                        <th>Credit</th>
                                        <th>Category</th>
                                    </tr>
                                </thead>
                                <tbody id="transactionTableBody">
                                </tbody>
                            </table>
                            <div class="pagination">
                                <button id="prevTransactionBtn" onclick="previousTransactionsPage('${{entity}}')">Previous</button>
                                <span id="transactionPageInfo"></span>
                                <button id="nextTransactionBtn" onclick="nextTransactionsPage('${{entity}}')">Next</button>
                            </div>
                        </div>
                    `;

                    document.getElementById('table-container-nested').innerHTML = transactionTableHtml;
                    
                    // Reset filtered transactions to all transactions
                    filteredEntityTransactions = transactions;
                    currentTransactionsPage = 1;
                    updateTransactionsTable(entity);
                   // adjustWebViewHeight();
                    
                    setTimeout(() => {{
                    document.getElementById('transaction-table-container').scrollIntoView();
                }}, 200);
                }}

                let filteredEntityTransactions = [];

                function handleTransactionSearch(entity) {{
                    const searchTerm = document.getElementById('transactionSearchInput').value.toLowerCase();
    
                    // Filter transactions based on search term
                    filteredEntityTransactions = currentEntityTransactions.filter(transaction => {{
                        return (
                            transaction.date.toLowerCase().includes(searchTerm) ||
                            transaction.description.toLowerCase().includes(searchTerm) ||
                            transaction.debit.toLowerCase().includes(searchTerm) ||
                            transaction.credit.toLowerCase().includes(searchTerm) ||
                            transaction.category.toLowerCase().includes(searchTerm)
                        );
                    }});
                    
                    // Reset to first page
                    currentTransactionsPage = 1;
                    
                    // Update table with filtered results
                    updateTransactionsTable(entity);
                }}

                function previousTransactionsPage(entity) {{
                    if (currentTransactionsPage > 1) {{
                        currentTransactionsPage--;
                        updateTransactionsTable(entity);
                    }}
                }}

                function nextTransactionsPage(entity) {{
                    const transactions = filteredEntityTransactions.length > 0 ? filteredEntityTransactions : currentEntityTransactions;
                    const totalPages = Math.ceil(transactions.length / transactionsPerPage);
                    
                    if (currentTransactionsPage < totalPages) {{
                        currentTransactionsPage++;
                        updateTransactionsTable(entity);
                    }}
                }}

                
                function closeTransactionTable() {{
                   // adjustWebViewHeightClose();
                    document.getElementById('table-container-nested').innerHTML = '';
                    filteredEntityTransactions = [];
                    currentEntity = '';
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
        
        # self.web.setMinimumHeight(1400)  # Set minimum height instead of fixed height
        self.web.setHtml(html_content)
