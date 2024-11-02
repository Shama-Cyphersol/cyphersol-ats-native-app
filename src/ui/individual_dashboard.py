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
from utils.summary_charts.Summary_income import SummaryIncome
from utils.summary_charts.Summary_particular import SummaryParticular
from utils.summary_charts.Summary_otherExpenses import SummaryOtherExpenses
from utils.summary_charts.Summary_important_expenses import SummaryImportantExpenses
from utils.summary_charts.transactions import BankTransactionDashboard
from utils.summary_charts.Creditors import Creditors
from utils.summary_charts.EOD_balance import EODBalanceChart
from utils.summary_charts.Debtors import DebtorsChart
from utils.summary_charts.Cash_withdrawal import CashWithdrawalChart
from utils.summary_charts.Cash_Deposit import CashDeposit
from utils.summary_charts.Summary_important_expenses import SummaryImportantExpenses
from utils.summary_charts.Summary_otherExpenses import SummaryOtherExpenses
from utils.summary_charts.Summary_income import SummaryIncome
from utils.summary_charts.Reversal import Reversal
from utils.summary_charts.Suspense_debit import SuspenseDebit
from utils.summary_charts.Suspense_Credit import SuspenseCredit
from utils.json_logic import load_result

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
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([250, 1150])  # Initial sizes
        
        main_layout.addWidget(splitter)

        # Set default section to open
        self.showSection("Particulars", SummaryParticular)
    
    def create_id(self):
        id = chr(ord('A') + self.row_id)
        id+=str(self.row_id)
        print("ID - ",id)
        return id
    
    def createSidebar(self):
        sidebar = QWidget()
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
        subtitle = QLabel(f"Case ID: {self.case_id}")
        subtitle.setStyleSheet("color: #64748b;padding:4px 0;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        sidebar_layout.addWidget(header)
        
        # Navigation buttons with their corresponding widget classes
        self.categories = {
            "Summary": {
                "Particulars": SummaryParticular,
                "Income": SummaryIncome,
                "Important Expenses": SummaryImportantExpenses,
                "Other Expenses": SummaryOtherExpenses,
                "Eod Balance":  EODBalanceChart,
            },
            "Transactions": {
                # "Transactions Summary": BankTransactionDashboard(data=self.single_df[self.create_id()]["data"]["transaction_sheet_df"]),
                "Transactions Details": BankTransactionDashboard,
                "Creditors": Creditors,
                "Debtors": DebtorsChart,
                "Cash Withdrawal": CashWithdrawalChart,
                "Cash Deposit": CashDeposit,
            },
            "Other": {
                "Suspense Debit": SuspenseDebit, #Show Suspense Debit Percentage chart also
                "Suspense Credit": SuspenseCredit, #Show Suspense Credit Percentage chart also
                "Reversal": Reversal
            }
        }
        
        # Create buttons for each category
        for category, items in self.categories.items():
            cat_label = QLabel(category)
            cat_label.setStyleSheet("""
                font-weight: bold;
                color: #64748b;
                padding: 15px 15px 5px 15px;
            """)
            sidebar_layout.addWidget(cat_label)
            
            # Create buttons for items in this category
            for item_name, widget_class in items.items():
                btn = SidebarButton(item_name)
                btn.clicked.connect(partial(self.showSection, item_name, widget_class))
                self.buttons[item_name] = btn
                sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        return sidebar
   
   
    def createContentArea(self):
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
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
        
        # Content container
        self.content_stack = QStackedWidget()
        scroll.setWidget(self.content_stack)
        
        # Wrap scroll area in a layout to maintain padding and spacing
        scroll_layout = QVBoxLayout()

        scroll_layout.setContentsMargins(0, 0, 0, 100)
        scroll_layout.addWidget(scroll)
        content_layout.addLayout(scroll_layout)
        
        return content_widget
    
    def showSection(self, section_name, widget_class):
        # Uncheck all buttons except the clicked one
        for btn in self.buttons.values():
            btn.setChecked(False)
        self.buttons[section_name].setChecked(True)

        
        # Update the section label
        self.current_section_label.setText(section_name)
        
        # Create or show the widget
        if section_name not in self.section_widgets:
            # Create new widget instance and container
            widget = widget_class()
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Set minimum height for the widget
            widget.setMinimumHeight(600)
            layout.addWidget(widget)
            
            # Store the container
            self.section_widgets[section_name] = container
            self.content_stack.addWidget(container)
        
        # Show the widget
        self.content_stack.setCurrentWidget(self.section_widgets[section_name])