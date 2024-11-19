from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
import pandas as pd
import sys

dummy_data = {
    'Utilization of Credit (10000) received by Gamma from Alpha on 2024-04-03': {
        'LIFO': pd.DataFrame({
            'Value Date': ['2024-04-01'],
            'Name': ['Alpha'],
            'Description': ['Opening Balance'],
            'Debit': [0],
            'Credit': [0],
            'Entity': ['poojan']
        }),
        'FIFO': pd.DataFrame({
            'Value Date': ['2024-04-03 00:00:00', '2024-04-04 00:00:00', '2024-04-05 00:00:00', '2024-04-06 00:00:00', '2024-04-06 00:00:00', '2024-04-07 00:00:00', '2024-04-10 00:00:00'],
            'Name': ['Gamma', 'Gamma', 'Gamma', 'Gamma', 'Gamma', 'Gamma', 'Gamma'], 
            'Description': ['Credit from Alpha', 'Groceries', 'Travel Expense', 'Transfer to Delta', 'Dining', 'Gift to Beta', 'Transfer to Delta'],
            'Debit': [0, 250, 100, 1500, 150, 200, 1500],
            'Credit': [10000, 0, 0, 0, 0, 0, 0],
            'Entity': ['Alpha', None, 'raj', 'Delta', None, 'Beta', 'Delta'],
            'Utilized Credit': [0, 250, 350, 1850, 2000, 2200, 3700],
            'Remaining Credit': [10000, 9750, 9650, 8150, 8000, 7800, 6300]
        }),
    },
    'Utilization of Credit (1000) received by Alpha from Beta on 2024-04-03': {
        'LIFO': pd.DataFrame({
            'Value Date': ['2024-04-01'],
            'Name': ['Beta'],
            'Description': ['Opening Balance'],
            'Debit': [0],
            'Credit': [0],
            'Entity': [None]
        }),
        'FIFO': pd.DataFrame({
            'Value Date': ['2024-04-03 00:00:00', '2024-04-04 00:00:00', '2024-04-05 00:00:00', '2024-04-06 00:00:00', '2024-04-07 00:00:00', '2024-04-08 00:00:00', '2024-04-09 00:00:00'],
            'Name': ['Alpha', 'Alpha', 'Alpha', 'Alpha', 'Alpha', 'Alpha', 'Alpha'],
            'Description': ['Credit from Beta', 'Groceries', 'Electricity Bill', 'Dinner', 'Fuel', 'Online Shopping', 'Gift to Beta'],
            'Debit': [0, 200, 150, 100, 50, 300, 100],
            'Credit': [1000, 0, 0, 0, 0, 0, 0],
            'Entity': ['Beta', 'sanjay', 'gar', 'hdfc', 'bigga', None, 'Beta'],
            'Utilized Credit': [0, 200, 350, 450, 500, 800, 900],
            'Remaining Credit': [1000, 800, 650, 550, 500, 200, 100]
        }),
    },
    'Utilization of Credit (2000) received by Delta from Epsilon on 2024-04-09': {
        'LIFO': pd.DataFrame({
            'Value Date': ['2024-04-08'],
            'Name': ['Epsilon'],
            'Description': ['Transfer to Beta'],
            'Debit': [2500],
            'Credit': [0],
            'Entity': ['Beta']
        }),
        'FIFO': pd.DataFrame({
            'Value Date': ['2024-04-09 00:00:00', '2024-04-10 00:00:00', '2024-04-11 00:00:00', '2024-04-11 00:00:00', '2024-04-12 00:00:00'],
            'Name': ['Delta', 'Delta', 'Delta', 'Delta', 'Delta'],
            'Description': ['Credit from Epsilon', 'Travel', 'Car Maintenance', 'Transfer to Alpha', 'Medical Expense'],
            'Debit': [0, 300, 200, 2000, 150], 
            'Credit': [2000, 0, 0, 0, 0],
            'Entity': ['Epsilon', None, 'google', 'Alpha', 'clone'],
            'Utilized Credit': [0, 300, 500, 2500, 2650],
            'Remaining Credit': [2000, 1700, 1500, -500, -650]
        }),
    },
    'Utilization of Credit (500) received by Beta from Gamma on 2024-04-04': {
        'LIFO': pd.DataFrame({
            'Value Date': ['2024-04-02', '2024-04-03'],
            'Name': ['Gamma', 'Gamma'],
            'Description': ['Opening Balance', 'Credit from Alpha'],
            'Debit': [0, 0],
            'Credit': [0, 10000],
            'Entity': [None, 'Alpha']
        }),
        'FIFO': pd.DataFrame({
            'Value Date': ['2024-04-04 00:00:00', '2024-04-05 00:00:00', '2024-04-05 00:00:00', '2024-04-06 00:00:00', '2024-04-06 00:00:00', '2024-04-07 00:00:00', '2024-04-08 00:00:00', '2024-04-09 00:00:00'],
            'Name': ['Beta', 'Beta', 'Beta', 'Beta', 'Beta', 'Beta', 'Beta', 'Beta'],
            'Description': ['Credit from Gamma', 'Shopping', 'Transfer to Gamma', 'Medical Expense', 'Salary Credit', 'Subscription', 'Gift to Alpha', 'Transfer to Gamma'],
            'Debit': [0, 200, 1000, 300, 0, 100, 150, 1000],
            'Credit': [500, 0, 0, 0, 50000, 0, 0, 0],
            'Entity': ['Gamma', None, 'Gamma', 'bihar', 'cyphersol', None, 'Alpha', 'Gamma'],
            'Utilized Credit': [0, 200, 1200, 1500, 0, 100, 250, 1250],
            'Remaining Credit': [500, 300, -700, -1000, 50500, 50400, 50250, 49250]
        }),
    },
    'Utilization of Credit (3000) received by Epsilon from Delta on 2024-04-14': {
        'LIFO': pd.DataFrame({
            'Value Date': ['2024-04-07', '2024-04-08', '2024-04-09', '2024-04-10', '2024-04-11', '2024-04-11', '2024-04-12'],
            'Name': ['Delta', 'Delta', 'Delta', 'Delta', 'Delta', 'Delta', 'Delta'],
            'Description': ['Transfer to Epsilon', 'Opening Balance', 'Credit from Epsilon', 'Travel', 'Car Maintenance', 'Transfer to Alpha', 'Medical Expense'],
            'Debit': [2000, 0, 0, 300, 200, 2000, 150],
            'Credit': [0, 0, 2000, 0, 0, 0, 0],
            'Entity': ['Epsilon', None, 'Epsilon', None, 'google', 'Alpha', 'clone']
        }),
        'FIFO': pd.DataFrame({
            'Value Date': ['2024-04-14 00:00:00', '2024-04-15 00:00:00', '2024-04-16 00:00:00', '2024-04-17 00:00:00'],
            'Name': ['Epsilon', 'Epsilon', 'Epsilon', 'Epsilon'],
            'Description': ['Credit from Delta', 'Home Renovation', 'Shopping', 'Gift to Gamma'],
            'Debit': [0, 500, 300, 100],
            'Credit': [3000, 0, 0, 0],
            'Entity': ['Delta', 'openai', None, 'Gamma'],
            'Utilized Credit': [0, 500, 800, 900],
            'Remaining Credit': [3000, 2500, 2200, 2100]
        }),
    }
    }

