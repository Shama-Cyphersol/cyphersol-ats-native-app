import sys
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPalette, QColor, QFont, QIcon
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QScrollArea, QTabWidget, QPushButton, QSplitter,
    QFrame, QStackedWidget, QSizePolicy
)
from PyQt6.QtCharts import QChart, QChartView
from functools import partial

# Import your existing chart classes
from utils.summary_charts.transactions import BankTransactionDashboard
from utils.summary_charts.Creditors import Creditors
from utils.summary_charts.EOD_balance import EODBalanceChart
from utils.summary_charts.Debtors import DebtorsChart
from utils.summary_charts.Cash_withdrawal import CashWithdrawalChart
from utils.summary_charts.Cash_Deposit import CashDeposit
from utils.summary_charts.Reversal import Reversal
from utils.summary_charts.Suspense_debit import SuspenseDebit
from utils.summary_charts.Suspense_Credit import SuspenseCredit
# from utils.summary_charts.Summary import SummaryWindow
from utils.json_logic import load_result
# from utils.summary_charts.Investment import InvestmentChart
# from utils.summary_charts.EMI import EMITransactionChart

class SidebarButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(40)
        self.setStyleSheet("""
            QPushButton {
                border: none;
                text-align: left;
                padding: 8px 15px;
                border-radius: 5px;
                margin: 2px 10px;
            }
            QPushButton:checked {
                background-color: #e0e7ff;
                color: #4338ca;
            }
            QPushButton:hover:!checked {
                background-color: #f3f4f6;
            }
        """)

