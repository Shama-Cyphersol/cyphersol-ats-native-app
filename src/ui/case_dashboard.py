from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
                             QScrollArea, QDialog,QPushButton,QSplitter,QSizePolicy)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from utils.json_logic import *
from functools import partial
from .case_dashboard_components.network import create_network_graph
from .case_dashboard_components.entity import create_entity_distribution_chart
from .case_dashboard_components.individual_table import create_individual_dashboard_table
from .case_dashboard_components.link_analysis import LinkAnalysisWidget
from .case_dashboard_components.bidirectional import create_bidirectional_analysis
from .case_dashboard_components.fifo_lifo import create_fifo_lifo_analysis

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


class CaseDashboard(QWidget):
    def __init__(self,case_id):
        super().__init__()
        self.case_id = case_id
        self.case = load_case_data(case_id)
        self.case_result = load_result(self.case_id)
        self.buttons = {}  # Store buttons for management
        self.section_widgets = {}  # Store section widgets
        self.current_section_label = None  # Store current section label

        self.init_ui()

    def init_ui(self):
        self.showFullScreen()  # Make window fullscreen

         # Create main widget and layout
        main_widget = QWidget()
        # self.setCentralWidget(main_widget)
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
        self.showSection("Fund Flow Network Graph", create_network_graph(result=self.case_result))

        self.setLayout(main_layout)
    
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
        
        title = QLabel("Case Dashboard")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e293b;")
        subtitle = QLabel(f"Case ID: {self.case_id}")
        subtitle.setStyleSheet("color: #64748b;padding:4px 0;")
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        sidebar_layout.addWidget(header)
        
       
        self.categories = {
            "Fund Flow Network Graph": create_network_graph(self.case_result),
            "Entites Distribution": create_entity_distribution_chart(self.case_result),
            "Individual Table": create_individual_dashboard_table(self.case),
            # "Link Analysis": create_link_analysis(self.case_result),
            "Link Analysis": LinkAnalysisWidget(self.case_result),
            "Bi-Directional Analysis": create_bidirectional_analysis(self.case_result),
            "FIFO LIFO": create_fifo_lifo_analysis(self.case_result),
        }
    
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
        
    def create_section_title(self, title):
        label = QLabel(title)
        label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        label.setStyleSheet("color: #2c3e50; margin-top: 20px;")
        return label

    def on_cell_click(self, row, column):
        # Open a new window with the details of the clicked item
        dialog = QDialog(self)
        dialog.setWindowTitle("Entry Details")
        dialog_layout = QVBoxLayout(dialog)
        entry_label = QLabel(f"Details for Entry {row + 1}")
        entry_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        dialog_layout.addWidget(entry_label)

        dialog.setLayout(dialog_layout)
        dialog.exec()

    def showSection(self, section_name, widget_class):
        # Uncheck all buttons except the clicked one
        for btn in self.buttons.values():
            btn.setChecked(False)
        self.buttons[section_name].setChecked(True)

        # Update the section label
        self.current_section_label.setText(section_name)

        # # Clear previous content
        # while self.content_layout.count():
        #     item = self.content_layout.takeAt(0)
        #     print("Item ",section_name," - ", item)
        #     print("Item widget ",section_name," - ", item.widget())
        #     if item.widget():
        #         item.widget().deleteLater()

        # Check if the widget for this section already exists
        if section_name in self.section_widgets:
            widget = self.section_widgets[section_name]
        else:
            widget = widget_class
            self.section_widgets[section_name] = widget

        # Set expanding size policy to adjust according to content
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        # Clear the content layout
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        # Add the widget to the content layout
        self.content_layout.addWidget(widget)
        
        # Add stretch at the bottom to push content to the top and allow scroll if necessary
        self.content_layout.addStretch()