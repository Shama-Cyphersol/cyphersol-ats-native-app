from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QTableWidget,
    QHeaderView,
    QTableWidgetItem
)
from .Summary_particular import SummaryParticular
from .Summary_income import IncomeSummaryDashboard
from .Summary_important_expenses import SummaryImportantExpenses 
from .Summary_otherExpenses import SummaryOtherExpenses
import pandas as pd
class SummaryWindow(QMainWindow):
    def __init__(self,data):
        super().__init__()
        self.setWindowTitle("Financial Analytics Dashboard - Summary")
        self.setGeometry(100, 100, 1200, 900)  # Adjust size as needed

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Add widgets vertically
        self.particular_widget = SummaryParticular(data=data[0])
        layout.addWidget(self.particular_widget)

        self.income_widget = IncomeSummaryDashboard(data=data[1])
        layout.addWidget(self.income_widget)

        self.important_expenses_widget = SummaryImportantExpenses(data=data[2])
        layout.addWidget(self.important_expenses_widget)

        self.other_expenses_widget = SummaryOtherExpenses(data=data[3])  # Add Other Expenses widget
        layout.addWidget(self.other_expenses_widget)

        # self.create_data_table(layout,"Summary Particular Data Table", headers=  ["Value Date", "Description", "Debit", "Credit", "Balance"] ,type="particular",data=data[0])
        # Example call with headers that represent the columns in your particulars data
        headers = ["Particulars", "Dec-2022", "Jan-2023", "Feb-2023", "Mar-2023", "Apr-2023", 
                "May-2023", "Jun-2023", "Jul-2023", "Aug-2023", "Sep-2023", "Oct-2023", 
                "Nov-2023", "Total"]

        # self.create_data_table_particular(layout, "Summary Particular Data Table", headers, type="particular", data=data[0])

        headers = ["Income / Receipts","Dec-2022", "Jan-2023", "Feb-2023", "Mar-2023", "Apr-2023", 
           "May-2023", "Jun-2023", "Jul-2023", "Aug-2023", "Sep-2023", "Oct-2023", 
           "Nov-2023", "Total"]
        
        # self.create_income_summary_table(layout, "Income Summary Data Table", headers, data=data[1])
        headers = ["Important Expenses / Payments", "Dec-2022", "Jan-2023", "Feb-2023", "Mar-2023", "Apr-2023", 
           "May-2023", "Jun-2023", "Jul-2023", "Aug-2023", "Sep-2023", "Oct-2023", 
           "Nov-2023", "Total"]
        # self.create_important_expenses_table(layout, "Important Expenses Data Table", headers, data=data[2])
        headers = ["Other Expenses / Payment", "Dec-2022", "Jan-2023", "Feb-2023", "Mar-2023", "Apr-2023", 
           "May-2023", "Jun-2023", "Jul-2023", "Aug-2023", "Sep-2023", "Oct-2023", 
           "Nov-2023", "Total"]
        # self.create_expenses_summary_table(layout, "Other Expenses Data Table", headers, data=data[3])


    def create_data_table_particular(self, layout, title, headers, type, data):
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
                margin-bottom: 10px;
            }
        """)

        # Add the title label to the layout
        layout.addWidget(title_label)

        table = QTableWidget()
        table.setRowCount(len(data))  # Set row count based on the number of particulars
        table.setColumnCount(len(headers))  # Set column count based on headers (including Total)
        table.setHorizontalHeaderLabels(headers)
        table.setSortingEnabled(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setAlternatingRowColors(True)

        table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
                color: #333333;  /* Set text color to dark gray for visibility */
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
        table.setFixedHeight(table.rowHeight(0) * 5 + table.horizontalHeader().height())

        for i, row in data.iterrows():
            # The first column is the particulars
            table.setItem(i, 0, QTableWidgetItem(row["Particulars"]))

            # Populate the remaining columns with the data for each month and total
            for j in range(1, len(headers)):
                # Set the respective month or total column
                table.setItem(i, j, QTableWidgetItem(f"₹{row[headers[j]]:.2f}" if pd.notnull(row[headers[j]]) else "N/A"))

        layout.addWidget(table)


    def create_income_summary_table(self, layout, title, headers, data):
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
                margin-bottom: 10px;
            }
        """)

        # Add the title label to the layout
        layout.addWidget(title_label)

        table = QTableWidget()
        table.setRowCount(len(data))  # Set row count based on the number of income items
        table.setColumnCount(len(headers))  # Set column count based on headers (including Total)
        table.setHorizontalHeaderLabels(headers)
        table.setSortingEnabled(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setAlternatingRowColors(True)

        table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
                color: #333333;  /* Set text color to dark gray for visibility */
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
        table.setFixedHeight(table.rowHeight(0) * 10 + table.horizontalHeader().height())

        for i, row in data.iterrows():
            # The first column is the income source
            table.setItem(i, 0, QTableWidgetItem(row["Income / Receipts"]))

            # Populate the remaining columns with the data for each month and total
            for j in range(1, len(headers)):
                # Set the respective month or total column
                table.setItem(i, j, QTableWidgetItem(f"₹{row[headers[j]]:.2f}" if pd.notnull(row[headers[j]]) else "N/A"))

        layout.addWidget(table)

    def create_expenses_summary_table(self, layout, title, headers, data):
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
                margin-bottom: 10px;
            }
        """)

        # Add the title label to the layout
        layout.addWidget(title_label)

        table = QTableWidget()
        table.setRowCount(len(data))  # Set row count based on the number of expense items
        table.setColumnCount(len(headers))  # Set column count based on headers (including Total)
        table.setHorizontalHeaderLabels(headers)
        table.setSortingEnabled(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setAlternatingRowColors(True)

        table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
                color: #333333;  /* Set text color to dark gray for visibility */
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
        table.setFixedHeight(table.rowHeight(0) * 10 + table.horizontalHeader().height())

        for i, row in data.iterrows():
            # The first column is the expense item name
            table.setItem(i, 0, QTableWidgetItem(row["Other Expenses / Payments"]))

            # Populate the remaining columns with the data for each month and total
            for j in range(1, len(headers)):
                # Set the respective month or total column
                table.setItem(i, j, QTableWidgetItem(f"₹{row[headers[j]]:.2f}" if pd.notnull(row[headers[j]]) else "N/A"))

        layout.addWidget(table)



    def create_important_expenses_table(self, layout, title, headers, data):
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
                margin-bottom: 10px;
            }
        """)

        # Add the title label to the layout
        layout.addWidget(title_label)

        table = QTableWidget()
        table.setRowCount(len(data))  # Set row count based on the number of important expense items
        table.setColumnCount(len(headers))  # Set column count based on headers (including Total)
        table.setHorizontalHeaderLabels(headers)
        table.setSortingEnabled(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setAlternatingRowColors(True)

        table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
                color: #333333;  /* Set text color to dark gray for visibility */
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
        table.setFixedHeight(table.rowHeight(0) * 10 + table.horizontalHeader().height())

        for i, row in data.iterrows():
            # The first column is the expense item name
            table.setItem(i, 0, QTableWidgetItem(row["Important Expenses / Payments"]))

            # Populate the remaining columns with the data for each month and total
            for j in range(1, len(headers)):
                # Set the respective month or total column
                table.setItem(i, j, QTableWidgetItem(f"₹{row[headers[j]]:.2f}" if pd.notnull(row[headers[j]]) else "N/A"))

        layout.addWidget(table)