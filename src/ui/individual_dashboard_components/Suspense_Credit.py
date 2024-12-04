import sys
import pandas as pd
import plotly.express as px
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import json
import tempfile
class SuspenseCredit(QWidget):
    def __init__(self, data, total_transactions, total_credit_txn):
        super().__init__()


        layout = QVBoxLayout(self)

        # Chart visualization setup
        df = pd.DataFrame(data)

        suspense_credit_count = len(df)

        pie_data = {
            'labels': ['Unkown Credit', 'Total Credit'],
            'values': [suspense_credit_count, total_credit_txn]
        }

        fig = px.bar(df, x='Credit', y='Description', color='Credit',
                     color_continuous_scale='Viridis', title='Credit Transactions')
        
        fig.update_layout(xaxis_title="Credit Amount (₹)", yaxis_title="Description", 
                          yaxis_tickangle=0, template="plotly_white")
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        fig.write_html(temp_file.name)

        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl.fromLocalFile(temp_file.name))
        self.web_view.setFixedHeight(700)

        layout.addWidget(self.web_view)

        temp_file_pie = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        
        fig_pie = px.pie(pie_data, names='labels', values='values', 
                        #  color_discrete_sequence=['#a5d7a7', '#f9a19a'], 
                         color_discrete_sequence=['#94cb94', '#f16e65'],
                         title='Unkown Credit Transactions vs Total Credit Transactions')
        
        fig_pie.update_layout(margin=dict(l=10, r=40, t=50, b=10))
        
        fig_pie.write_html(temp_file_pie.name)

        self.web_view_pie = QWebEngineView()
        self.web_view_pie.setUrl(QUrl.fromLocalFile(temp_file_pie.name))
        self.web_view_pie.setFixedHeight(500)

        layout.addWidget(self.web_view_pie)
        
        # Call create_html_table to add the table below the chart
        self.create_html_table(layout, data)

    def create_html_table(self, layout, data):
        web_view = QWebEngineView()
        
        table_data = [
            {
                'date': row["Value Date"].strftime("%d-%m-%Y"),
                'description': row["Description"],
                'credit': f"₹{row['Credit']:.2f}",
            }
            for _, row in data.iterrows()
        ]

        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Unkown Credit Details</title>
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
                    # box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                .table-header {{
                    text-align: center;
                    padding: 10px;
                    color: #2c3e50;
                    font-size: 1.2rem;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .table-container table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                .table-container th, .table-container td {{
                    padding: 10px;
                    text-align: center;
                    border-bottom: 1px solid #ddd;
                }}
                .table-container th {{
                    background-color: #3498db;
                    color: white;
                    font-weight: bold;
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
                .description-column {{
                    text-align: left;
                }}
                tr:hover {{
                    background-color: #f8fafc;
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
                <div class="table-header">Suspense Credit Data Table</div>
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
                            <th>Date</th>
                            <th>Description</th>
                            <th>Credit</th>
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
                               row.credit.toLowerCase().includes(searchTerm);
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
                    }} else{{
                        pageData.forEach(row => {{
                            const tr = `
                                <tr>
                                    <td>${{row.date}}</td>
                                    <td>${{row.description}}</td>
                                    <td>${{row.credit}}</td>
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

                updateTable();
            </script>
        </body>
        </html>
        '''
        
        web_view.setHtml(html_content)
        web_view.setMinimumHeight(800)
        layout.addWidget(web_view)

