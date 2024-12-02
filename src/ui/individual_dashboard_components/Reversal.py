from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout,QLabel
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
import sys
import pandas as pd
import json
from PyQt6.QtCore import Qt


class Reversal(QMainWindow):
    def __init__(self,data):
        super().__init__()
        self.setWindowTitle("Financial Dashboard")
        self.resize(1200, 800)
        # print("Reversal",data.head())
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # self.data = {
        #     'Value Date': ['22-01-2024', '22-03-2024'],
        #     'Debit': [None, 199.00],
        #     'Credit': [62.00, None],
        #     'Balance': [1974571.12, -692538.43],
          
        # }
        
        self.df = pd.DataFrame(data)
        if self.df.empty:
            self.handle_empty_data(layout)
            return
        self.web_view = QWebEngineView()
        self.web_view.setFixedHeight(400)


        layout.addWidget(self.web_view)
        
        self.load_dashboard()
        self.create_data_table_reversal(layout)

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

    def load_dashboard(self):
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.7.0/chart.min.js"></script>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Poppins', sans-serif;
                    background-color: #ffffff;  /* Changed to white */
                    color: #333333;  /* Darker text for better contrast */
                    padding: 25px;
                    min-height: 100vh;
                }}
                
                .dashboard-header {{
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
                }}
                
                .dashboard-title {{
                    font-size: 28px;
                    font-weight: 600;
                    color: #333333;  /* Darker color for the title */
                    margin-bottom: 10px;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                }}
                
                .summary-stats {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 25px;
                    margin-bottom: 30px;
                }}
                
                .stat-card {{
                    background: rgba(0, 0, 0, 0.05);  /* Light background for cards */
                    border: 1px solid rgba(0, 0, 0, 0.1);
                    border-radius: 15px;
                    padding: 25px;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                    position: relative;
                    overflow: hidden;
                }}
                
                .stat-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
                }}
                
                .stat-icon {{
                    font-size: 24px;
                    margin-bottom: 15px;
                    color: #007BFF;  /* Change icon color to a vibrant blue */
                }}
                
                .stat-value {{
                    font-size: 28px;
                    font-weight: 700;
                    margin: 10px 0;
                    color: #007BFF;  /* Change stat value color */
                }}
                
                .stat-label {{
                    font-size: 14px;
                    color: #8e9aaf;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                
                .dashboard-container {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 25px;
                }}
                
                .chart-container {{
                    background: rgba(0, 0, 0, 0.03);
                    border: 1px solid rgba(0, 0, 0, 0.05);
                    border-radius: 15px;
                    padding: 25px;
                    position: relative;
                    overflow: hidden;
                }}
                
                .chart-title {{
                    font-size: 18px;
                    font-weight: 600;
                    color: #333333;  /* Darker color for the chart title */
                    margin-bottom: 20px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}
                
                canvas {{
                    margin-top: 10px;
                }}

                @keyframes pulse {{
                    0% {{ transform: scale(1); }}
                    50% {{ transform: scale(1.02); }}
                    100% {{ transform: scale(1); }}
                }}
                
                .pulse {{
                    animation: pulse 2s infinite;
                }}
            </style>
        </head>
        <body>
            
            <div class="dashboard-container">
                <div class="chart-container">
                    <h2 class="chart-title">
                        <i class="fas fa-chart-line"></i>
                        Balance Trend
                    </h2>
                    <canvas id="balanceChart"></canvas>
                </div>
                <div class="chart-container">
                    <h2 class="chart-title">
                        <i class="fas fa-exchange-alt"></i>
                        Debit vs Credit
                    </h2>
                    <canvas id="debitCreditChart"></canvas>
                </div>

            </div>

            <script>
                Chart.defaults.color = '#333333';  // Change default chart text color to dark
                Chart.defaults.borderColor = 'rgba(0, 0, 0, 0.1)';
                
                // Balance Trend Chart
                new Chart(document.getElementById('balanceChart'), {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps([str(date) for date in self.df['Value Date']])},
                        datasets: [{{
                            label: 'Balance',
                            data: {json.dumps(self.df['Balance'].tolist())},
                            borderColor: '#007BFF',  // Change to blue color
                            backgroundColor: 'rgba(0, 123, 255, 0.1)',
                            borderWidth: 2,
                            tension: 0.4,
                            fill: true,
                            pointBackgroundColor: '#007BFF',
                            pointBorderColor: '#fff',
                            pointHoverRadius: 8,
                            pointHoverBackgroundColor: '#fff',
                            pointHoverBorderColor: '#007BFF'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            legend: {{
                                position: 'top',
                                labels: {{
                                    font: {{
                                        family: 'Poppins',
                                        size: 12
                                    }}
                                }}
                            }}
                        }},
                        scales: {{
                            y: {{
                                grid: {{
                                    color: 'rgba(0, 0, 0, 0.05)'
                                }}
                            }},
                            x: {{
                                grid: {{
                                    color: 'rgba(0, 0, 0, 0.05)'
                                }}
                            }}
                        }}
                    }}
                }});

                // Debit vs Credit Chart
                new Chart(document.getElementById('debitCreditChart'), {{
                    type: 'bar',
                    data: {{
                        labels: {json.dumps([str(date) for date in self.df['Value Date']])},
                        datasets: [
                            {{
                                label: 'Debit',
                                data: {json.dumps([float(x) if pd.notna(x) else 0 for x in self.df['Debit']])},
                                backgroundColor: 'rgba(255, 99, 132, 0.7)',
                                borderColor: 'rgba(255, 99, 132, 1)',
                                borderWidth: 2
                            }},
                            {{
                                label: 'Credit',
                                data: {json.dumps([float(x) if pd.notna(x) else 0 for x in self.df['Credit']])},
                                backgroundColor: 'rgba(72, 207, 173, 0.7)',
                                borderColor: 'rgba(72, 207, 173, 1)',
                                borderWidth: 2
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            legend: {{
                                position: 'top',
                                labels: {{
                                    font: {{
                                        family: 'Poppins',
                                        size: 12
                                    }}
                                }}
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                grid: {{
                                    color: 'rgba(0, 0, 0, 0.05)'
                                }}
                            }},
                            x: {{
                                grid: {{
                                    color: 'rgba(0, 0, 0, 0.05)'
                                }}
                            }}
                        }}
                    }}
                }});

                // Add hover effect to stat cards
                document.querySelectorAll('.stat-card').forEach(card => {{
                    card.addEventListener('mouseover', () => {{
                        card.classList.add('pulse');
                    }});
                    card.addEventListener('mouseout', () => {{
                        card.classList.remove('pulse');
                    }});
                }});
            </script>
        </body>
        </html>
        """
        
        self.web_view.setHtml(html_content)

    def create_data_table_reversal(self, layout):
        web_view = QWebEngineView()
        
        # Prepare table data
        table_data = []
        for _, row in self.df.iterrows():
            table_data.append({
                'date': str(row["Value Date"]),
                'description': row["Description"][:50] + "...",
                'debit': f"{float(row['Debit']) if pd.notna(row['Debit']) else 0:.2f}",
                'credit': f"{float(row['Credit']) if pd.notna(row['Credit']) else 0:.2f}",
                'balance': f"{float(row['Balance']):,.2f}",
                'category': row["Category"]
            })

        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Reversal Data</title>
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
                <div class="table-header">Reversal Data Table</div>
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
                            <th>Debit</th>
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

                    
                    
                    document.getElementById('pageInfo').textContent =filteredData.length > 0 ? `Page ${{currentPage}} of ${{totalPages}}` : '';
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
        web_view.setFixedHeight(1000)  # Set minimum height for the table
        layout.addWidget(web_view)

        