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
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create tab widget for different views
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Create tabs for different chart types
        self.create_transactions_tab(tab_widget, data)
        
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