class IndividualDashboard(QMainWindow):
    def __init__(self, case_id, name,row_id):
        super().__init__()
        self.case_id = case_id
        self.name = name
        result = load_result(case_id)
        self.single_df = result["single_df"]
        self.buttons = {}  # Store buttons for management
        self.section_widgets = {}  # Store section widgets
        self.current_section_label = None  # Store current section label
        self.row_id = row_id
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(f"Financial Dashboard - {self.name}")
        self.showFullScreen()  # Make window fullscreen
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create sidebar
        sidebar = self.createSidebar()
        
        # Create content area
        content_area = self.createContentArea()
        
        # Add splitter for resizable sidebar
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(sidebar)
        splitter.addWidget(content_area)
        splitter.setStretchFactor(splitter.indexOf(content_area), 1)
        splitter.setStretchFactor(0, 0)  # Sidebar gets minimal stretch
        splitter.setStretchFactor(1, 1)  # Content area stretches with the window
        splitter.setSizes([250, 1150])  # Initial sizes
            
        main_layout.addWidget(splitter,stretch=1)

        # Set default section to open
        self.showSection("Summary", SummaryWindow)
    
    def create_id(self):
        id = chr(ord('A') + self.row_id)
        id+=str(self.row_id)
        print("ID - ",id)
        return id
    
    def createSidebar(self):
        sidebar = QWidget()
        sidebar.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)  # Prevents sidebar from expanding unnecessarily
        sidebar.setMaximumWidth(300)
        sidebar.setMinimumWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(5)
        
        # Header
        header = QWidget()
        header.setStyleSheet("background-color: #f8fafc;")
        header_layout = QVBoxLayout(header)
        
        title = QLabel("Financial Dashboard")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e293b;")
        subtitle = QLabel(f"Name: {self.name}")
        subtitle.setStyleSheet("color: #64748b;padding:4px 0;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        sidebar_layout.addWidget(header)
        
        # Navigation buttons with their corresponding widget classes
        # self.categories = {
        #     "Summary": {
        #         "Particulars": SummaryParticular,
        #         "Income": SummaryIncome,
        #         "Important Expenses": SummaryImportantExpenses,
        #         "Other Expenses": SummaryOtherExpenses,
        #         "Eod Balance":  EODBalanceChart,
        #     },
        #     "Transactions": {
        #         "Transactions Details": BankTransactionDashboard,
        #         "Creditors": Creditors,
        #         "Debtors": DebtorsChart,
        #         "Cash Withdrawal": CashWithdrawalChart,
        #         "Cash Deposit": CashDeposit,
        #     },
        #     "Other": {
        #         "Suspense Debit": SuspenseDebit, #Show Suspense Debit Percentage chart also
        #         "Suspense Credit": SuspenseCredit, #Show Suspense Credit Percentage chart also
        #         "Reversal": Reversal
        #     }
        # }
        self.categories = {
            "Summary": SummaryWindow,
            "Transactions": BankTransactionDashboard,
            "EOD Balance": EODBalanceChart,
            "Creditors": Creditors,
            "Debtors": DebtorsChart,
            "Cash Withdrawal": CashWithdrawalChart,
            "Cash Deposit": CashDeposit,
            "Suspense Debit": SuspenseDebit,
            "Suspense Credit": SuspenseCredit,
            "Reversal": Reversal,
            "Investment": InvestmentChart,
            "EMI": EMITransactionChart
        }
        # # Create buttons for each category
        # for category, items in self.categories:
        #     cat_label = QLabel(category)
        #     cat_label.setStyleSheet("""
        #         font-weight: bold;
        #         color: #64748b;
        #         padding: 15px 15px 5px 15px;
        #     """)
        #     sidebar_layout.addWidget(cat_label)
            
        #     # Create buttons for items in this category
        #     for item_name, widget_class in items.items():
        #         btn = SidebarButton(item_name)
        #         btn.clicked.connect(partial(self.showSection, item_name, widget_class))
        #         self.buttons[item_name] = btn
        #         sidebar_layout.addWidget(btn)
        
        # sidebar_layout.addStretch()
        # return sidebar
    # Create buttons for each category
        for category, widget_class in self.categories.items():
            # Create button for each category
            btn = SidebarButton(category)
            btn.clicked.connect(partial(self.showSection, category, widget_class))
            self.buttons[category] = btn
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        return sidebar
   
    def createContentArea(self):
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Header bar
        header = QWidget()
        header.setStyleSheet("background-color: white; border-bottom: 1px solid #e2e8f0;")
        header_layout = QHBoxLayout(header)
        
        self.current_section_label = QLabel("Bank Transactions")
        self.current_section_label.setStyleSheet("font-size: 24px; font-weight: bold; color:#1e293b;opacity:0.8;padding: 5px 0;")
        self.current_section_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center align the text
        header_layout.addWidget(self.current_section_label)
        
        content_layout.addWidget(header)
        
        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f8fafc;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #f1f5f9;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #cbd5e1;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #94a3b8;
            }
        """)
        
        # # Content container
        # self.content_stack = QStackedWidget()
        # scroll.setWidget(self.content_stack)
        
        # # Wrap scroll area in a layout to maintain padding and spacing
        # scroll_layout = QVBoxLayout()

        # scroll_layout.setContentsMargins(0, 0, 0, 100)
        # scroll_layout.addWidget(scroll)
        # content_layout.addLayout(scroll_layout)
        
        # return content_widget
        # Create a widget to hold all the content
        self.content_container = QWidget()
        # make content_container take all the height available

        self.content_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(20)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self.content_container)
        content_layout.addWidget(scroll,stretch=1)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        
        return content_widget
        
    def showSection(self, section_name, widget_class):
        # Uncheck all buttons except the clicked one
        for btn in self.buttons.values():
            btn.setChecked(False)
        self.buttons[section_name].setChecked(True)

        # Update the section label
        self.current_section_label.setText(section_name)

        # Clear previous content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Create new widget based on the selected section
        if widget_class == SummaryWindow:
            widget = widget_class(data=self.single_df[self.create_id()]["data"]["summary_df_list"])
        elif widget_class == BankTransactionDashboard:
            widget = widget_class(data=self.single_df[self.create_id()]["data"]["transaction_sheet_df"])
        elif widget_class == EODBalanceChart:
            widget = widget_class(data=self.single_df[self.create_id()]["data"]["eod_sheet_df"])
        elif widget_class == Creditors:
            widget = widget_class(data=self.single_df[self.create_id()]["data"]["creditor_df"])
        elif widget_class == DebtorsChart:
            widget = widget_class(data=self.single_df[self.create_id()]["data"]["debtor_df"])
        elif widget_class == CashWithdrawalChart:
            widget = widget_class(data=self.single_df[self.create_id()]["data"]["cash_withdrawal_df"])
        elif widget_class == CashDeposit:
            widget = widget_class(data=self.single_df[self.create_id()]["data"]["cash_deposit_df"])
        elif widget_class == SuspenseDebit:
            widget = widget_class(data=self.single_df[self.create_id()]["data"]["suspense_debit_df"], total_transactions=self.single_df[self.create_id()]["data"]["transaction_sheet_df"].shape[0])
        elif widget_class == SuspenseCredit:
            widget = widget_class(data=self.single_df[self.create_id()]["data"]["suspense_credit_df"], total_transactions=self.single_df[self.create_id()]["data"]["transaction_sheet_df"].shape[0])
        elif widget_class == Reversal:
            widget = widget_class(data=self.single_df[self.create_id()]["data"]["refund"])
        elif widget_class == InvestmentChart:
            widget = widget_class(data=self.single_df[self.create_id()]["data"]["investment_df"])
        elif widget_class == EMITransactionChart:
            widget = widget_class(data=self.single_df[self.create_id()]["data"]["emi_df"])
        else:
            widget = widget_class()

        # Set expanding size policy to adjust according to content
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        # Add the widget to the content layout
        self.content_layout.addWidget(widget)
        
        # Add stretch at the bottom to push content to the top and allow scroll if necessary
        self.content_layout.addStretch()