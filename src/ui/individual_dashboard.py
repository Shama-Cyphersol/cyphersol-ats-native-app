import sys
import json
import tempfile
import plotly.graph_objs as go
from PyQt6.QtCore import QDateTime, Qt, QUrl
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QScrollArea)
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from PyQt6.QtWebEngineWidgets import QWebEngineView

from utils.summary_charts.transactions import BankTransactionDashboard
from utils.summary_charts.Creditors import TransactionChart
from utils.summary_charts.EOD_balance import EODBalanceChart
from utils.summary_charts.Debtors import DebtorsChart
from utils.summary_charts.Cash_withdrawal import StackedBarChart
from utils.summary_charts.Cash_Deposit import CashDeposit
from utils.summary_charts.Payment_Voucher import PaymentDashboard
from utils.summary_charts.Summary_important_expenses import ImportantExpenses
from utils.summary_charts.Summary_particular import Particular
from utils.summary_charts.Summary_income import Income
from utils.summary_charts.Summary_otherExpenses import OtherExpenses
from utils.summary_charts.Reversal import Reversal
from utils.summary_charts.Suspense_debit import SuspenseDebit
from utils.summary_charts.Receipt_voucher import Receiptvoucher
from utils.summary_charts.Suspense_Credit import SuspenseCredit
class IndividualDashboard(QMainWindow):
    def __init__(self,case_id,name):
        super().__init__()
        self.setWindowTitle("Combined Visualization Overview")
        self.setGeometry(100, 100, 1200, 800)

        self.case_id = case_id
        self.name = name
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setCentralWidget(scroll_area)
        
        # Main widget and layout
        main_widget = QWidget()
        scroll_area.setWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        title_bank_txn = QLabel("Bank Transaction Analysis")
        title_bank_txn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_bank_txn.setStyleSheet("QLabel { font-size: 16pt; font-weight: bold; margin: 10px; }")
        layout.addWidget(title_bank_txn)
        bank_txn_dashboard = BankTransactionDashboard()
        bank_txn_dashboard.setFixedHeight(700)
        layout.addWidget(bank_txn_dashboard)


        title_eod = QLabel("EOD Balance Visualization")
        title_eod.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_eod.setStyleSheet("QLabel { font-size: 16pt; font-weight: bold; margin: 10px; }")
        layout.addWidget(title_eod)
        eod_view = EODBalanceChart()
        eod_view.setFixedHeight(700)
        layout.addWidget(eod_view)

        
        title1 = QLabel("Transaction History (Creditors)")
        title1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title1.setStyleSheet("QLabel { font-size: 16pt; font-weight: bold; margin: 10px; }")
        layout.addWidget(title1)
        txn_history_chart = TransactionChart()
        txn_history_chart.setFixedHeight(700)
        layout.addWidget(txn_history_chart)
        

        title2 = QLabel("Financial Transactions (Debtors)")
        title2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title2.setStyleSheet("QLabel { font-size: 16pt; font-weight: bold; margin: 10px; }")
        layout.addWidget(title2)
        fin_txn_chart = DebtorsChart()
        fin_txn_chart.setFixedHeight(700)
        layout.addWidget(fin_txn_chart)

        
        title3 = QLabel("Cash Withdrawal Analysis")
        title3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title3.setStyleSheet("QLabel { font-size: 16pt; font-weight: bold; margin: 10px; }")
        layout.addWidget(title3)
        cash_withdrawal = StackedBarChart()
        cash_withdrawal.setFixedHeight(700)
        layout.addWidget(cash_withdrawal)

        title4 = QLabel("Cash Deposit Analysis")
        title4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title4.setStyleSheet("QLabel { font-size: 16pt; font-weight: bold; margin: 10px; }")
        layout.addWidget(title4)
        cash_deposit = CashDeposit()
        cash_deposit.setFixedHeight(700)
        layout.addWidget(cash_deposit)
    
        

        title6 = QLabel("Payment Voucher Analysis")
        title6.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title6.setStyleSheet("QLabel { font-size: 16pt; font-weight: bold; margin: 10px; }")
        layout.addWidget(title6)
        payment_voucher = PaymentDashboard()
        payment_voucher.setFixedHeight(700)
        layout.addWidget(payment_voucher)


        title7 = QLabel("Important Expenses Analysis")
        title7.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title7.setStyleSheet("QLabel { font-size: 16pt; font-weight: bold; margin: 10px; }")
        layout.addWidget(title7)
        important_expenses = ImportantExpenses()
        important_expenses.setFixedHeight(800)
        layout.addWidget(important_expenses) 


        title8 = QLabel("Particular Analysis")
        title8.setAlignment(Qt.AlignmentFlag.AlignCenter)    
        title8.setStyleSheet("QLabel { font-size: 16pt; font-weight: bold; margin: 10px; }")
        layout.addWidget(title8)
        particular = Particular()
        particular.setFixedHeight(700)
        layout.addWidget(particular)


        title9 = QLabel("Income Analysis")
        title9.setAlignment(Qt.AlignmentFlag.AlignCenter)    
        title9.setStyleSheet("QLabel { font-size: 16pt; font-weight: bold; margin: 10px; }")
        layout.addWidget(title9)
        income = Income()
        income.setFixedHeight(700)
        layout.addWidget(income)

        title10 = QLabel("Other Expenses Analysis")
        title10.setAlignment(Qt.AlignmentFlag.AlignCenter)    
        title10.setStyleSheet("QLabel { font-size: 16pt; font-weight: bold; margin: 10px; }")
        layout.addWidget(title10)
        other_expenses = OtherExpenses()
        other_expenses.setFixedHeight(700)
        layout.addWidget(other_expenses)


        title11 = QLabel("Reversal Analysis")
        title11.setAlignment(Qt.AlignmentFlag.AlignCenter)    
        title11.setStyleSheet("QLabel { font-size: 16pt; font-weight: bold; margin: 10px; }")
        layout.addWidget(title11)
        reversal = Reversal()
        reversal.setFixedHeight(700)
        layout.addWidget(reversal)

        title12 = QLabel("Suspense Debit Analysis")
        title12.setAlignment(Qt.AlignmentFlag.AlignCenter)    
        title12.setStyleSheet("QLabel { font-size: 16pt; font-weight: bold; margin: 10px; }")
        layout.addWidget(title12)
        suspense_debit = SuspenseDebit()
        suspense_debit.setFixedHeight(700)    
        layout.addWidget(suspense_debit)

        title13 = QLabel("Receipt Voucher Analysis")
        title13.setAlignment(Qt.AlignmentFlag.AlignCenter)    
        title13.setStyleSheet("QLabel { font-size: 16pt; font-weight: bold; margin: 10px; }")    
        layout.addWidget(title13)
        receipt_voucher = Receiptvoucher()  
        receipt_voucher.setFixedHeight(700)
        layout.addWidget(receipt_voucher)

        title14 = QLabel("Suspense Credit Analysis")
        title14.setAlignment(Qt.AlignmentFlag.AlignCenter)    
        title14.setStyleSheet("QLabel { font-size: 16pt; font-weight: bold; margin: 10px; }")
        layout.addWidget(title14)
        suspense_credit = SuspenseCredit()
        suspense_credit.setFixedHeight(700)
        layout.addWidget(suspense_credit)

        
        # Add spacing between charts
        layout.setSpacing(40)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CombinedFinancialView()
    window.show()
    sys.exit(app.exec())
