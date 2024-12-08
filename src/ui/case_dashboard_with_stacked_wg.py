from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
                             QScrollArea, QDialog,QPushButton,QMessageBox,QSplitter,QSizePolicy, QStackedWidget)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QEvent
from ..utils.json_logic import *
from functools import partial
from ..utils.json_logic import delete_name_merge_object
from .case_dashboard_components.individual_table import IndividualDashboardTable
from .case_dashboard_components.link_analysis import LinkAnalysisWidget
from .case_dashboard_components.bidirectional import BiDirectionalAnalysisWidget
from .case_dashboard_components.fifo_lifo import FIFO_LFIO_Analysis
from .case_dashboard_components.name_manager import SimilarNameGroups
from .case_dashboard_components.account_number_and_name_manager import AccountNumberAndNameManager
from .case_dashboard_components.fund_tracking import FundTrackingComponent
from .case_dashboard_components.entity import EntityDistributionChart
from .case_dashboard_components.CashFlowNetwork import CashFlowNetwork
from .case_dashboard_components.individual_table import create_individual_dashboard_table,IndividualDashboardTable
from .case_dashboard_components.link_analysis import LinkAnalysisWidget
from .case_dashboard_components.bidirectional import BiDirectionalAnalysisWidget
from src.ui.case_dashboard_components.name_manager import SimilarNameGroups
from .case_dashboard_components.fifo_lifo import FIFO_LFIO_Analysis


class SidebarButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(50)
        self.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #252525;
                font-weight: 400;
                border: none;  
                padding: 12px 20px;
                text-align: left;
                font-size: 18px;
                margin: 2px 10px;
                outline: none;
                border-left: 3px solid transparent;
                border-radius: 5px;
     
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                color: #3498db;

            }
            QPushButton:checked {
                background-color: #e0e7ff;
                color: #3498db;
                border-left: 3px solid #3498db;
            }
            QPushButton:disabled {
                color: #aaaaaa;
                background-color: #f0f0f0;
                border-left: 3px solid transparent;
            }
        """)
        

class CaseDashboard(QWidget):
    def __init__(self, case_id):
        super().__init__()
        self.case_id = case_id
        self.case = load_case_data(case_id)
        self.case_result = load_result(self.case_id)
        self.buttons = {}
        self.section_widgets = {}
        self._widget_refs = {}
        self.categories = {}

        self.current_section_label = None
        self.disabled_buttons = []

         # Lazy loading mapping
        self.lazy_categories = {
            "Name Manager": self.lazy_load_name_manager,
            "Acc No and Name Manager": self.lazy_load_account_manager,
            # "Network Graph": create_network_graph(self.case_result),
            # "Network Graph": self.lazy_load_network_graph,
            # "Entites Distribution": self.lazy_load_entity_distribution,
            "Individual Table": self.lazy_load_individual_table,
            # "Link Analysis": self.lazy_load_link_analysis,
            # "Bi-Directional Analysis": self.lazy_load_bidirectional_analysis,
            # "FIFO LIFO": self.lazy_load_fifo_lifo,
            # "Fund Tracking": self.lazy_load_fund_tracking
        }
        
        self.init_ui()


    def lazy_load_network_graph(self):
        try:
            process_df = self.case_result["cummalative_df"]["process_df"]
            # More robust filtering
            filtered_df = process_df[['Name', 'Value Date', 'Debit', 'Credit', 'Entity']]
            filtered_df = filtered_df[filtered_df['Entity'].notna() & (filtered_df['Entity'] != '')]
            
            # Check if filtered DataFrame is not empty before creating CashFlowNetwork
            if not filtered_df.empty:
                return CashFlowNetwork(filtered_df)
            else:
                # Return a message or a placeholder widget
                from PyQt6.QtWidgets import QLabel
                return QLabel("No entities found for network graph.")
        
        except Exception as e:
            from PyQt6.QtWidgets import QLabel
            print(f"Error in network graph: {e}")
            return QLabel(f"Error loading network graph: {str(e)}")

    def lazy_load_entity_distribution(self):
        
        try:
            entity_df = self.case_result["cummalative_df"]["entity_df"]
            
            # More robust filtering
            entity_df = entity_df[entity_df['Entity'].notna() & (entity_df['Entity'] != '')]
            entity_df = entity_df[entity_df.iloc[:, 0] != ""]
            
            # Check if DataFrame is not empty before processing
            if not entity_df.empty:
                # Take top 10 entities by frequency
                entity_df_10 = entity_df.nlargest(10, entity_df.columns[1]) if len(entity_df) > 10 else entity_df

                all_transactions = self.case_result["cummalative_df"]["process_df"]
                all_transactions = all_transactions[all_transactions['Entity'].notna() & (all_transactions['Entity'] != '')]

                return EntityDistributionChart(data={
                    "piechart_data": entity_df_10,
                    "table_data": entity_df,
                    "all_transactions": all_transactions
                })
            else:
                # Return a message or a placeholder widget
                return QLabel("No entities found for distribution chart.")
        
        except Exception as e:
            print(f"Error in entity distribution: {e}")
            return QLabel(f"Error loading entity distribution: {str(e)}")

    def lazy_load_individual_table(self):
        data = []
        for i in range(len(self.case["individual_names"]["Name"])):
            data.append({
                "Name": self.case["individual_names"]["Name"][i],
                "Account Number": self.case["individual_names"]["Acc Number"][i],
                "Pdf Path": self.case["file_names"][i],
                "row_id": i
            })
        
        return IndividualDashboardTable(data,self.case_id)

    def lazy_load_link_analysis(self):
        return LinkAnalysisWidget(self.case_result, self.case_id)

    def lazy_load_bidirectional_analysis(self):
        return BiDirectionalAnalysisWidget(self.case_result, self.case_id)

    def lazy_load_fifo_lifo(self):
        return FIFO_LFIO_Analysis(self.case_result, self.case_id)

    def lazy_load_name_manager(self):
        return SimilarNameGroups(case_id=self.case_id,parent= self,refresh_case_dashboard=self.refresh_case_dashboard)

    def lazy_load_account_manager(self):
        return AccountNumberAndNameManager(self.case_id,self.refresh_case_dashboard)
    
    def lazy_load_fund_tracking(self):
        return FundTrackingComponent(self.case_id,self.case_result["cummalative_df"]["process_df"])

        

    def init_ui(self):
        self.showFullScreen()  # Make window fullscreen

        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        sidebar = self.createSidebar()

        self.content_area = self.createContentArea()

        # Add splitter for resizable sidebar
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(sidebar)
        splitter.addWidget(self.content_area)
        splitter.setStretchFactor(splitter.indexOf(self.content_area), 1)
        splitter.setStretchFactor(0, 1)  # Sidebar gets minimal stretch
        splitter.setStretchFactor(1, 1)  # Content area stretches with the window
        splitter.setSizes([350, 1150])  # Initial sizes
        splitter.setHandleWidth(0)  # Make sidebar non-resizable

            
        main_layout.addWidget(splitter, stretch=1)

        self.setLayout(main_layout)

        self.showSection("Name Manager")
    
    def createSidebar(self):
        sidebar = QWidget()
        sidebar.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)  # Prevents sidebar from expanding unnecessarily
        sidebar.setMaximumWidth(300)
        sidebar.setMinimumWidth(200)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)  # Add some padding to the sidebar
        sidebar_layout.setSpacing(5)
        
        # Sidebar background and border style
        sidebar.setStyleSheet("""
            background-color: white;  
        """)
        
        # Header
        header = QWidget()
        header.setStyleSheet("background-color: #f8fafc;")
        header_layout = QVBoxLayout(header)

        title = QLabel("Case Dashboard")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e293b;")
        subtitle = QLabel(f"Case ID: {self.case_id}")
        subtitle.setStyleSheet("color: #64748b; padding: 4px 0; ")

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)

        sidebar_layout.addWidget(header)

        # Add significant padding between the header and the categories
        sidebar_layout.addSpacing(20)  # Adjust the value (e.g., 20 pixels) as needed


        self.categories = {
            category: None for category in self.lazy_categories.keys()
        }


        self.buttons = {}  # Store buttons for future reference
        for category in self.categories:
            btn = SidebarButton(category)
            btn.clicked.connect(partial(self.showSection, category))  # Connect to showSection
            self.buttons[category] = btn
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        return sidebar
    

    def createContentArea(self):
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)  # Add some padding to the content area

        # Header bar
        header = QWidget()
        header.setStyleSheet("background-color: white; border-bottom: 1px solid #e2e8f0;")
        header_layout = QHBoxLayout(header)
        
        self.current_section_label = QLabel("Bank Transactions")
        self.current_section_label.setStyleSheet("font-size: 20px; font-weight: bold; color:#1e293b;opacity:0.8;padding:14px 0;")
        self.current_section_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center align the text
        header_layout.addWidget(self.current_section_label)
        content_layout.addWidget(header)
      
        # Create the QStackedWidget
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #f8fafc;")

        # Content container (to hold the stacked widget)
        self.content_container = QWidget()
        self.content_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(30)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Add stacked widget to content container
        self.content_layout.addWidget(self.stacked_widget)

        # Create scroll area to make the content scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.content_container)
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

        # Set the scroll area to allow scrolling if the content exceeds the viewport
        content_layout.addWidget(scroll, stretch=1)

        # Set the scroll to allow vertical scrolling if needed
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        return content_widget


    def contentForCategory(self, category):
        """
        Create the content widget dynamically based on the category name.
        This function will handle the different content creation logic for each category.
        """
        category_to_widget_map = {
            "Bank Transactions": lambda: SimilarNameGroups(case_id=self.case_id,parent= self,refresh_case_dashboard=self.refresh_case_dashboard),
            "Reports": lambda: AccountNumberAndNameManager(self.case_id, self.refresh_case_dashboard),
            "Summary": lambda: IndividualDashboardTable(self.case_result, self.case_id),
        }
        return category_to_widget_map[category]()


    def getSectionIndex(self, section_name):
        """
        Get the index of the section widget in the QStackedWidget.
        """
        return list(self.section_widgets.keys()).index(section_name)
    
    
    def showSection(self, section_name):
        """
        Show the section dynamically, creating content the first time it's accessed.
        """
        try:
            if section_name not in self.section_widgets:
                # Dynamically create and add the section widget based on the category
                content_widget = self.lazy_categories[section_name]()
                self.stacked_widget.addWidget(content_widget)
                self.section_widgets[section_name] = content_widget

            # Get the index for the section and set it as the current index in QStackedWidget
            index = self.getSectionIndex(section_name)
            self.stacked_widget.setCurrentIndex(index)


        except Exception as e:
                import traceback
                print(f"Error in showSection: {e}")
                print(traceback.format_exc())

                # Fallback error handling
                from PyQt6.QtWidgets import QLabel, QMessageBox
                error_label = QLabel(f"Error loading section: {str(e)}")
                
                # Show error message box
                error_box = QMessageBox()
                error_box.setIcon(QMessageBox.Icon.Critical)
                error_box.setText("Error Loading Section")
                error_box.setInformativeText(str(e))
                error_box.setWindowTitle("Section Loading Error")
                error_box.exec()

        
    def refresh_case_dashboard(self):
        pass
    