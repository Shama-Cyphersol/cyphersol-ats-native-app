import traceback
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
                             QScrollArea, QDialog,QPushButton,QMessageBox,QSplitter,QSizePolicy, QLabel, QMessageBox)

from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt,QEvent
from utils.json_logic import *
from functools import partial
from .case_dashboard_components.individual_table import create_individual_dashboard_table,IndividualDashboardTable
from .case_dashboard_components.CashFlowNetwork import CashFlowNetwork
from .case_dashboard_components.entity import EntityDistributionChart
from .case_dashboard_components.link_analysis import LinkAnalysisWidget
from .case_dashboard_components.bidirectional import BiDirectionalAnalysisWidget
from .case_dashboard_components.fifo_lifo import FIFO_LFIO_Analysis
from .case_dashboard_components.name_manager import SimilarNameGroups
from .case_dashboard_components.account_number_and_name_manager import AccountNumberAndNameManager
from .case_dashboard_components.fund_tracking import FundTrackingComponent


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
        self._widget_refs = {}

        self.current_section_label = None  # Store current section label
        self.disabled_buttons = []
        # self.sidebar_options_disabled = True
        similar_names_groups = find_merge_name_object(self.case_id)
        if similar_names_groups==None or similar_names_groups["final_merged_status"] == False:
                self.disabled_buttons = ["Link Analysis", "Bi-Directional Analysis", "FIFO LIFO","Fund Tracking","Entites Distribution","Network Graph"]

         # Lazy loading mapping
        self.lazy_categories = {
            "Name Manager": self.lazy_load_name_manager,
            "Acc No and Name Manager": self.lazy_load_account_manager,
            # "Network Graph": create_network_graph(self.case_result),
            "Network Graph": self.lazy_load_network_graph,
            "Entites Distribution": self.lazy_load_entity_distribution,
            "Individual Table": self.lazy_load_individual_table,
            "Link Analysis": self.lazy_load_link_analysis,
            "Bi-Directional Analysis": self.lazy_load_bidirectional_analysis,
            "FIFO LIFO": self.lazy_load_fifo_lifo,
            "Fund Tracking": self.lazy_load_fund_tracking
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
                return QLabel("No entities found for network graph.")
        
        except Exception as e:
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
        self.showSection("Name Manager", SimilarNameGroups(case_id=self.case_id,parent= self,refresh_case_dashboard=self.refresh_case_dashboard))

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

            if category in self.disabled_buttons:
                btn.setDisabled(True)
                btn.installEventFilter(self)

            # else:
            btn.clicked.connect(partial(self.showSection, category))
            self.buttons[category] = btn
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()
        return sidebar
    
    def eventFilter(self, obj, event):
        # Check if the object is a disabled button and the event is a mouse press
        if (isinstance(obj, SidebarButton) and obj.isEnabled() == False and 
            event.type() == QEvent.Type.MouseButtonPress):
            
            msg_box = QMessageBox(self)
            msg_box.setStyleSheet("""
                QMessageBox QLabel {
                    color: black;
                }
            """)
            msg_box.setWindowTitle("Warning")
            msg_box.setText("Please Merge Similar Names first from Name Manager Tab in order to get accurate Analysis.")
            msg_box.setIcon(QMessageBox.Icon.Warning)

            # Create custom buttons with specific text
            btn_styles = """
                QPushButton {
                    border-radius: 5px;
                    padding: 6px 10px;
                    font-weight: 400;
                    border: 1px solid #999999;
                }
                QPushButton:hover {
                }
            """
            merge_now_button = QPushButton("Merge Names Now")
            merge_now_button.setStyleSheet(btn_styles+"""
            QPushButton {
                    background-color: #3498db;
                    color: white;
                }            
            """)
            merge_later_button = QPushButton("Merge Names Later")
            merge_later_button.setStyleSheet(btn_styles+"""
            QPushButton {
                    background-color: #c0392b;
                    color: white;
                }            
            """)

            # Add the custom buttons to the message box
            msg_box.addButton(merge_now_button, QMessageBox.ButtonRole.AcceptRole)
            msg_box.addButton(merge_later_button, QMessageBox.ButtonRole.RejectRole)
            msg_box.setDefaultButton(merge_now_button)  # Set default button
            msg_box.setEscapeButton(merge_now_button)  # Set escape button
            

            reply = msg_box.exec()
            clicked_button = msg_box.clickedButton()

            # Check which button was clicked
            if clicked_button  == merge_now_button:
                # Redirect to Name Manager tab
                self.showSection("Name Manager", SimilarNameGroups(case_id=self.case_id,parent= self,refresh_case_dashboard=self.refresh_case_dashboard))

            elif clicked_button  == merge_later_button:
                # Enable all previously disabled buttons
               self.enable_disabled_options()
               
            # Return True to indicate the event has been handled
            return True
        
        # Let the default event handling continue for other events
        return super().eventFilter(obj, event)

    def enable_disabled_options(self):
        for category in self.disabled_buttons:
            if category in self.buttons:
                self.buttons[category].setEnabled(True) 
                self.buttons[category].removeEventFilter(self)
        self.disabled_buttons = []  # Clear the list after enabling

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
        try:
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
            # if section_name not in self.section_widgets :
            #     # Use the lazy loading function to create the widget
            #     widget = self.lazy_categories[section_name]()
            #     self._widget_refs[section_name] = widget
            #     self.section_widgets[section_name] = widget

            # # Get the widget (either newly created or existing)
            # widget = self.section_widgets[section_name] 
            if section_name in self.section_widgets:
                widget = self.section_widgets[section_name]
            else:
                widget = self.lazy_categories[section_name]()
                self.section_widgets[section_name] = widget
            
            # Set minimum height for specific sections
            if section_name in ["Name Manager", "Acc No and Name Manager"]:
                widget.setMinimumHeight(int(self.height()*0.8))
            
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            
            # Clear the content layout
            while self.content_layout.count():
                item = self.content_layout.takeAt(0)
                if item.widget():
                    item.widget().setParent(None)
                
            self.content_layout.addWidget(widget)
            
            self.content_layout.addStretch()

        except Exception as e:
                print(f"Error in showSection: {e}")
                print(traceback.format_exc())

                # Fallback error handling
                error_label = QLabel(f"Error loading section: {str(e)}")
                
                # Show error message box
                error_box = QMessageBox()
                error_box.setIcon(QMessageBox.Icon.Critical)
                error_box.setText("Error Loading Section")
                error_box.setInformativeText(str(e))
                error_box.setWindowTitle("Section Loading Error")
                error_box.exec()
        
                
    # def refresh_case_dashboard(self,source,new_case_data=None):
        # refresh this page
        # if source == "SimilarNameGroups":
        #     self.enable_disabled_options()

        # self.section_widgets["Name Manager"] = self.lazy_load_name_manager()
        # self.section_widgets["Acc No and Name Manager"] = self.lazy_load_account_manager()
        # self.section_widgets["Network Graph"] = self.lazy_load_network_graph()
        # self.section_widgets["Entites Distribution"] = self.lazy_load_entity_distribution()
        # self.section_widgets["Individual Table"] = self.lazy_load_individual_table()
        # self.section_widgets["Link Analysis"] = self.lazy_load_link_analysis()
        # self.section_widgets["Bi-Directional Analysis"] = self.lazy_load_bidirectional_analysis()
        # self.section_widgets["FIFO LIFO"] = self.lazy_load_fifo_lifo()
        # if source == "AccountNumberAndNameManager":
        #     self.case = new_case_data
        #     delete_name_merge_object(self.case_id)

        # self.section_widgets=self.lazy_categories

    def refresh_case_dashboard(self, source, new_case_data=None):
        print("=" * 50)
        print(f"Refreshing Case Dashboard - Source: {source}")
        print("=" * 50)

        try:
            # Log the initial state
            print("Initial Section Widgets:", list(self.section_widgets.keys()))
            print("Initial Categories:", list(self.categories.keys()))
            print("Initial Disabled Buttons:", self.disabled_buttons)

            # If changes were made in Account Number and Name Manager
            if source == "AccountNumberAndNameManager":
                # Log data update
                print("Updating Case Data...")
                
                # Update the case data if a new case data is provided
                if new_case_data is not None:
                    self.case = new_case_data
                    print("New case data loaded")
                
                # Clear existing section widgets
                print("Clearing section widgets...")
                self.section_widgets.clear()
                
                # Reset lazy loading categories
                print("Resetting categories...")
                self.categories = {
                    category: None for category in self.lazy_categories.keys()
                }
                
                # Reload disabled buttons based on name merging status
                print("Checking name merging status...")
                similar_names_groups = find_merge_name_object(self.case_id)
                if similar_names_groups is None or similar_names_groups["final_merged_status"] == False:
                    self.disabled_buttons = ["Link Analysis", "Bi-Directional Analysis", "FIFO LIFO", "Fund Tracking", "Entites Distribution", "Network Graph"]
                    
                    print("Disabling buttons:", self.disabled_buttons)
                    # Disable corresponding buttons
                    for category in self.disabled_buttons:
                        if category in self.buttons:
                            self.buttons[category].setDisabled(True)
                            self.buttons[category].installEventFilter(self)
                else:
                    # If names are merged, enable all buttons
                    print("Enabling all buttons...")
                    self.enable_disabled_options()
                
                # Reload the current section (or default to Name Manager)
                current_section = self.current_section_label.text()
                
                if current_section == "Acc No and Name Manager":
                    current_section = "Account Number and Name Manager"
                
                print(f"Reloading section: {current_section}")
                # Find the corresponding widget and reload
                for section, widget in self.lazy_categories.items():
                    if section.replace(" ", "") == current_section.replace(" ", ""):
                        self.showSection(section, widget)
                        break
                    
                    # Log final state
                    print("\n" + "=" * 50)
                    print("Refresh Complete")
                    print("Final Section Widgets:", list(self.section_widgets.keys()))
                    print("Final Categories:", list(self.categories.keys()))
                    print("Final Disabled Buttons:", self.disabled_buttons)
                    print("=" * 50)

        except Exception as e:
            print(f"Error during dashboard refresh: {e}")
            import traceback
            traceback.print_exc()
        
        
        