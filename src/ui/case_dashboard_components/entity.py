from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QHeaderView, QGraphicsDropShadowEffect,
                             QScrollArea, QDialog,QPushButton,QSplitter,QSizePolicy)
import pandas as pd
import os
from utils.json_logic import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
import json
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
        layout.addWidget(self.web)
        
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
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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

            </style>
        </head>
        <body>
            <div class="header">Top 10 Entities by Transaction Frequency</div>
            <div class="chart-container">
                <canvas id="entityChart"></canvas>
            </div>
            
            <div class="table-container">
                <div class="table-header">Complete Entity Frequency List</div>
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
                const totalPages = Math.ceil(data.length / rowsPerPage);

                function updateTable() {{
                    const start = (currentPage - 1) * rowsPerPage;
                    const end = start + rowsPerPage;
                    const pageData = data.slice(start, end);
                    
                    const tableBody = document.getElementById('tableBody');
                    tableBody.innerHTML = '';
                    
                    pageData.forEach(([entity, frequency]) => {{
                        const row = `
                            <tr class="tr-list" onclick="showTransactionTable('${{entity}}')">
                                <td class="key">${{entity}}</td>
                                <td>${{frequency}}</td>
                            </tr>
                        `;
                        tableBody.innerHTML += row;
                    }});
                    
                    document.getElementById('pageInfo').textContent = `Page ${{currentPage}} of ${{totalPages}}`;
                    document.getElementById('prevBtn').disabled = currentPage === 1;
                    document.getElementById('nextBtn').disabled = currentPage === totalPages;
                }}

                function updateTransactionsTable(entity) {{
                    const start = (currentTransactionsPage - 1) * transactionsPerPage;
                    const end = start + transactionsPerPage;
                    const pageTransactions = currentEntityTransactions.slice(start, end);
                    const totalTransactionsPages = Math.ceil(currentEntityTransactions.length / transactionsPerPage);
                    
                    const transactionTableHtml = `
                        <div class="table-container">
                                <button class="close-button" onclick="closeTransactionTable()">Close</button>
                            <div class="table-header-container">
                                <div class="table-header">Transactions for ${{entity}}</div>
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
                                <tbody>
                                    ${{pageTransactions.map(t => `
                                        <tr>
                                            <td>${{t.date}}</td>
                                            <td>${{t.description}}</td>
                                            <td class="amount-cell debit">${{t.debit}}</td>
                                            <td class="amount-cell credit">${{t.credit}}</td>
                                            <td>${{t.category}}</td>
                                        </tr>
                                    `).join('')}}
                                </tbody>
                            </table>
                            <div class="pagination">
                                <button onclick="previousTransactionsPage('${{entity}}')" ${{currentTransactionsPage === 1 ? 'disabled' : ''}}>Previous</button>
                                <span>Page ${{currentTransactionsPage}} of ${{totalTransactionsPages}}</span>
                                <button onclick="nextTransactionsPage('${{entity}}')" ${{currentTransactionsPage === totalTransactionsPages ? 'disabled' : ''}}>Next</button>
                            </div>
                        </div>
                    `;

                    document.getElementById('table-container-nested').innerHTML = transactionTableHtml;
                }}

                function showTransactionTable(entity) {{
                    const transactions = transactionsByEntity[entity] || [];
                    currentEntityTransactions = transactions;
                    currentTransactionsPage = 1;
                    
                   if (transactions.length === 0) {{
                        document.getElementById('table-container-nested').innerHTML = `
                            <div class="table-container">
                                <div class="table-header-container">
                                    <div class="table-header">No transactions found for ${entity}</div>
                                    <button class="close-button" onclick="closeTransactionTable()">Close</button>
                                </div>
                            </div>
                        `;
                        return;
                    }}
                    
                    updateTransactionsTable(entity);
                }}

                function previousTransactionsPage(entity) {{
                    if (currentTransactionsPage > 1) {{
                        currentTransactionsPage--;
                        updateTransactionsTable(entity);
                    }}
                }}

                function nextTransactionsPage(entity) {{
                    const totalPages = Math.ceil(currentEntityTransactions.length / transactionsPerPage);
                    if (currentTransactionsPage < totalPages) {{
                        currentTransactionsPage++;
                        updateTransactionsTable(entity);
                    }}
                }}

                
                function closeTransactionTable() {{
                    document.getElementById('table-container-nested').innerHTML = '';
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
        '''
        
        self.web.setMinimumHeight(2100)  # Set minimum height instead of fixed height
        self.web.setHtml(html_content)
