from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
import sys
import pandas as pd
import json

class Reversal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Financial Dashboard")
        self.resize(1200, 800)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        self.data = {
            'Value Date': ['22-01-2024', '22-03-2024'],
            'Debit': [None, 199.00],
            'Credit': [62.00, None],
            'Balance': [1974571.12, -692538.43],
          
        }
        
        self.df = pd.DataFrame(self.data)
        
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        self.load_dashboard()

    def load_dashboard(self):
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Financial Dashboard</title>
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
                    background: linear-gradient(135deg, #1a1f35 0%, #0f1628 100%);
                    color: #e4e4e4;
                    padding: 25px;
                    min-height: 100vh;
                }}
                
                .dashboard-header {{
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }}
                
                .dashboard-title {{
                    font-size: 28px;
                    font-weight: 600;
                    color: #fff;
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
                    background: rgba(255, 255, 255, 0.05);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    padding: 25px;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                    position: relative;
                    overflow: hidden;
                }}
                
                .stat-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
                }}
                
                .stat-card::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.05));
                    pointer-events: none;
                }}
                
                .stat-icon {{
                    font-size: 24px;
                    margin-bottom: 15px;
                    background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }}
                
                .stat-value {{
                    font-size: 28px;
                    font-weight: 700;
                    margin: 10px 0;
                    background: linear-gradient(135deg, #fff 0%, #d7d7d7 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
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
                    background: rgba(255, 255, 255, 0.03);
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    border-radius: 15px;
                    padding: 25px;
                    position: relative;
                    overflow: hidden;
                }}
                
                .chart-container::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 5px;
                    background: linear-gradient(90deg, #00f2fe, #4facfe);
                }}
                
                .chart-title {{
                    font-size: 18px;
                    font-weight: 600;
                    color: #fff;
                    margin-bottom: 20px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}
                
                .chart-title i {{
                    font-size: 16px;
                    color: #4facfe;
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
            <div class="dashboard-header">
                <h1 class="dashboard-title">Financial Analytics</h1>
            </div>
            
            <div class="summary-stats">
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-wallet"></i>
                    </div>
                    <div class="stat-label">Total Balance</div>
                    <div class="stat-value">${self.df['Balance'].iloc[-1]:,.2f}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-arrow-down"></i>
                    </div>
                    <div class="stat-label">Last Debit</div>
                    <div class="stat-value">${float(self.df['Debit'].dropna().iloc[-1]) if not self.df['Debit'].dropna().empty else 0:,.2f}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">
                        <i class="fas fa-arrow-up"></i>
                    </div>
                    <div class="stat-label">Last Credit</div>
                    <div class="stat-value">${float(self.df['Credit'].dropna().iloc[-1]) if not self.df['Credit'].dropna().empty else 0:,.2f}</div>
                </div>
            </div>
            
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
                Chart.defaults.color = '#e4e4e4';
                Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
                
                // Balance Trend Chart
                new Chart(document.getElementById('balanceChart'), {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps([str(date) for date in self.df['Value Date']])},
                        datasets: [{{
                            label: 'Balance',
                            data: {json.dumps(self.df['Balance'].tolist())},
                            borderColor: '#4facfe',
                            backgroundColor: 'rgba(79, 172, 254, 0.1)',
                            borderWidth: 2,
                            tension: 0.4,
                            fill: true,
                            pointBackgroundColor: '#00f2fe',
                            pointBorderColor: '#fff',
                            pointHoverRadius: 8,
                            pointHoverBackgroundColor: '#fff',
                            pointHoverBorderColor: '#00f2fe'
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
                                    color: 'rgba(255, 255, 255, 0.05)'
                                }}
                            }},
                            x: {{
                                grid: {{
                                    color: 'rgba(255, 255, 255, 0.05)'
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
                                    color: 'rgba(255, 255, 255, 0.05)'
                                }}
                            }},
                            x: {{
                                grid: {{
                                    color: 'rgba(255, 255, 255, 0.05)'
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