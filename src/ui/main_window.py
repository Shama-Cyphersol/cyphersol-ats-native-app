from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt,QSize
from .dashboard import DashboardTab
from .file_opener import FileOpenerTab
from .report_generator import ReportGeneratorTab
from .cash_flow import CashFlowNetwork
from .settings import SettingsTab
import pandas as pd

dummy_data_for_network_graph = pd.DataFrame([
        {'Value Date': '01-04-2022', 'Description': 'openingbalance', 'Debit': 0.00, 'Credit': 3397.13, 'Balance': 3397.13, 'Category': 'Opening Balance'},
        {'Value Date': '01-04-2022', 'Description': 'mbrentref209108561454', 'Debit': 3000.00, 'Credit': 0.00, 'Balance': 397.13, 'Category': 'Rent Paid'},
        {'Value Date': '01-04-2022', 'Description': 'upi/saisuvidhasho/209125626472/paymentfromph', 'Debit': 140.00, 'Credit': 0.00, 'Balance': 257.13, 'Category': 'UPI-Dr'},
        {'Value Date': '01-04-2022', 'Description': 'mbsenttogane62491633408impsref209121360374', 'Debit': 200.00, 'Credit': 0.00, 'Balance': 57.13, 'Category': 'Creditor'},
        {'Value Date': '01-04-2022', 'Description': 'rev:imps62491633408ref209121360374', 'Debit': 0.00, 'Credit': 200.00, 'Balance': 257.13, 'Category': 'Refund/Reversal'},
        {'Value Date': '03-04-2022', 'Description': 'recd:imps/209310634191/mrsmeena/kkbk/x8247/ineti', 'Debit': 0.00, 'Credit': 3000.00, 'Balance': 3057.13, 'Category': 'Debtor'},
        {'Value Date': '03-04-2022', 'Description': 'upi/kfcsapphirefo/209376260786/ye', 'Debit': 250.00, 'Credit': 0.00, 'Balance': 807.13, 'Category': 'Food Expense/Hotel'},
        {'Value Date': '04-04-2022', 'Description': 'ib:receivedfromruteshslodaya06580010004867', 'Debit': 0.00, 'Credit': 18269.00, 'Balance': 18516.13, 'Category': 'Suspense'},
        {'Value Date': '05-04-2022', 'Description': 'mbloanref209507057778', 'Debit': 6000.00, 'Credit': 0.00, 'Balance': 7316.13, 'Category': 'Loan given'},
        {'Value Date': '07-04-2022', 'Description': 'upi/irctcwebupi/209730050986/oid100003321095', 'Debit': 2568.60, 'Credit': 0.00, 'Balance': 3387.03, 'Category': 'Travelling Expense'},
    ])
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CypherSol")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
                           
            QMainWindow {
                background-color: #f0f0f0;
            }
                           
            QPushButton {
                background-color: #ffffff;
                color: #2c3e50;
                border: none;  
                padding: 12px 20px;
                text-align: left;
                font-size: 16px;
                margin: 2px 10px;
                outline: none;
                border-left: 3px solid transparent;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                color: #3498db;
            }
            QPushButton:checked {
                background-color: #f0f7ff;
                color: #3498db;
                border-left: 3px solid #3498db;
            }
        
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Add footer label
        footer_label = QLabel("© Copyright 2024 CypherSOL Fintech India Pvt Ltd.\nAll Rights Reserved")
        footer_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 11px;
                padding: 20px;
                qproperty-alignment: AlignCenter;
            }
        """)
        footer_label.setWordWrap(True)

        # Sidebar
        sidebar = QWidget()
        sidebar.setStyleSheet("""
            QWidget {
                background-color: white;
            }
        """)
        sidebar.setFixedWidth(300)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setSpacing(0)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)

        # Cyphersol Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/logo.png")
        scaled_pixmap = logo_pixmap.scaled(200, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        logo_label.setPixmap(scaled_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setContentsMargins(0, 10, 0, 45)
        sidebar_layout.addWidget(logo_label)

        # Navigation buttons
        self.nav_buttons = []
        button_icons = [
            ("Dashboard", "dashboard.png"),
            ("Generate Report", "generate_report.png"),
            ("Settings", "settings.png"),
            ("Cash Flow Network", "cash-flow.png"),
        ]

        for text, icon in button_icons:
            btn = QPushButton(" " * 2 +text)
            btn.setIcon(QIcon(f"assets/{icon}"))
            btn.setIconSize(QSize(23, 23))  # Make icons slightly larger
            btn.setCheckable(True)
            btn.setChecked(text == "Dashboard")
            self.nav_buttons.append(btn)
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        sidebar_layout.addWidget(footer_label)

        main_layout.addWidget(sidebar)

        # Content area with updated background
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f8f9fa;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)

        self.content_area = QStackedWidget()
        self.content_area.addWidget(DashboardTab())
        self.content_area.addWidget(ReportGeneratorTab())
        self.content_area.addWidget(SettingsTab())
        self.content_area.addWidget(CashFlowNetwork(data=dummy_data_for_network_graph))

        content_layout.addWidget(self.content_area)
        main_layout.addWidget(content_widget)

        # Connect buttons
        for i, btn in enumerate(self.nav_buttons):
            btn.clicked.connect(lambda checked, index=i: self.switch_page(index))

    def switch_page(self, index):
        self.content_area.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

 