import sys
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView

class StackedBarChart(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cash Withdrawal")
        self.resize(800, 600)

        # Transaction data
        self.data = [
            ("2023-04-20", 1000.00, 246837.78),
            ("2023-04-20", 10000.00, 236837.78),
            ("2023-04-23", 10024.78, 226854.00),
            ("2023-04-27", 10000.00, 907622.00),
            ("2023-05-20", 10000.00, 860132.44),
            ("2023-06-13", 10000.00, 274998.06),
            ("2023-12-10", 10000.00, 847504.03)
        ]

        # Prepare the data for the chart
        self.dates = [item[0] for item in self.data]
        self.withdrawals = [item[1] for item in self.data]
        self.deposits = [5000, 7000, 9000, 11000, 13000, 15000, 17000]  # Example deposit data

        # Set up layout
        layout = QVBoxLayout()
        
        # Create a QWebEngineView
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Show the stacked bar chart immediately
        self.show_stacked_bar_chart()

    def show_stacked_bar_chart(self):
        html_content = self.create_stacked_bar_chart_html(self.dates, self.withdrawals, self.deposits)
        self.browser.setHtml(html_content)

    def create_stacked_bar_chart_html(self, dates, withdrawals, deposits):
        # Create the HTML content with Plotly.js for Stacked Bar Chart
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                #chart {{ width: 100%; height: 650px; }}
            </style>
        </head>
        <body>
            <div id="chart"></div>
            <script>
                var dates = {json.dumps(dates)};
                var withdrawals = {json.dumps(withdrawals)};
                var deposits = {json.dumps(deposits)};
                
                var trace1 = {{
                    x: dates,
                    y: withdrawals,
                    name: 'Withdrawals',
                    type: 'bar',
                    marker: {{ color: 'blue' }}
                }};
                
                var trace2 = {{
                    x: dates,
                    y: deposits,
                    name: 'Deposits',
                    type: 'bar',
                    marker: {{ color: 'orange' }}
                }};
                
                var layout = {{
                    title: 'Stacked Bar Chart of Transactions',
                    xaxis: {{ title: 'Date' }},
                    yaxis: {{ title: 'Amount' }},
                    barmode: 'stack'
                }};
                
                var data = [trace1, trace2];
                
                Plotly.newPlot('chart', data, layout);
            </script>
        </body>
        </html>
        """
        return html

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StackedBarChart()
    window.show()
    sys.exit(app.exec())
