from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PyQt6.QtCore import QDateTime, Qt
from PyQt6.QtGui import QPainter
import sys
from datetime import datetime

class TransactionChart(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transaction History (Creditors)")
        self.resize(800, 600)
        
        # Create series for balance and withdrawals
        self.balance_series = QLineSeries()
        self.balance_series.setName("Balance")
        
        # Transaction data
        data = [
            ("2023-04-20", 1000.00, 246837.78),
            ("2023-04-20", 10000.00, 236837.78),
            ("2023-04-23", 10024.78, 226854.00),
            ("2023-04-27", 10000.00, 907622.00),
            ("2023-05-20", 10000.00, 860132.44),
            ("2023-06-13", 10000.00, 274998.06),
            ("2023-12-10", 10000.00, 847504.03)
        ]
        
        # Populate series
        for date_str, _, balance in data:
            date = QDateTime.fromString(date_str, "yyyy-MM-dd")
            self.balance_series.append(date.toMSecsSinceEpoch(), balance)
        
        # Create chart
        chart = QChart()
        chart.addSeries(self.balance_series)
        chart.setTitle("Transaction History")
        
        # Create axes
        date_axis = QDateTimeAxis()
        date_axis.setFormat("dd-MM-yyyy")
        date_axis.setTitleText("Date")
        value_axis = QValueAxis()
        value_axis.setTitleText("Amount")
        
        chart.addAxis(date_axis, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(value_axis, Qt.AlignmentFlag.AlignLeft)
        
        self.balance_series.attachAxis(date_axis)
        self.balance_series.attachAxis(value_axis)
        
        # Create chart view
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        self.setCentralWidget(chart_view)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TransactionChart()
    window.show()
    sys.exit(app.exec())
