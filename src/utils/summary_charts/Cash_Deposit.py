from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import sys
import json

class CashDeposit(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Financial Dashboard")
        self.setGeometry(100, 100, 1200, 600)
        
        # Create QWebEngineView
        self.web_view = QWebEngineView()
        
        # Prepare data
        dates = ['28-06-2023', '19-08-2023', '15-09-2023']
        balances = [368768.02, 556580.28, 837625.19]
        credits = [250000.00, 22000.00, 240000.00]
        
        # Create HTML content with Chart.js
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Financial Dashboard</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.7.0/chart.min.js"></script>
            <style>
                .chart-container {{
                    display: flex;
                    justify-content: space-around;
                    padding: 20px;
                }}
                .chart-wrapper {{
                    width: 45%;
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    padding: 15px;
                }}
                body {{
                    margin: 0;
                    padding: 0;
                    background-color: #f5f5f5;
                    font-family: Arial, sans-serif;
                }}
            </style>
        </head>
        <body>
            <div class="chart-container">
                <div class="chart-wrapper">
                    <canvas id="balanceChart"></canvas>
                </div>
                <div class="chart-wrapper">
                    <canvas id="creditChart"></canvas>
                </div>
            </div>
            
            <script>
                // Balance Line Chart
                new Chart(document.getElementById('balanceChart'), {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps(dates)},
                        datasets: [{{
                            label: 'Balance',
                            data: {json.dumps(balances)},
                            borderColor: 'rgb(75, 192, 192)',
                            tension: 0.1,
                            fill: true,
                            backgroundColor: 'rgba(75, 192, 192, 0.2)'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            title: {{
                                display: true,
                                text: 'Balance Over Time',
                                font: {{
                                    size: 16
                                }}
                            }},
                            legend: {{
                                position: 'bottom'
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: 'Balance (INR)'
                                }},
                                ticks: {{
                                    callback: function(value) {{
                                        return '₹' + value.toLocaleString();
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
                
                // Credit Bar Chart
                new Chart(document.getElementById('creditChart'), {{
                    type: 'bar',
                    data: {{
                        labels: {json.dumps(dates)},
                        datasets: [{{
                            label: 'Credits',
                            data: {json.dumps(credits)},
                            backgroundColor: 'rgba(54, 162, 235, 0.5)',
                            borderColor: 'rgb(54, 162, 235)',
                            borderWidth: 1
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            title: {{
                                display: true,
                                text: 'Credit Transactions',
                                font: {{
                                    size: 16
                                }}
                            }},
                            legend: {{
                                position: 'bottom'
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: 'Credits (INR)'
                                }},
                                ticks: {{
                                    callback: function(value) {{
                                        return '₹' + value.toLocaleString();
                                    }}
                                }}
                            }}
                        }}
                    }}
                }});
            </script>
        </body>
        </html>
        """
        
        # Set HTML content to QWebEngineView
        self.web_view.setHtml(html_content)
        
        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.web_view)
        
        # Set up the widget and layout
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

# Running the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CashDeposit()
    window.show()
    sys.exit(app.exec())