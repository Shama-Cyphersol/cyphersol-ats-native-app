from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCharts import *
import sys
# from datetime import datetime

class BankTransactionDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bank Transactions Analysis")
        self.setGeometry(100, 100, 1200, 800)
        
        # Data
        self.dates = ['15-04-2023', '08-05-2023', '24-05-2023', '03-06-2023', 
                     '05-07-2023', '17-07-2023', '07-08-2023', '14-08-2023']
        self.debits = [6.72, 15.92, 5.47, 45.42, 8.14, 33.62, 47.20, 33.62]
        self.balances = [274994.78, 893695.44, 452747.97, 279686.88, 
                        243845.26, 711017.32, 5192.90, 87382.28]
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QGridLayout(central_widget)
        
        # Create charts
        self.create_balance_line_chart(layout, 0, 0)
        self.create_debit_bar_chart(layout, 0, 1)
        self.create_pie_chart(layout, 1, 0)
        
        # Add styling using QWebEngineView
        self.add_styled_info(layout, 1, 1)

    def create_balance_line_chart(self, layout, row, col):
        chart = QChart()
        series = QLineSeries()
        
        # Enable hover signals
        series.setPointsVisible(True)
        series.hovered.connect(self.handle_line_hover)
        
        # Convert dates to QDateTime and add points
        for i, date_str in enumerate(self.dates):
            date = QDateTime.fromString(date_str, "dd-MM-yyyy")
            series.append(date.toMSecsSinceEpoch(), self.balances[i])
        
        chart.addSeries(series)
        chart.setTitle("Account Balance Over Time")
        
        # Create axes
        axis_x = QDateTimeAxis()
        axis_x.setFormat("dd-MM-yyyy")
        axis_x.setTitleText("Date")
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setTitleText("Balance (₹)")
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        layout.addWidget(chart_view, row, col)

    def handle_line_hover(self, point, state):
        if state:
            date = QDateTime.fromMSecsSinceEpoch(int(point.x()))
            QToolTip.showText(
                QCursor.pos(),
                f"Date: {date.toString('dd-MM-yyyy')}\nBalance: ₹{point.y():,.2f}"
            )

    def create_debit_bar_chart(self, layout, row, col):
        chart = QChart()
        series = QBarSeries()
        
        bar_set = QBarSet("Debit Amount")
        for debit in self.debits:
            bar_set.append(debit)
        
        # Enable hover signals
        series.hovered.connect(self.handle_bar_hover)
        
        series.append(bar_set)
        chart.addSeries(series)
        chart.setTitle("Transaction Amounts")
        
        # Create axes
        axis_x = QBarCategoryAxis()
        axis_x.append(self.dates)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setTitleText("Amount (₹)")
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        layout.addWidget(chart_view, row, col)

    def handle_bar_hover(self, status, index, bar_set):
        if status:
            QToolTip.showText(
                QCursor.pos(),
                f"Date: {self.dates[index]}\nAmount: ₹{self.debits[index]:,.2f}"
            )

    def create_pie_chart(self, layout, row, col):
        chart = QChart()
        series = QPieSeries()
        
        # Group similar amounts
        amount_groups = {}
        for i, debit in enumerate(self.debits):
            rounded = round(debit, 1)
            if rounded in amount_groups:
                amount_groups[rounded] += 1
            else:
                amount_groups[rounded] = 1
        
        for amount, count in amount_groups.items():
            slice = QPieSlice(f"₹{amount} ({count} times)", count)
            slice.hovered.connect(self.handle_pie_hover)
            series.append(slice)
        
        chart.addSeries(series)
        chart.setTitle("Distribution of Transaction Amounts")
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        layout.addWidget(chart_view, row, col)

    def handle_pie_hover(self, state):
        slice = self.sender()
        if state:
            # Extract amount from the label (assumes format "₹XX.XX (Y times)")
            label_parts = slice.label().split()
            amount = label_parts[0]
            count = slice.value()
            percentage = (slice.percentage() * 100)
            
            QToolTip.showText(
                QCursor.pos(),
                f"Amount: {amount}\nCount: {int(count)} transactions\nPercentage: {percentage:.1f}%"
            )
            slice.setExploded(True)
        else:
            slice.setExploded(False)

    def add_styled_info(self, layout, row, col):
        web_view = QWebEngineView()
        
        # Calculate some statistics
        total_debits = sum(self.debits)
        avg_debit = total_debits / len(self.debits)
        max_debit = max(self.debits)
        min_debit = min(self.debits)
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .stats-container {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .stat-item {{
                    margin-bottom: 15px;
                }}
                .stat-label {{
                    color: #666;
                    font-size: 14px;
                }}
                .stat-value {{
                    color: #333;
                    font-size: 18px;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="stats-container">
                <h2>Transaction Statistics</h2>
                <div class="stat-item">
                    <div class="stat-label">Total Charges</div>
                    <div class="stat-value">₹{total_debits:.2f}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Average Charge</div>
                    <div class="stat-value">₹{avg_debit:.2f}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Highest Charge</div>
                    <div class="stat-value">₹{max_debit:.2f}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Lowest Charge</div>
                    <div class="stat-value">₹{min_debit:.2f}</div>
                </div>
            </div>
        </body>
        </html>
        """
        
        web_view.setHtml(html_content)
        layout.addWidget(web_view, row, col)

def main():
    app = QApplication(sys.argv)
    window = BankTransactionDashboard()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()