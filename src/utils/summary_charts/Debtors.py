import sys
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QFile, QTextStream

class DebtorsChart(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Financial Transactions Overview")
        self.setGeometry(100, 100, 1200, 600)

        # Create a QWebEngineView
        self.browser = QWebEngineView()
        
        # Prepare data
        dates = ["04-03-2024", "15-07-2023", "19-03-2024", "26-02-2024", "19-04-2023"]
        credits = [79873.00, 100000.00, 18000.00, 50000.00, 5000.00]
        balances = [1079401.47, 720361.94, -716597.43, 1039334.47, 249575.78]

        # Create the HTML and JavaScript for the chart
        html_content = self.create_html(dates, credits, balances)
        
        # Load the HTML content into the QWebEngineView
        self.browser.setHtml(html_content)

        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def create_html(self, dates, credits, balances):
        # Create the HTML content with Plotly.js
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body>
            <div id="chart" style="width: 100%; height: 100%;"></div>
            <script>
                var dates = {json.dumps(dates)};
                var credits = {json.dumps(credits)};
                var balances = {json.dumps(balances)};
                
                var trace1 = {{
                    x: dates,
                    y: credits,
                    name: 'Credit Amount',
                    type: 'bar'
                }};
                
                var trace2 = {{
                    x: dates,
                    y: balances,
                    name: 'Balance',
                    type: 'scatter',
                    mode: 'lines+markers',
                    yaxis: 'y2'
                }};
                
                var data = [trace1, trace2];
                
                var layout = {{
                    title: 'Financial Transactions: Credit Amounts and Balance Over Time',
                    yaxis: {{
                        title: 'Credit Amount',
                    }},
                    yaxis2: {{
                        title: 'Balance',
                        overlaying: 'y',
                        side: 'right',
                    }},
                    barmode: 'group'
                }};
                
                Plotly.newPlot('chart', data, layout);
            </script>
        </body>
        </html>
        """
        return html

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DebtorsChart()
    window.show()
    sys.exit(app.exec())
