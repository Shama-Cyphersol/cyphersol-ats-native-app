from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCharts import *
import sys
import json

class BankTransactionDashboard(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("Bank Transactions Analysis")
        self.resize(2000, 1000)
        self.data = data

        # Data setup
        self.dates = self.data["Value Date"].dt.strftime("%d-%m-%Y").tolist()
        self.debits = self.data["Debit"].tolist()
        self.credits = self.data["Credit"].tolist()
        self.balances = self.data["Balance"].tolist()

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(15, 15, 15, 15)

        # Create chart layout
        chart_layout = QVBoxLayout()
        layout.addLayout(chart_layout)
        chart_layout.setSpacing(20)

        # Add charts and info
        self.create_balance_line_chart(chart_layout)
        self.create_transaction_bar_chart(chart_layout)
        self.create_pie_chart(chart_layout)
        self.add_styled_info(chart_layout)
        
        # Add HTML table
        self.create_html_table(layout)

    def create_balance_line_chart(self, layout):
        chart = QChart()
        series = QLineSeries()
        series.setPointsVisible(True)
        series.setColor(QColor("#3498db"))
        series.hovered.connect(self.handle_line_hover)

        for i, date_str in enumerate(self.dates):
            date = QDateTime.fromString(date_str, "dd-MM-yyyy")
            series.append(date.toMSecsSinceEpoch(), self.balances[i])

        chart.addSeries(series)
        chart.setTitle("Account Balance Over Time")
        chart.setBackgroundBrush(QBrush(QColor("#f5f5f5")))

        axis_x = QDateTimeAxis()
        axis_x.setFormat("dd-MM-yyyy")
        axis_x.setLabelsAngle(-45)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setTitleText("Balance (₹)")
        axis_y.setGridLineColor(QColor("#dddddd"))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setFixedHeight(500)

        layout.addWidget(chart_view)

    def create_transaction_bar_chart(self, layout):
        chart = QChart()
        series = QBarSeries()

        debit_set = QBarSet("Debit Amount")
        credit_set = QBarSet("Credit Amount")
        debit_set.setColor(QColor("#e74c3c"))
        credit_set.setColor(QColor("#2ecc71"))

        debit_set.append(self.debits)
        credit_set.append(self.credits)

        series.append(debit_set)
        series.append(credit_set)
        chart.addSeries(series)
        chart.setTitle("Debit and Credit Transactions")
        chart.setBackgroundBrush(QBrush(QColor("#f5f5f5")))

        axis_x = QBarCategoryAxis()
        axis_x.append(self.dates)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axis_x)

        axis_y = QValueAxis()
        axis_y.setTitleText("Amount (₹)")
        axis_y.setGridLineColor(QColor("#dddddd"))
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axis_y)

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setFixedHeight(500)

        layout.addWidget(chart_view)

    def create_pie_chart(self, layout):
        chart = QChart()
        series = QPieSeries()
        threshold = 5000

        amount_groups = {}
        other_count = 0

        for debit in self.debits:
            if debit > 0:
                rounded = round(debit, 1)
                if rounded < threshold:
                    other_count += 1
                else:
                    amount_groups[rounded] = amount_groups.get(rounded, 0) + 1

        for amount, count in amount_groups.items():
            slice = QPieSlice(f"₹{amount} ({count} times)", count)
            slice.setColor(QColor("#3498db").lighter(100 + count * 10))
            slice.hovered.connect(self.handle_pie_hover)
            series.append(slice)

        if other_count > 0:
            others_slice = QPieSlice(f"Others (<₹{threshold})", other_count)
            others_slice.setColor(QColor("#95a5a6"))
            series.append(others_slice)

        chart.addSeries(series)
        chart.setTitle("Distribution of Debit Transactions")
        chart.setBackgroundBrush(QBrush(QColor("#f5f5f5")))

        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        chart_view.setFixedHeight(500)
        chart.setTitleFont(QFont("Arial", 16))

        layout.addWidget(chart_view)

    def handle_pie_hover(self, state):
        slice = self.sender()
        if state:
            label_parts = slice.label().split()
            amount = label_parts[0]
            count = slice.value()
            percentage = (slice.percentage() * 100)
            QToolTip.showText(QCursor.pos(), f"Amount: {amount}\nCount: {int(count)} transactions\nPercentage: {percentage:.1f}%")
            slice.setExploded(True)
        else:
            slice.setExploded(False)

    def handle_line_hover(self, point, state):
        if state:
            date = QDateTime.fromMSecsSinceEpoch(int(point.x()))
            QToolTip.showText(QCursor.pos(), f"Date: {date.toString('dd-MM-yyyy')}\nBalance: ₹{point.y():,.2f}")

    def add_styled_info(self, layout):
        web_view = QWebEngineView()
        total_debits = sum(self.debits)
        avg_debit = total_debits / len(self.debits)
        max_debit = max(self.debits)
        min_debit = min(self.debits)
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5; }}
                .stats-container {{ background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .stat-item {{ margin-bottom: 15px; }}
                .stat-label {{ color: #666; font-size: 14px; }}
                .stat-value {{ color: #333; font-size: 18px; font-weight: bold; }}
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
        layout.addWidget(web_view)

    def create_html_table(self, layout):
        web_view = QWebEngineView()
        
        # Prepare table data
        table_data = []
        for _, row in self.data.iterrows():
            table_data.append({
                'date': row["Value Date"].strftime("%d-%m-%Y"),
                'description': row["Description"],
                'debit': f"₹{row['Debit']:.2f}",
                'credit': f"₹{row['Credit']:.2f}",
                'balance': f"₹{row['Balance']:.2f}"
            })

        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Transaction Details</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}
                .table-container {{
                    margin: 20px;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: 20px;
                    overflow: hidden;
                }}
                .table-header {{
                    text-align: center;
                    padding: 10px;
                    color: #2c3e50;
                    font-size: 1.2rem;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }}
                
                th, td {{
                    padding: 12px;
                    text-align: center;
                    border-bottom: 1px solid #e2e8f0;
                }}
                
                th {{
                    background-color: #3498db;
                    color: white;
                    font-weight: bold;
                    position: sticky;
                    top: 0;
                }}
                tr:hover {{
                    background-color: #f8fafc;
                }}
                .pagination {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin-top: 20px;
                    gap: 10px;
                }}
                .pagination button {{
                    padding: 8px 16px;
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: bold;
                }}
                .pagination button:disabled {{
                    background-color: #bdc3c7;
                    cursor: not-allowed;
                }}
                .pagination span {{
                    font-weight: bold;
                    color: #2c3e50;
                }}
                .description-column {{
                    text-align: left;
                }}
            </style>
        </head>
        <body>
            <div class="table-container">
                <div class="table-header">Transaction Details</div>
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th class="description-column">Description</th>
                            <th>Debit</th>
                            <th>Credit</th>
                            <th>Balance</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody">
                    </tbody>
                </table>
                <div class="pagination">
                    <button id="prevBtn" onclick="previousPage()">Previous</button>
                    <span id="pageInfo"></span>
                    <button id="nextBtn" onclick="nextPage()">Next</button>
                </div>
            </div>
            
            <script>
                const rowsPerPage = 10;
                let currentPage = 1;
                const data = {json.dumps(table_data)};
                const totalPages = Math.ceil(data.length / rowsPerPage);

                function updateTable() {{
                    const start = (currentPage - 1) * rowsPerPage;
                    const end = start + rowsPerPage;
                    const pageData = data.slice(start, end);
                    
                    const tableBody = document.getElementById('tableBody');
                    tableBody.innerHTML = '';
                    
                    pageData.forEach(row => {{
                        const tr = `
                            <tr>
                                <td>${{row.date}}</td>
                                <td class="description-column">${{row.description}}</td>
                                <td>${{row.debit}}</td>
                                <td>${{row.credit}}</td>
                                <td>${{row.balance}}</td>
                            </tr>
                        `;
                        tableBody.innerHTML += tr;
                    }});
                    
                    document.getElementById('pageInfo').textContent = `Page ${{currentPage}} of ${{totalPages}}`;
                    document.getElementById('prevBtn').disabled = currentPage === 1;
                    document.getElementById('nextBtn').disabled = currentPage === totalPages;
                }}

                function nextPage() {{
                    if (currentPage < totalPages) {{
                        currentPage++;
                        updateTable();
                    }}
                }}

                function previousPage() {{
                    if (currentPage > 1) {{
                        currentPage--;
                        updateTable();
                    }}
                }}

                // Initial table load
                updateTable();
            </script>
        </body>
        </html>
        '''
        
        web_view.setHtml(html_content)
        web_view.setMinimumHeight(900)  # Set minimum height for the table
        layout.addWidget(web_view)