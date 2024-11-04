import sys
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget,QLabel, QWidgetItem,QTableView,QTableWidgetItem,QTableWidget,QHeaderView
from PyQt6.QtWebEngineWidgets import QWebEngineView
import pandas as pd

class Creditors(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.setGeometry(100, 100, 1200, 600)

        # Create a QWebEngineView
        self.browser = QWebEngineView()
        
        # Sort data by date
        data = data.sort_values(by="Value Date")
        print(data.head())
        self.data= data

        # Extract data from the DataFrame
        dates = data["Value Date"].dt.strftime("%d-%m-%Y").tolist()
        debits = data["Debit"].tolist() if "Debit" in data.columns else []
        balances = data["Balance"].tolist()

        # Create the HTML and JavaScript for the chart
        html_content = self.create_html(dates, debits, balances)
        
        # Load the HTML content into the QWebEngineView
        self.browser.setHtml(html_content)
        self.browser.setFixedHeight(600)


        layout = QVBoxLayout()
        layout.addWidget(self.browser)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # self.create_data_table_creditor(layout,title="Creditor Data Table", headers=["Value Date","Description","Debit","Credit","Balance","Category"],data=self.data)

    def create_html(self, dates, debits, balances):
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
                var debits = {json.dumps(debits)};
                var balances = {json.dumps(balances)};
                
                var trace1 = {{
                    x: dates,
                    y: debits,
                    name: 'Debit Amount',
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
                    xaxis: {{
                        title: 'Date',
                        tickformat: "%d-%m-%Y",
                         tickangle: -45,  // Rotate x-axis labels for better readability
                    }},
                    yaxis: {{
                        title: 'Debit Amount',
                    }},
                    yaxis2: {{
                        title: 'Balance',
                        overlaying: 'y',
                        side: 'right',
                    }},
                    barmode: 'group',
                    legend: {{
                        orientation: 'h',
                        x: 0.5,
                        y: 1.15,
                        xanchor: 'center',
                        yanchor: 'bottom'
                    }},
                    margin: {{
                        b: 100  // Increase bottom margin for space below the x-axis
                    }}
                }};
                
                Plotly.newPlot('chart', data, layout);
            </script>
        </body>
        </html>
        """
        return html
    
    def create_data_table_creditor(self, layout, title, headers, data):
        # Set up the title label with styling
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)  # Add title to the layout

        # Initialize the table with row and column counts
        table = QTableWidget()
        table.setRowCount(len(data))  # Set row count based on data length
        table.setColumnCount(len(headers))  # Set column count based on headers
        table.setHorizontalHeaderLabels(headers)
        table.setSortingEnabled(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setAlternatingRowColors(True)

        # Table style settings
        table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
                color: #333333;  /* Set text color */
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                font-weight: bold;
                color: black;
                padding: 6px;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)

        # Adjust table height based on row count
        table.setFixedHeight(table.rowHeight(0) * min(10, len(data)) + table.horizontalHeader().height())

        # Populate the table with data
        for i, row in data.iterrows():
            table.setItem(i, 0, QTableWidgetItem(row["Value Date"]))
            table.setItem(i, 1, QTableWidgetItem(row["Description"]))
            
            # Format Debit and Credit columns with currency and commas
            table.setItem(i, 2, QTableWidgetItem(f"₹{float(row['Debit']):,.2f}" if pd.notnull(row['Debit']) else "N/A"))
            table.setItem(i, 3, QTableWidgetItem(f"₹{float(row['Credit']):,.2f}" if pd.notnull(row['Credit']) else "N/A"))
            
            # Format Balance with currency and commas
            table.setItem(i, 4, QTableWidgetItem(f"₹{float(row['Balance']):,.2f}" if pd.notnull(row['Balance']) else "N/A"))

            # Display the Category as is
            table.setItem(i, 5, QTableWidgetItem(row["Category"]))

        layout.addWidget(table)