from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
import sys
import pandas as pd
import json

class Reversal(QMainWindow):
    def __init__(self,data):
        super().__init__()
        self.setWindowTitle("Financial Dashboard")
        self.resize(1200, 800)
        print("Reversal",data.head())
        
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
        
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        self.load_dashboard()

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Reversal()
    window.show()
    sys.exit(app.exec())