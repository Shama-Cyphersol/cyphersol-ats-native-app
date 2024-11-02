import sys
import pandas as pd
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
import json

class PaymentDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Payment Analysis Dashboard")
        self.setGeometry(100, 100, 1400, 800)

        # Sample data
        self.data = {
            'Date': ['01-04-2023', '02-04-2023', '03-04-2023', '04-04-2023', '04-04-2023', '05-04-2023', '05-04-2023', '06-04-2023', '06-04-2023', '08-04-2023','13-05-2023'],
            'Amount': [0.00, 22499.00, 4125.00, 500000.00, 500000.00,45000.00,300000.00,1980.00,1980.00, 588.82, 2000.00],
            'Category': ['Opening Balance', 'Salary', 'Suspense', 'Creditor', 'Loan given','Creditor','Creditor','Suspense', 'Suspense', 'Utility Bills', 'Subscription / Entertainment']
        }
        self.df = pd.DataFrame(self.data)
        self.df['Date'] = pd.to_datetime(self.df['Date'], format='%d-%m-%Y')

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create QWebEngineView
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        # HTML content
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Payment Analysis Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 20px;
                    background-color: #f8f9fa;
                }
                .dashboard-header {
                    text-align: center;
                    color: #2c3e50;
                    margin-bottom: 30px;
                }
                .summary-stats {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .stat-card {
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    text-align: center;
                }
                .stat-value {
                    font-size: 24px;
                    font-weight: bold;
                    color: #2980b9;
                }
                .stat-label {
                    color: #7f8c8d;
                    margin-top: 5px;
                }
                .chart-grid {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 20px;
                }
                .chart-container {
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
            </style>
        </head>
        <body>
            <div class="dashboard-header">
                <h1>Payment Analysis Dashboard</h1>
            </div>

            <div class="summary-stats">
                <div class="stat-card">
                    <div class="stat-value" id="totalAmount">₹0</div>
                    <div class="stat-label">Total Amount</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="avgTransaction">₹0</div>
                    <div class="stat-label">Average Transaction</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="transactionCount">0</div>
                    <div class="stat-label">Total Transactions</div>
                </div>
            </div>

            <div class="chart-grid">
                <div class="chart-container">
                    <canvas id="pieChart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="barChart"></canvas>
                </div>
                <div class="chart-container">
                    <canvas id="lineChart"></canvas>
                </div>
            </div>

            <script>
                let pieChart, barChart, lineChart;

                // Function to initialize charts
                function initializeCharts(data) {
                    // Destroy previous charts if they exist
                    if (pieChart) {
                        pieChart.destroy();
                    }
                    if (barChart) {
                        barChart.destroy();
                    }
                    if (lineChart) {
                        lineChart.destroy();
                    }

                    // Initialize Pie Chart
                    const pieCtx = document.getElementById('pieChart').getContext('2d');
                    pieChart = new Chart(pieCtx, {
                        type: 'doughnut',
                        data: {
                            labels: data.categories,
                            datasets: [{
                                data: data.categoryAmounts,
                                backgroundColor: [
                                    '#3498db',
                                    '#2ecc71',
                                    '#e74c3c',
                                    '#f1c40f',
                                    '#9b59b6',
                                    '#34495e',
                                    '#16a085',
                                    '#27ae60',
                                    '#2980b9',
                                    '#8e44ad'
                                ]
                            }]
                        },
                        options: {
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'Transaction Distribution'
                                }
                            }
                        }
                    });

                    // Initialize Bar Chart
                    const barCtx = document.getElementById('barChart').getContext('2d');
                    barChart = new Chart(barCtx, {
                        type: 'bar',
                        data: {
                            labels: data.dates,
                            datasets: [{
                                label: 'Daily Transactions',
                                data: data.amounts,
                                backgroundColor: '#3498db'
                            }]
                        },
                        options: {
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'Daily Transactions'
                                }
                            }
                        }
                    });

                    // Initialize Line Chart
                    const lineCtx = document.getElementById('lineChart').getContext('2d');
                    lineChart = new Chart(lineCtx, {
                        type: 'line',
                        data: {
                            labels: data.dates,
                            datasets: [{
                                label: 'Cumulative Flow',
                                data: data.cumulative,
                                borderColor: '#2ecc71',
                                tension: 0.1
                            }]
                        },
                        options: {
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'Cumulative Flow'
                                }
                            }
                        }
                    });

                    // Update summary stats
                    document.getElementById('totalAmount').textContent = 
                        '₹' + (data.totalAmount ? data.totalAmount.toLocaleString('en-IN') : '0');
                    document.getElementById('avgTransaction').textContent = 
                        '₹' + (data.avgTransaction ? data.avgTransaction.toLocaleString('en-IN') : '0');
                    document.getElementById('transactionCount').textContent = 
                        data.transactionCount ? data.transactionCount : '0';
                }

                // Ensure that charts are initialized after the page fully loads
                window.onload = function() {
                    // Placeholder data for initialization (data will be updated from PyQt)
                    const initialData = {
                        dates: [],
                        amounts: [],
                        categories: [],
                        categoryAmounts: [],
                        cumulative: [],
                        totalAmount: 0,
                        avgTransaction: 0,
                        transactionCount: 0
                    };
                    initializeCharts(initialData);
                };
            </script>
        </body>
        </html>
        """

        # Set HTML content
        self.web_view.setHtml(html_content)

        # Initialize charts with data after a slight delay to ensure the page is ready
        self.web_view.page().loadFinished.connect(self.update_charts)

    def update_charts(self):
        # Prepare data for charts
        chart_data = {
            'dates': self.df['Date'].dt.strftime('%Y-%m-%d').tolist(),
            'amounts': self.df['Amount'].tolist(),
            'categories': self.df['Category'].unique().tolist(),
            'categoryAmounts': self.df.groupby('Category')['Amount'].sum().tolist(),
            'cumulative': self.df['Amount'].cumsum().tolist(),
            'totalAmount': self.df['Amount'].sum(),
            'avgTransaction': self.df['Amount'].mean(),
            'transactionCount': len(self.df)
        }

        # Ensure the function exists before calling it
        self.web_view.page().runJavaScript("""
            if (typeof initializeCharts !== 'undefined') {
                initializeCharts(%s);
            }
        """ % json.dumps(chart_data))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PaymentDashboard()
    window.show()
    sys.exit(app.exec())