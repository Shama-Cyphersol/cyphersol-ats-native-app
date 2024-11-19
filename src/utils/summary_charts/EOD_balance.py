import sys
import pandas as pd
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import json

class EODBalanceChart(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("Daily Financial Trends")
        self.resize(1400, 800)
        self.data = data
        print(self.data.head())
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create QWebEngineView
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        # Process the data
        months_data = self.process_data()
        
        # Create the HTML content
        html_content = self.create_html_content(months_data)
        
        # Set HTML content in the QWebEngineView
        self.web_view.setFixedHeight(800)
        self.web_view.setHtml(html_content)
    
    def process_data(self):
        # Create a copy of the data to avoid modifying the original
        processed_data = self.data.copy()
        
        def safe_convert(val):
            if pd.isna(val):
                return 0.0
            if isinstance(val, (int, float)):
                return float(val)
            if isinstance(val, str):
                return float(val.replace(',', ''))
            return 0.0
        
        months_data = {}
        
        for column in processed_data.columns:
            if column not in ['Month', 'Day', 'Total', 'Average']:
                valid_rows = processed_data[processed_data['Day'].apply(lambda x: isinstance(x, (int, float)) or (isinstance(x, str) and x.replace('.', '').isdigit()))]
                values = [safe_convert(val) for val in valid_rows[column]]
                months_data[column] = values
        
        return months_data

    def create_html_content(self, months_data):
        # Create radio buttons HTML
        radio_buttons = ''
        for month in months_data.keys():
            checked = 'checked' if month == list(months_data.keys())[0] else ''
            radio_buttons += f'<label><input type="radio" name="month" value="{month}" {checked}> {month}</label>\n'

        # Prepare table data
        table_data = {}
        for month, values in months_data.items():
            table_data[month] = [{"day": i + 1, "value": value} for i, value in enumerate(values)]

        # Convert months_data and table_data to JavaScript
        months_data_js = "const monthsData = " + str(months_data).replace("'", '"')
        table_data_js = "const tableData = " + json.dumps(table_data)

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Daily Financial Values</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
            <style>
                body {{ 
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    flex-direction: column;
                    margin: 0; 
                    padding: 20px; 
                    font-family: Arial, sans-serif;
                    background-color: #f8fafc;
                    height: full;
                }}
                .chart-container {{ 
                    width: 80%;
                    height: auto;
                    background-color: white;
                    padding: 10px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }}
                .table-container {{
                    width: 80%;
                    background-color: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-top: 20px;
                }}
                .title {{
                    text-align: center;
                    margin-bottom: 20px;
                    font-size: 20px;
                    font-weight: bold;
                    color: #1e293b;
                }}
                .radio-group {{
                    text-align: center;
                    margin-bottom: 20px;
                }}
                .radio-group label {{
                    margin-right: 15px;
                    font-size: 16px;
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
                    height: auto;
                }}
                th, td {{
                    padding: 8px;
                    text-align: center;
                }}
                .table-container td {{
                    padding: 10px;
                    background-color: white;
                    color: black;
                    text-align: center;
                    border-bottom: 1px solid #ddd;
                }}
                .table-container th {{
                    background-color: #3498db;
                    color: white;
                    font-weight: bold;
                }}
                tr:hover {{
                    background-color: #e2e8f0;
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
            </style>
        </head>
        <body>
            <div class="radio-group">
                {radio_buttons}
            </div>
            
            <div class="chart-container">
                <div class="title">Daily Financial Values</div>
                <canvas id="financialChart"></canvas>
            </div>
            
            <div class="table-container">
                <div class="title">Monthly Data</div>
                <div class="search-container">
                    <input type="text" id="searchInput" class="search-input" placeholder="Search by day or amount...">
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Day</th>
                            <th>Amount</th>
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
                {months_data_js};
                {table_data_js};
                
                const colors = [
                    '#2563eb', '#16a34a', '#f59e0b', '#ef4444', '#8b5cf6', 
                    '#ec4899', '#10b981', '#f97316', '#3b82f6', '#d97706', 
                    '#06b6d4', '#22d3ee', '#4f46e5', '#059669'
                ];
                
                const monthColors = {{}};
                Object.keys(monthsData).forEach((month, index) => {{
                    monthColors[month] = colors[index % colors.length];
                }});

                let selectedMonth = Object.keys(monthsData)[0];
                let searchTerm = '';
                
                function generateLabels(dataLength) {{
                    return Array.from({{length: dataLength}}, (_, i) => (i + 1).toString());
                }}
                
                const config = {{
                    type: 'line',
                    data: {{
                        labels: generateLabels(monthsData[selectedMonth].length),
                        datasets: [{{
                            label: selectedMonth,
                            data: monthsData[selectedMonth],
                            backgroundColor: monthColors[selectedMonth],
                            borderColor: monthColors[selectedMonth],
                            borderWidth: 2,
                            fill: false,
                            pointBackgroundColor: '#ffffff',
                            pointBorderWidth: 2,
                            pointRadius: 4
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            legend: {{
                                position: 'top'
                            }}
                        }},
                        scales: {{
                            x: {{
                                title: {{
                                    display: true,
                                    text: 'Days'
                                }},
                                ticks: {{
                                    maxTicksLimit: 31,
                                    callback: function(value, index) {{
                                        return index % Math.ceil(monthsData[selectedMonth].length / 15) === 0 ? value : '';
                                    }}
                                }}
                            }},
                            y: {{
                                title: {{
                                    display: true,
                                    text: 'Amount ($)'
                                }}
                            }}
                        }}
                    }}
                }};
                
                const ctx = document.getElementById('financialChart').getContext('2d');
                let financialChart = new Chart(ctx, config);
                
                // Table pagination setup
                const rowsPerPage = 10;
                let currentPage = 1;
                
                function filterData() {{
                    const currentData = tableData[selectedMonth];
                    if (!searchTerm) return currentData;
                    
                    return currentData.filter(item => {{
                        const dayStr = item.day.toString();
                        const valueStr = item.value.toFixed(2).toString();
                        const searchTermLower = searchTerm.toLowerCase();
                        
                        return dayStr.includes(searchTermLower) || 
                               valueStr.includes(searchTermLower);
                    }});
                }}
                
                function updateTable() {{
                    const filteredData = filterData();
                    const totalPages = Math.ceil(filteredData.length / rowsPerPage);
                    const start = (currentPage - 1) * rowsPerPage;
                    const end = Math.min(start + rowsPerPage, filteredData.length);
                    
                    const tableBody = document.getElementById('tableBody');
                    tableBody.innerHTML = '';
                    
                    for (let i = start; i < end; i++) {{
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td>${{filteredData[i].day}}</td>
                            <td>${{filteredData[i].value.toFixed(2)}}</td>
                        `;
                        tableBody.appendChild(tr);
                    }}
                    
                    document.getElementById('pageInfo').textContent = 
                        filteredData.length > 0 
                            ? `Page ${{currentPage}} of ${{totalPages}}` 
                            : 'No results found';
                    
                    document.getElementById('prevBtn').disabled = currentPage === 1;
                    document.getElementById('nextBtn').disabled = currentPage === totalPages || filteredData.length === 0;
                }}
                
                function nextPage() {{
                    const totalPages = Math.ceil(filterData().length / rowsPerPage);
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
                
                // Search functionality
                const searchInput = document.getElementById('searchInput');
                searchInput.addEventListener('input', function(e) {{
                    searchTerm = e.target.value;
                    currentPage = 1; // Reset to first page when searching
                    updateTable();
                }});
                
                // Update chart and table when radio button changes
                document.querySelectorAll('input[name="month"]').forEach(radio => {{
                    radio.addEventListener('change', function() {{
                        selectedMonth = this.value;
                        const newLabels = generateLabels(monthsData[selectedMonth].length);
                        
                        financialChart.data.labels = newLabels;
                        financialChart.data.datasets[0].label = selectedMonth;
                        financialChart.data.datasets[0].data = monthsData[selectedMonth];
                        financialChart.data.datasets[0].backgroundColor = monthColors[selectedMonth];
                        financialChart.data.datasets[0].borderColor = monthColors[selectedMonth];
                        
                        financialChart.options.scales.x.ticks.callback = function(value, index) {{
                            return index % Math.ceil(monthsData[selectedMonth].length / 15) === 0 ? value : '';
                        }};
                        
                        financialChart.update('active');
                        
                        // Reset pagination and search
                        currentPage = 1;
                        searchTerm = '';
                        searchInput.value = '';
                        updateTable();
                    }});
                }});
                
                // Initialize table
                updateTable();
            </script>
        </body>
        </html>
        """