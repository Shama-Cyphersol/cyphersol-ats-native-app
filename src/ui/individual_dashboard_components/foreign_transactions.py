from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QLabel
from utils.dynamic_table import DynamicDataTable
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from PyQt6.QtCore import Qt


class ForeignTransactionsWidget(QWidget):
    def __init__(self, df=None, parent=None):
        super().__init__(parent)
        
        # If no DataFrame is provided, generate dummy data
        # if df is None:
        #     df = self.generate_dummy_foreign_transactions()

         # Check if lifo_fifo_analysis_data is empty
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.foreign_transaction_data = df
        try:
            if self.foreign_transaction_data.empty:
                self.is_data_empty = True
        except:
            if not self.foreign_transaction_data:
                self.is_data_empty = True
                
        if self.is_data_empty:
            no_data_label = QLabel(f"No data available.")
            no_data_label.setStyleSheet("""
               QLabel {
                    font-size: 16px;
                    color: #666;
                    padding: 20px;
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    margin: 20px;
                }
            """)
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(no_data_label)
            # scroll_area.setMinimumHeight(500)

        else:
        
            

            self.create_table(df)
        self.setLayout(self.layout)

    def generate_dummy_foreign_transactions(self, num_rows=200):
        """
        Generate a dummy DataFrame for Foreign Transactions
        """
        np.random.seed(42)
        start_date = datetime(2023, 1, 1)

        data = {
            'Transaction_ID': [f'FT-{np.random.randint(10000, 99999)}' for _ in range(num_rows)],
            'Transaction_Date': [start_date + timedelta(days=np.random.randint(0, 365)) for _ in range(num_rows)],
            'Country': np.random.choice(['United Kingdom', 'Germany', 'France', 'Japan', 'China', 'Canada', 'Australia', 'Brazil', 'India', 'UAE'], num_rows),
            'Transaction_Type': np.random.choice(['Purchase', 'Refund', 'Transfer', 'Withdrawal'], num_rows),
            'Payment_Method': np.random.choice(['Credit Card', 'Debit Card', 'Bank Transfer', 'Digital Wallet'], num_rows),
            'Currency': np.random.choice(['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'BRL', 'INR', 'AED'], num_rows),
            'Amount': np.round(np.random.uniform(10, 5000, num_rows), 2),
            'Exchange_Rate': np.round(np.random.uniform(0.7, 1.5, num_rows), 4),
            'Merchant_Name': [f'Merchant_{i}' for i in np.random.randint(1, 200, num_rows)],
            'Is_Fraudulent': np.random.choice([True, False], num_rows, p=[0.05, 0.95]),
            'Customer_ID': [f'CUS-{np.random.randint(1000, 9999)}' for _ in range(num_rows)]
        }

        df = pd.DataFrame(data)
        df['Transaction_Date'] = pd.to_datetime(df['Transaction_Date'])
        return df

    def create_table(self, df):
        """
        Create a dynamic table for Foreign Transactions
        """
        self.foreign_transactions_table = DynamicDataTable(
            df=df,
            rows_per_page=10,
            table_for="foreign_transactions",
        )
        self.layout.addWidget(self.foreign_transactions_table)

    def update_table(self, new_df):
        """
        Update the table with a new DataFrame
        """
        if hasattr(self, 'foreign_transactions_table'):
            self.layout.removeWidget(self.foreign_transactions_table)
            self.foreign_transactions_table.deleteLater()

        self.create_table(new_df)