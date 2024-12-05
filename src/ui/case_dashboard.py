from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
                             QScrollArea, QDialog,QPushButton,QSplitter,QSizePolicy)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from ..utils.json_logic import *
from functools import partial
from utils.json_logic import delete_name_merge_object
from src.ui.case_dashboard_components.name_manager import SimilarNameGroups

# from .case_dashboard_components.entity import create_entity_distribution_chart
# from .case_dashboard_components.individual_table import create_individual_dashboard_table
# from .case_dashboard_components.link_analysis import LinkAnalysisWidget
# from .case_dashboard_components.bidirectional import BiDirectionalAnalysisWidget
# from .case_dashboard_components.fifo_lifo import FIFO_LFIO_Analysis
# from .case_dashboard_components.name_manager import SimilarNameGroups
# from .case_dashboard_components.account_number_and_name_manager import AccountNumberAndNameManager

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
        self.buttons = {}  # Store buttons for management
        self.section_widgets = {}  # Store section widgets
        self.current_section_label = None  # Store current section label
        self.sidebar_options_disabled = True

         # Lazy loading mapping
        self.lazy_categories = {
            "Name Manager": self.lazy_load_name_manager,
            "Acc No and Name Manager": self.lazy_load_account_manager,
            "Network Graph": self.lazy_load_network_graph,
            "Entites Distribution": self.lazy_load_entity_distribution,
            "Individual Table": self.lazy_load_individual_table,
            "Link Analysis": self.lazy_load_link_analysis,
            "Bi-Directional Analysis": self.lazy_load_bidirectional_analysis,
            "FIFO LIFO": self.lazy_load_fifo_lifo
        }
        
        self.init_ui()

    def lazy_load_network_graph(self):
        from .case_dashboard_components.network import create_network_graph
        return create_network_graph(result=self.case_result)

    def lazy_load_entity_distribution(self):
        from .case_dashboard_components.entity import create_entity_distribution_chart
        return create_entity_distribution_chart(self.case_result)

    def lazy_load_individual_table(self):
        from .case_dashboard_components.individual_table import create_individual_dashboard_table
        return create_individual_dashboard_table(self.case)

    def lazy_load_link_analysis(self):
        from .case_dashboard_components.link_analysis import LinkAnalysisWidget
        return LinkAnalysisWidget(self.case_result, self.case_id)

    def lazy_load_bidirectional_analysis(self):
        from .case_dashboard_components.bidirectional import BiDirectionalAnalysisWidget
        return BiDirectionalAnalysisWidget(self.case_result, self.case_id)

    def lazy_load_fifo_lifo(self):
        from .case_dashboard_components.fifo_lifo import FIFO_LFIO_Analysis
        return FIFO_LFIO_Analysis(self.case_result, self.case_id)

    def lazy_load_name_manager(self):
        from src.ui.case_dashboard_components.name_manager import SimilarNameGroups
        return SimilarNameGroups(self.case_id, self)

    def lazy_load_account_manager(self):
        from src.ui.case_dashboard_components.account_number_and_name_manager import AccountNumberAndNameManager
        return AccountNumberAndNameManager(self.case_id,self.refresh_case_data)
    

    def init_ui(self):
        self.showFullScreen()  # Make window fullscreen

        # Create main widget and layout
        main_widget = QWidget()
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
        splitter.setStretchFactor(0, 1)  # Sidebar gets minimal stretch
        splitter.setStretchFactor(1, 1)  # Content area stretches with the window
        splitter.setSizes([350, 1150])  # Initial sizes
        splitter.setHandleWidth(0)  # Make sidebar non-resizable

            
        main_layout.addWidget(splitter, stretch=1)

        # Set default section to open
        self.showSection("Name Manager", SimilarNameGroups(self.case_id, self))

        self.setLayout(main_layout)
    
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
        
        # self.categories = {
        #     "Network Graph": create_network_graph(self.case_result),
        #     "Entites Distribution": create_entity_distribution_chart(self.case_result),
        #     "Individual Table": create_individual_dashboard_table(self.case),
        #     "Link Analysis": LinkAnalysisWidget(self.case_result,self.case_id),
        #     "Bi-Directional Analysis": BiDirectionalAnalysisWidget(self.case_result,self.case_id),
        #     "FIFO LIFO": FIFO_LFIO_Analysis(self.case_result,self.case_id),
        #     "Name Manager": SimilarNameGroups(self.case_id,self),
        #     "Acc No and Name Manager": AccountNumberAndNameManager(self.case_id),
        # }

        self.categories = {
            category: None for category in self.lazy_categories.keys()
        }
    
        # # Create buttons for each category
        # for category, widget_class in self.categories.items():
        #     # Create button for each category
        #     btn = SidebarButton(category)
        #     btn.clicked.connect(partial(self.showSection, category, widget_class))
        #     self.buttons[category] = btn
        #     sidebar_layout.addWidget(btn)

        # sidebar_layout.addStretch()
        # return sidebar

        for category in self.categories:
            # Create button for each category
            btn = SidebarButton(category)
            if self.sidebar_options_disabled and (category is not "Name Manager" and not "Acc No and Name Manager"):
                btn.setEnabled(False)
                btn.setCheckable(False)
            else:
                btn.clicked.connect(partial(self.showSection, category))
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
        self.content_layout.setContentsMargins(0,0,0,0)
        self.content_layout.setSpacing(30)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self.content_container)
        # scroll.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        
        content_layout.addWidget(scroll,stretch=1)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        
        return content_widget
        
    def create_section_title(self, title):
        label = QLabel(title)
        label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        label.setStyleSheet("color: #2c3e50; margin-top: 30px;")
        return label

    def on_cell_click(self, row, column):
        # Open a new window with the details of the clicked item
        dialog = QDialog(self)
        dialog.setWindowTitle("Entry Details")
        dialog_layout = QVBoxLayout(dialog)
        entry_label = QLabel(f"Details for Entry {row + 1}")
        entry_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        dialog_layout.addWidget(entry_label)

        dialog.setLayout(dialog_layout)
        dialog.exec()

    def showSection(self, section_name, widget_class):
        for btn in self.buttons.values():
            btn.setChecked(False)
        self.buttons[section_name].setChecked(True)

        if section_name == "Acc No and Name Manager":
            self.current_section_label.setText("Account Number and Name Manager")
        else:
            self.current_section_label.setText(section_name)

        # if section_name in self.section_widgets:
        #     widget = self.section_widgets[section_name]
        # else:
        #     widget = widget_class
        #     self.section_widgets[section_name] = widget

        # Lazy load the widget if it doesn't exist
        if section_name not in self.section_widgets:
            # Use the lazy loading function to create the widget
            widget = self.lazy_categories[section_name]()
            self.section_widgets[section_name] = widget

        # Get the widget (either newly created or existing)
        widget = self.section_widgets[section_name]

        if section_name == "Name Manager" or section_name == "Acc No and Name Manager":
            widget.setMinimumHeight(int(self.height()*0.8))
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Clear the content layout
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        self.content_layout.addWidget(widget)
        
        self.content_layout.addStretch()

    def refresh_case_data(self,new_case_data):
        self.case = new_case_data
        self.section_widgets["Network Graph"] = self.lazy_load_network_graph()
        self.section_widgets["Entites Distribution"] = self.lazy_load_bidirectional_analysis()
        self.section_widgets["Individual Table"] = self.lazy_load_individual_table()
        self.section_widgets["Link Analysis"] = self.lazy_load_link_analysis()
        self.section_widgets["Bi-Directional Analysis"] = self.lazy_load_bidirectional_analysis()
        self.section_widgets["FIFO LIFO"] = self.lazy_load_fifo_lifo()
        delete_name_merge_object(self.case_id)
        self.section_widgets["Name Manager"] = self.lazy_load_name_manager()

        # self.section_widgets=self.lazy_categories

     
        
        
