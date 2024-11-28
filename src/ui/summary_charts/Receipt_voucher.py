import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                            QHBoxLayout, QComboBox, QPushButton)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtCharts import (QChart, QChartView, QBarSeries, QBarSet, 
                           QBarCategoryAxis, QSplineSeries, QDateTimeAxis, 
                           QValueAxis)
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QGradient
import pandas as pd

class Receiptvoucher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Bank Transaction Analysis")
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background: white;
                min-width: 150px;
            }
            QPushButton {
                padding: 5px 15px;
                background-color: #1a73e8;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1557b0;
            }
        """)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Load data
        self.data = {
            'Date': ['01-04-2023', '03-04-2023', '04-04-2023', '07-04-2023', '07-04-2023', '08-04-2023'],
            'Amount': [0.00, 4800.00, 300000.00, 1000.00, 1000.00, 3000.00],
            'Narration': ['openingbalance', 'upi/cr', 'loantomayurkhai', 'upi/cr', 'upi/cr', 'upi/cr']
        }
        self.df = pd.DataFrame(self.data)
        self.df['Date'] = pd.to_datetime(self.df['Date'], format='%d-%m-%Y')
        
        # Add controls
        controls_layout = QHBoxLayout()
        self.chart_type = QComboBox()
        self.chart_type.addItems(['Bar + Spline'])
        self.chart_type.currentTextChanged.connect(self.update_chart)
        
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(['Light', 'Dark', 'Blue', 'Brown'])
        self.theme_selector.currentTextChanged.connect(self.update_theme)
        
        controls_layout.addWidget(self.chart_type)
        controls_layout.addWidget(self.theme_selector)
        controls_layout.addStretch()
        
        main_layout.addLayout(controls_layout)
        
        # Create charts container
        charts_widget = QWidget()
        charts_layout = QHBoxLayout(charts_widget)
        
        # Create and setup charts
        self.create_charts(charts_layout)
        
        # Add web view for statistics
        web_view = QWebEngineView()
        web_view.setMaximumHeight(200)
        
        # Generate statistics HTML
        stats_html = self.generate_stats_html()
        web_view.setHtml(stats_html)
        
        # Add to main layout
        main_layout.addWidget(web_view)
        main_layout.addWidget(charts_widget)

    def generate_stats_html(self):
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
                }}
                .stats-container {{
                    display: flex;
                    justify-content: space-around;
                    margin-bottom: 20px;
                    gap: 20px;
                }}
                .stat-box {{
                    flex: 1;
                    background: white;
                    padding: 20px;
                    border-radius: 12px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    text-align: center;
                    transition: transform 0.2s;
                }}
                .stat-box:hover {{
                    transform: translateY(-5px);
                }}
                .stat-box h3 {{
                    color: #1a73e8;
                    margin: 0 0 10px 0;
                    font-size: 1.2em;
                }}
                .stat-box p {{
                    font-size: 1.5em;
                    margin: 0;
                    color: #202124;
                    font-weight: 500;
                }}
                .trend {{
                    font-size: 0.9em;
                    color: #34a853;
                    margin-top: 8px;
                }}
            </style>
        </head>
        <body>
            <div class="stats-container">
                <div class="stat-box">
                    <h3>Total Transactions</h3>
                    <p>{len(self.df)}</p>
                    <div class="trend">+{len(self.df)} this month</div>
                </div>
                <div class="stat-box">
                    <h3>Total Credits</h3>
                    <p>₹{self.df['Amount'].sum():,.2f}</p>
                    <div class="trend">+{(self.df['Amount'].sum()/self.df['Amount'].sum()*100):.1f}% vs last month</div>
                </div>
                <div class="stat-box">
                    <h3>Average Transaction</h3>
                    <p>₹{self.df['Amount'].mean():,.2f}</p>
                    <div class="trend">Typical range: ₹1,000 - ₹300,000</div>
                </div>
                <div class="stat-box">
                    <h3>Largest Transaction</h3>
                    <p>₹{self.df['Amount'].max():,.2f}</p>
                    <div class="trend">On {self.df.loc[self.df['Amount'].idxmax(), 'Date'].strftime('%d-%m-%Y')}</div>
                </div>
            </div>
        </body>
        </html>
        """

    def create_charts(self, layout):
        # Create Bar Chart
        bar_chart = QChart()
        bar_series = QBarSeries()
        bar_set = QBarSet("Transactions")
        
        for amount in self.df['Amount']:
            bar_set.append(amount)
        
        bar_series.append(bar_set)
        bar_chart.addSeries(bar_series)
        
        # Create Spline Chart for running balance
        spline_chart = QChart()
        spline_series = QSplineSeries()
        spline_series.setName("Running Balance")
        
        running_balance = 0
        for i, row in self.df.iterrows():
            running_balance += row['Amount']
            # Convert timestamp to milliseconds for QDateTime
            date = row['Date'].to_pydatetime()
            qt_date = QDateTime(date)
            spline_series.append(qt_date.toMSecsSinceEpoch(), running_balance)
        
        spline_chart.addSeries(spline_series)
        
        # Setup axes for both charts
        self.setup_axes(bar_chart, spline_chart)
        
        # Style the charts
        self.style_charts(bar_chart, spline_chart)
        
        # Create chart views
        bar_view = QChartView(bar_chart)
        spline_view = QChartView(spline_chart)
        
        # Enable antialiasing
        bar_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        spline_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Add to layout
        layout.addWidget(bar_view)
        layout.addWidget(spline_view)
        
        self.bar_chart = bar_chart
        self.spline_chart = spline_chart
        self.bar_view = bar_view
        self.spline_view = spline_view

    def setup_axes(self, bar_chart, spline_chart):
        # Bar Chart Axes
        categories = [date.strftime('%d-%m') for date in self.df['Date']]
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        bar_chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        axis_y = QValueAxis()
        axis_y.setTitleText("Transaction Amount (₹)")
        bar_chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        
        # Spline Chart Axes
        date_axis = QDateTimeAxis()
        date_axis.setFormat("dd-MM-yyyy")
        date_axis.setTitleText("Date")
        spline_chart.addAxis(date_axis, Qt.AlignmentFlag.AlignBottom)
        
        value_axis = QValueAxis()
        value_axis.setTitleText("Running Balance (₹)")
        value_axis.setLabelFormat("%.2f")
        spline_chart.addAxis(value_axis, Qt.AlignmentFlag.AlignLeft)
        
        # Attach axes to series
        bar_chart.series()[0].attachAxis(axis_x)
        bar_chart.series()[0].attachAxis(axis_y)
        spline_chart.series()[0].attachAxis(date_axis)
        spline_chart.series()[0].attachAxis(value_axis)

    def style_charts(self, bar_chart, spline_chart):
        # Common styling
        for chart in [bar_chart, spline_chart]:
            chart.setBackgroundVisible(False)
            chart.setDropShadowEnabled(True)
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        
        # Bar Chart specific
        bar_chart.setTitle("Individual Transactions")
        
        # Spline Chart specific
        spline_chart.setTitle("Running Balance Over Time")
        
        # Apply gradient to bar series
        bar_series = bar_chart.series()[0]
        bar_set = bar_series.barSets()[0]
        gradient = QLinearGradient(0, 0, 0, 1)
        gradient.setColorAt(0, QColor("#1a73e8"))
        gradient.setColorAt(1, QColor("#1557b0"))
        gradient.setCoordinateMode(QGradient.CoordinateMode.ObjectBoundingMode)
        bar_set.setBrush(gradient)

    def update_chart(self, chart_type):
        if chart_type == 'Bar Only':
            self.spline_view.hide()
            self.bar_view.show()
        elif chart_type == 'Spline Only':
            self.bar_view.hide()
            self.spline_view.show()
        else:
            self.bar_view.show()
            self.spline_view.show()

    def update_theme(self, theme):
        themes = {
            'Light': (QColor("#ffffff"), QColor("#000000"), QColor("#1a73e8")),
            'Dark': (QColor("#2d2d2d"), QColor("#ffffff"), QColor("#00ff00")),
            'Blue': (QColor("#e8f0fe"), QColor("#1a73e8"), QColor("#1557b0")),
            'Brown': (QColor("#f5e6d3"), QColor("#7c4a03"), QColor("#c17f59"))
        }
        
        background, text, accent = themes[theme]
        
        for chart in [self.bar_chart, self.spline_chart]:
            chart.setBackgroundBrush(background)
            chart.setTitleBrush(text)
            
            for axis in chart.axes():
                axis.setLabelsBrush(text)
                axis.setTitleBrush(text)
            
            if isinstance(chart.series()[0], QBarSeries):
                gradient = QLinearGradient(0, 0, 0, 1)
                gradient.setColorAt(0, accent)
                gradient.setColorAt(1, accent.darker(120))
                gradient.setCoordinateMode(QGradient.CoordinateMode.ObjectBoundingMode)
                chart.series()[0].barSets()[0].setBrush(gradient)
            else:
                chart.series()[0].setColor(accent)

def main():
    app = QApplication(sys.argv)
    window = Receiptvoucher()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()