class FIFO_LFIO(QWidget):
    def __init__(self, data):
        super().__init__()
        self.setStyleSheet("background-color: white; color: #3498db;")
        layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)

        for key, value in data.items():
            accordion_item = AccordionItem(key, value['LIFO'], value['FIFO'])
            scroll_layout.addWidget(accordion_item)
        
        scroll_layout.addStretch(1)
        scroll_area.setMinimumHeight(1200)
        layout.addWidget(scroll_area)
        self.setLayout(layout)


class AccordionItem(QFrame):
    def __init__(self, title, lifo_data, fifo_data):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #3498db;
                border-radius: 5px;
                margin: 10px 0;
                background-color: white;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                text-align: left;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                           
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLabel {
                font-weight: bold;
                color: #3498db;
                font-size: 14px;
                margin-top: 10px;
            }
        """)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)

        layout = QVBoxLayout()
        self.toggle_button = QPushButton(f"+ {title}")
        self.toggle_button.clicked.connect(self.toggle_content)

        # LIFO Title
        self.lifo_title = QLabel("LIFO Table")
        self.lifo_title.setVisible(False)  # Initially hidden
        layout.addWidget(self.lifo_title)

        # LIFO HTML Table
        self.lifo_table_view = QWebEngineView()
        self.lifo_table_view.setHtml(self.create_html_table(lifo_data))
        self.lifo_table_view.setVisible(False)
        layout.addWidget(self.lifo_table_view)

        # FIFO Title
        self.fifo_title = QLabel("FIFO Table")
        self.fifo_title.setVisible(False)  # Initially hidden
        layout.addWidget(self.fifo_title)

        # FIFO HTML Table
        self.fifo_table_view = QWebEngineView()
        self.fifo_table_view.setHtml(self.create_html_table(fifo_data))
        self.fifo_table_view.setVisible(False)
        layout.addWidget(self.fifo_table_view)

        layout.insertWidget(0, self.toggle_button)
        self.setLayout(layout)

    def create_html_table(self, data):
        # Start HTML with styling for the table
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                table {
                    width: 100%;
                    border-collapse: collapse;
                }
                th {
                    background-color: #3498db;
                    color: white;
                    padding: 8px;
                    font-size: 13px;
                }
                td {
                    padding: 8px;
                    text-align: center;
                    font-size: 13px;
                    border-bottom: 1px solid #ddd;
                }
                tr:nth-child(even) {
                    background-color: #f2f2f2;
                }
            </style>
        </head>
        <body>
        <table>
        <tr>""" 
        
        # Add headers
        for col in data.columns:
            html += f"<th>{col}</th>"
        html += "</tr>"

        # Add table rows
        for _, row in data.iterrows():
            html += "<tr>"
            for value in row:
                html += f"<td>{value}</td>"
            html += "</tr>"
        
        # Close HTML tags
        html += """
        </table>
        </body>
        </html>
        """
        return html

    def toggle_content(self):
        # Toggle visibility of HTML tables and their titles
        is_visible = not self.lifo_table_view.isVisible()
        
        # Set visibility of titles and tables based on toggle state
        self.lifo_title.setVisible(is_visible)
        self.lifo_table_view.setVisible(is_visible)
        self.fifo_title.setVisible(is_visible)
        self.fifo_table_view.setVisible(is_visible)
        
        # Toggle button text based on visibility state
        if is_visible:
            self.toggle_button.setText(f"- {self.toggle_button.text()[2:]}")
        else:
            self.toggle_button.setText(f"+ {self.toggle_button.text()[2:]}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FIFO_LFIO(dummy_data)
    window.show()
    sys.exit(app.exec())


def create_fifo_lifo_analysis(result):
    return FIFO_LFIO(dummy_data)