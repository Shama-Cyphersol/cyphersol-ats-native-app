# for particulars

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QPalette, QColor
import sys
import pandas as pd
import json

class Particular(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Financial Analytics Dashboard")
        self.setGeometry(100, 100, 1600, 900)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create tab widget for different views
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Create tabs for different chart types
        self.create_transactions_tab(tab_widget)
        
    def create_balance_tab(self, tab_widget):
        balance_widget = QWidget()
        layout = QVBoxLayout(balance_widget)
        
        web_view = QWebEngineView()
        layout.addWidget(web_view)
        
        # HTML content with Chart.js
        
    def create_transactions_tab(self, tab_widget):
        transactions_widget = QWidget()
        layout = QVBoxLayout(transactions_widget)
        
        web_view = QWebEngineView()
        layout.addWidget(web_view)
        
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.7.0/chart.min.js"></script>
            <style>
                body { background-color: #f5f5f5; }
                .chart-container { 
                    background-color: white;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
            </style>
        </head>
        <body>
            <div class="chart-container">
                <canvas id="transactionsChart"></canvas>
            </div>
            <script>
                const transactionData = {
                    labels: ['Apr-2023', 'May-2023', 'Jun-2023', 'Jul-2023', 'Aug-2023', 'Sep-2023', 
                            'Oct-2023', 'Nov-2023', 'Dec-2023', 'Jan-2024', 'Feb-2024', 'Mar-2024'],
                    datasets: [{
                        label: 'Credit Transactions',
                        data: [1123076.00, 1271753.73, 444500.00, 1525651.68, 1390694.90, 291130.00,
                               280600.00, 1396821.00, 941502.00, 1348063.00, 138039.00, 1454138.00],
                        backgroundColor: 'rgba(76, 175, 80, 0.5)',
                        borderColor: '#4CAF50',
                        borderWidth: 1
                    },
                    {
                        label: 'Debit Transactions',
                        data: [1654300.32, 1795958.43, 434497.28, 1003375.60, 1456045.15, 383294.38,
                               789689.70, 764280.74, 823872.83, 663186.07, 714259.66, 2927766.98],
                        backgroundColor: 'rgba(244, 67, 54, 0.5)',
                        borderColor: '#F44336',
                        borderWidth: 1
                    }]
                };

                new Chart('transactionsChart', {
                    type: 'bar',
                    data: transactionData,
                    options: {
                        responsive: true,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Monthly Transaction Analysis',
                                font: { size: 16 }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                stacked: false
                            },
                            x: {
                                stacked: false
                            }
                        }
                    }
                });
            </script>
        </body>
        </html>
        """
        web_view.setHtml(html_content)
        tab_widget.addTab(transactions_widget, "Transaction Analysis")

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    
    app.setPalette(palette)
    
    window = Particular()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
