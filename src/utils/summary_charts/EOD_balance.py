import sys
import pandas as pd
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

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
        self.web_view.setFixedHeight(650)

        self.web_view.setHtml(html_content)
    
    def process_data(self):
        # Create a copy of the data to avoid modifying the original
        processed_data = self.data.copy()
        
        # Function to safely convert values
        def safe_convert(val):
            if pd.isna(val):
                return 0.0
            if isinstance(val, (int, float)):
                return float(val)
            if isinstance(val, str):
                # Remove commas and convert to float
                return float(val.replace(',', ''))
            return 0.0
        
        # Create a dictionary to store the data for each month
        months_data = {}
        
        # Process each month column
        for column in processed_data.columns:
            if column not in ['Month', 'Day', 'Total', 'Average']:
                # Get the values for all days (excluding Total and Average rows)
                # Filter out rows where Day is not numeric
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

        # Convert months_data to JavaScript
        months_data_js = "const monthsData = " + str(months_data).replace("'", '"')

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
                    height:100%;
                }}
                .chart-container {{ 
                    width: 80%;
                    height: auto;
                    overflow: visible;
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
                    overflow-x: auto;
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
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }}
                th, td {{
                    border: 1px solid #e2e8f0;
                    padding: 8px;
                    text-align: right;
                }}
                th {{
                    background-color: #f1f5f9;
                    font-weight: 600;
                    text-align: center;
                }}
                tr:nth-child(even) {{
                    background-color: #f8fafc;
                }}
                tr:hover {{
                    background-color: #e2e8f0;
                }}
                .table-title {{
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 10px;
                    text-align: center;
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
            
            
            <script>
                {months_data_js};
                
                // Define colors for each month
                const colors = [
                    '#2563eb', '#16a34a', '#f59e0b', '#ef4444', '#8b5cf6', 
                    '#ec4899', '#10b981', '#f97316', '#3b82f6', '#d97706', 
                    '#06b6d4', '#22d3ee', '#4f46e5', '#059669'
                ];
                
                const monthColors = {{}};
                Object.keys(monthsData).forEach((month, index) => {{
                    monthColors[month] = colors[index % colors.length];
                }});
                
                // Default chart data
                let selectedMonth = Object.keys(monthsData)[0];
                
                // Function to generate labels based on data length
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
                
                // Initial table update
                updateTable(selectedMonth);
                
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
                        
                        financialChart.update();
                        
                    }});
                }});
            </script>
        </body>
        </html>
        """