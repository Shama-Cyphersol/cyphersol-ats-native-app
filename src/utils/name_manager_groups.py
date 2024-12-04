import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QListWidget, QListWidgetItem, QPushButton, QWidget, 
                             QMessageBox, QLabel, QGroupBox, QCheckBox, QTabWidget, 
                             QTableWidget, QTableWidgetItem, QInputDialog,  QMessageBox, QScrollArea, QGridLayout, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtGui import QBrush
from ..utils.json_logic import *
from ..utils.name_merge import *
import time
from ..utils.refresh import replace_entities

# Enhanced color scheme with better contrast
BLUE_COLOR = "#3498db"  
WHITE_COLOR = "#FFFFFF"
BACKGROUND_COLOR = "#f8fafc"  # Light gray background
HOVER_BLUE = "#3498db"  
TEXT_COLOR = "#1e293b"  # Darker text for better readability
BORDER_COLOR = "#cbd5e1"  # Subtle border color
GROUP_BOX_BG = "#f1f5f9"  # Light background for group boxes
RED_COLOR = "#e74c3c"

sample_similar_names = [
    ['John', 'Jon', 'Johnny', 'Johny'],
    ['Elizabeth', 'Liz', 'Beth', 'Eliza'],
    ['Michael', 'Mike', 'Mikey']
]

class StyledPushButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {BLUE_COLOR};
                color: {WHITE_COLOR};
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 200px;
            }}
            QPushButton:hover {{
                background-color: {HOVER_BLUE};
            }}
            QPushButton:pressed {{
                background-color: {BLUE_COLOR};
                transform: translateY(1px);
            }}
            QPushButton:disabled {{
                background-color: #94a3b8;
                color: #e2e8f0;
            }}
        """)

class ClickableLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet(f"""
            QLabel {{
                color: {BLUE_COLOR};
                padding: 5px;
                text-decoration: underline;
                font-size: 13px;
                font-weight: 500;
            }}
            QLabel:hover {{
                color: {HOVER_BLUE};
            }}
        """)

class GroupSelector(QMainWindow):
    def __init__(self,case_id, parent, similar_names_groups=sample_similar_names):
        super().__init__()
        self.setWindowTitle(f"Similar Names Merger for Case Id - {case_id}")
        self.setGeometry(100, 100, 1000, 800)
        self.case_id = case_id
        
        start = time.time()
        similar_names_groups = self.get_similar_names()
        self.original_groups = similar_names_groups["original_groups"]
        self.merged_groups = similar_names_groups["merged_groups"]
        if similar_names_groups["unselected_groups"] == [] and similar_names_groups["merged_groups"] == []:
            self.unselected_groups = similar_names_groups["original_groups"]
        else:
            self.unselected_groups = similar_names_groups["unselected_groups"]

        print("merged groups", self.merged_groups)
        print("Unselected groups", self.unselected_groups)
        end = time.time()

        print("Time taken to get similar names in seconds - ",end-start)

        # Enhanced window styling
        self.setStyleSheet(f"""
            *{{
                background-color: {BACKGROUND_COLOR};
            }}
            QMainWindow {{
                background-color: {BACKGROUND_COLOR};
            }}
            QTabWidget::pane {{
                border: 1px solid {BORDER_COLOR};
                background-color: {WHITE_COLOR};
                border-radius: 8px;
                margin-top: -1px;
            }}
            QTabBar::tab {{
                background-color: {BACKGROUND_COLOR};
                padding: 10px 25px;
                margin-right: 4px;
                color: {TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 14px;
            }}
            QTabBar::tab:selected {{
                background-color: {BLUE_COLOR};
                color: {WHITE_COLOR};
                border-color: {BLUE_COLOR};
                font-weight: bold;
            }}
            QGroupBox {{
                background-color: {GROUP_BOX_BG};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                margin-top: 15px;
                padding: 20px;
                font-size: 14px;
                font-weight: bold;
                color: {TEXT_COLOR};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: {TEXT_COLOR};
            }}
            QCheckBox {{
                spacing: 10px;
                color: {TEXT_COLOR};
                font-size: 13px;
                padding: 5px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 2px solid {BLUE_COLOR};
                border-radius: 4px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {BLUE_COLOR};
                image: url(assets/check.png);
            }}
            QCheckBox::indicator:checked:hover {{
                border-color: {HOVER_BLUE};
            }}
            QCheckBox::indicator:hover {{
                border-color: {HOVER_BLUE};
            }}
            QTableWidget {{
                border: 1px solid {BORDER_COLOR};
                background-color: {WHITE_COLOR};
                gridline-color: {BORDER_COLOR};
                border-radius: 8px;
            }}
            QTableWidget::item {{
                padding: 8px;
                color: {TEXT_COLOR};
                font-size: 13px;
            }}
            QHeaderView::section {{
                background-color: {BLUE_COLOR};
                color: {WHITE_COLOR};
                padding: 12px 8px;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }}
            QHeaderView::section:first {{
                border-top-left-radius: 8px;
            }}
            QHeaderView::section:last {{
                border-top-right-radius: 8px;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {BACKGROUND_COLOR};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {BLUE_COLOR};
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """)
        
        # self.merged_history = []

        # Create and set up the central widget with margins
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Create and set up tabs
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Similar Names Tab
        similar_names_tab = QWidget()
        similar_names_layout = QVBoxLayout()
        similar_names_layout.setContentsMargins(20, 20, 20, 20)
        similar_names_layout.setSpacing(15)
        similar_names_tab.setLayout(similar_names_layout)
        
        # Add title label
        title_label = QLabel("Select names to merge")
        self.count_label = QLabel("Total groups: " + str(len(self.unselected_groups)))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
        """)

        self.count_label.setStyleSheet(f"""
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 14px;
                margin-bottom: 10px;
            }}
        """)

        similar_names_layout.addWidget(title_label)
        similar_names_layout.addWidget(self.count_label)

         # Create scroll area for similar names groups
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {BACKGROUND_COLOR};
            }}
            QScrollBar:vertical {{
                border: none;
                background: {BACKGROUND_COLOR};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {BLUE_COLOR};
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """)

        # Create a widget to hold the grid layout
        scroll_content = QWidget()
        self.similar_groups_container = QGridLayout()
        self.similar_groups_container.setSpacing(15)
        scroll_content.setLayout(self.similar_groups_container)
        scroll_area.setWidget(scroll_content)
        
        similar_names_layout.addWidget(scroll_area)

        
        # Merged History Tab
        merged_history_tab = QWidget()
        merged_history_layout = QVBoxLayout()
        merged_history_layout.setContentsMargins(20, 20, 20, 20)
        merged_history_tab.setLayout(merged_history_layout)
        
        # Add tabs
        self.tab_widget.addTab(similar_names_tab, "Similar Names")
        self.tab_widget.addTab(merged_history_tab, "Merged History")
        
        # # Similar Names Container
        # self.similar_groups_container = QVBoxLayout()
        # similar_names_layout.addLayout(self.similar_groups_container)
        
        # Merged History Table
        self.merged_history_table = QTableWidget()
        self.merged_history_table.setColumnCount(2)
        self.merged_history_table.setHorizontalHeaderLabels(["Original Names", "Actions"])
        self.merged_history_table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        self.merged_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        table_width = self.merged_history_table.width()
        self.merged_history_table.setColumnWidth(0, int(table_width * 0.5))
        self.merged_history_table.setColumnWidth(1, int(table_width * 0.5))
        
        # Button container with improved spacing
        final_button_container = QHBoxLayout()
        final_button_container.addStretch()

        # Final submit button for merge history page
        final_merge_btn = StyledPushButton("Merge All Groups")
        final_merge_btn.clicked.connect(self.final_merge_all_groups)
        final_button_container.addWidget(final_merge_btn)
        final_button_container.addStretch()


        merged_history_layout.addWidget(self.merged_history_table)
        merged_history_layout.addLayout(final_button_container)

        
        # Button container with improved spacing
        single_button_container = QHBoxLayout()
        single_button_container.addStretch()
        
        # Merge button
        single_merge_btn = StyledPushButton("Merge Selected Names")
        single_merge_btn.clicked.connect(self.merge_selected_names)
        single_button_container.addWidget(single_merge_btn)
        single_button_container.addStretch()
        
        similar_names_layout.addLayout(single_button_container)
        
        # Populate similar names groups
        self.populate_merged_history_table()
        self.create_similar_names_groups()

    def populate_merged_history_table(self):
        """Populate the merged history table with existing merged groups"""
        # Clear any existing rows first
        self.merged_history_table.setRowCount(0)
        
        # Iterate through merged groups and add to the table
        for merged_group in self.merged_groups:
            row_position = self.merged_history_table.rowCount()
            self.merged_history_table.insertRow(row_position)
            
            # Create original names string (join all names in the merged group)
            original_names = ', '.join(merged_group)
            
            # Create and set original names item
            original_names_item = QTableWidgetItem(original_names)
            self.merged_history_table.setItem(row_position, 0, original_names_item)
            
            # Add "Demerge" text to the actions column
            demerge_label = QTableWidgetItem("Demerge")
            demerge_label.setForeground(QBrush(QColor(255,0,0)))
            demerge_label.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.merged_history_table.setItem(row_position, 1, demerge_label)
        
    def get_similar_names(self):
        """Get similar names groups for a given case ID"""
        print("case_id name manager groups",self.case_id)
        merged_names_object = find_merge_name_object(self.case_id)
        data = load_result(self.case_id)

        group_of_similar_entities = None

        # if "similar_entities" not in data["cummalative_df"]:
        #     process_df = None
        #     try:
        #         process_df = data["cummalative_df"]["process_df"] 
        #     except:
        #         process_df = data["cummalative_df"]["df"]

        #     unique_values = extract_unique_names_and_entities(process_df)
        #     group_of_similar_entities = group_similar_entities(unique_values)
        #     # data["cummalative_df"]["similar_entities"] = group_of_similar_entities
        #     # save_result(self.case_id,data)
        #     print("Saved similar entities in pkl")
        # else:
        #     group_of_similar_entities = data["cummalative_df"]["similar_entities"]

        if merged_names_object == None:
            process_df = data["cummalative_df"]["process_df"]
            unique_values = extract_unique_names_and_entities(process_df)
            similar_groups = group_similar_entities(unique_values)

            obj = {
                "case_id":self.case_id,
                "original_groups":similar_groups,
                "merged_groups":[],
                "unselected_groups":[],
            }

            create_name_merge_object(obj)
            group_of_similar_entities = obj
        else:
            group_of_similar_entities = merged_names_object

        # Call the function which takes in process df and returns similar names
        return group_of_similar_entities

    def final_merge_all_groups(self):

        if self.unselected_groups:
            # Show error message if there are still groups to merge
            self.show_error_message(f"Please merge all {len(self.unselected_groups)} remaining name groups before final submission.")
            return
        
        # Show confirmation dialog
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("Confirm Merge")
        msg.setText("Are you sure you want to merge all groups?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {WHITE_COLOR};
            }}
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 14px;
                padding: 10px;
            }}
            QPushButton {{
                background-color: {BLUE_COLOR};
                color: {WHITE_COLOR};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {HOVER_BLUE};
            }}
        """)

        reply = msg.exec()

        if reply == QMessageBox.StandardButton.Yes:
            # self.merged_groups
            print("Get old process df")
            process_df = get_process_df(self.case_id)
            print("Got old process df, now replacing entities")
            new_process_df = replace_entities(process_df,self.merged_groups)
            print("Replaced entities Got new process df, now updating process df and running refresh function")
            response = update_process_df(self.case_id,new_process_df)
            print("Updated process df and ran refresh function reponse = ",response)
            if response == True:
                self.show_success_message("Successfully merged all groups")
                self.close()
            else:
                self.show_error_message("Error while merging groups")
        else:
            return


    def create_similar_names_groups(self):
        """Create UI for each group of similar names in a grid layout"""
        self.clear_layout(self.similar_groups_container)

        if not self.unselected_groups:
            # Show a message if there are no similar names
            text_style = f"""
                    QLabel {{
                        color: {TEXT_COLOR};
                        font-size: 14px;
                    }}
                """
            no_names_label = QLabel("No similar names found")

            if not self.unselected_groups:
                no_names_label = QLabel("All names have been merged")
            no_names_label.setStyleSheet(text_style)
           
            self.similar_groups_container.addWidget(no_names_label)
            self.similar_groups_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return
        
        for i, group in enumerate(self.unselected_groups):
            group_box = QGroupBox(f"Similar Names Group {i + 1}")
            group_layout = QVBoxLayout()
            group_layout.setSpacing(8)
            group_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align names to the top

            name_radios = []
            radio_group = QWidget()
            radio_group_layout = QVBoxLayout()
            radio_group_layout.setSpacing(8)
            radio_group_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align names to the top

            radio_group.setLayout(radio_group_layout)
            
            for name in group:
                radio = QCheckBox(name)
                radio_group_layout.addWidget(radio)
                name_radios.append(radio)
                radio.stateChanged.connect(self.handle_radio_state)

            radio_group_layout.addStretch(1)

            group_layout.addWidget(radio_group)
            group_box.setLayout(group_layout)
            group_box.name_radios = name_radios
            
            # Calculate row and column for grid layout
            row = i // 2  # Integer division to determine row
            col = i % 2   # Remainder to determine column
            self.similar_groups_container.addWidget(group_box, row, col)
        
        # Add stretch to the last row
        last_row = (len(self.unselected_groups) - 1) // 2 + 1
        self.similar_groups_container.setRowStretch(last_row, 1)

    def update_json(self):
        merged_names_object = find_merge_name_object(self.case_id)
        merged_names_object["merged_groups"] = self.merged_groups
        merged_names_object["unselected_groups"] = self.unselected_groups

        update_name_merge_object(self.case_id,merged_names_object)


    def clear_layout(self, layout):
        """Helper method to clear all widgets from a layout"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def handle_radio_state(self, state):
        """Handle radio button state changes"""
        sender = self.sender()
        if state == Qt.CheckState.Checked:
            for i in range(self.similar_groups_container.count()):
                item = self.similar_groups_container.itemAt(i)
                if not item or not isinstance(item.widget(), QGroupBox):
                    continue
                
                group_box = item.widget()
                for radio in group_box.name_radios:
                    if radio != sender:
                        radio.setChecked(False)

    def merge_selected_names(self):
        """Handle merging of selected names"""
        selected_groups = []

        for i in range(self.similar_groups_container.count()):
            item = self.similar_groups_container.itemAt(i)
            
            if not item or not isinstance(item.widget(), QGroupBox):
                continue
            
            group_box = item.widget()
            name_radios = group_box.name_radios
            selected_names = [radio.text() for radio in name_radios if radio.isChecked()]
            original_group = [radio.text() for radio in name_radios]
            
            if selected_names:
                selected_groups.append((original_group, selected_names))
        if selected_groups == []:
            self.show_error_message("No names selected for merging")
            return
        

        # Show confirmation dialog
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("Confirm Merge")
        msg.setText(f"Are you sure you want to merge these names?\n\n{', '.join(selected_names)}")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {WHITE_COLOR};
            }}
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 14px;
                padding: 10px;
            }}
            QPushButton {{
                background-color: {BLUE_COLOR};
                color: {WHITE_COLOR};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {HOVER_BLUE};
            }}
        """)
        
        reply = msg.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            # original_group, selected_names = selected_group
            for selected_group in selected_groups:
                if selected_group == []:
                    continue
                original_group, selected_names = selected_group
                # Use the first selected name as the merged name
                self.process_merge(selected_names, original_group)
            
            self.update_json()
            self.count_label.setText("Total groups: " + str(len(self.unselected_groups)))
            self.tab_widget.setCurrentIndex(1)

    def show_error_message(self, message):
        """Show styled error message"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Merge Error")
        msg.setText(message)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {WHITE_COLOR};
            }}
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 14px;
                padding: 10px;
            }}
            QPushButton {{
                background-color: {BLUE_COLOR};
                color: {WHITE_COLOR};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {HOVER_BLUE};
            }}
        """)
        msg.exec()

    def get_merged_name_input(self):
        """Get merged name input with styled dialog"""
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Merge Names")
        dialog.setLabelText("Enter the name to merge into:")
        dialog.setStyleSheet(f"""
            QInputDialog {{
                background-color: {WHITE_COLOR};
            }}
            QLineEdit {{
                padding: 8px;
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
                background-color: {WHITE_COLOR};
                color: {TEXT_COLOR};
                font-size: 14px;
            }}
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 14px;
                padding: 5px;
            }}
            QPushButton {{
                background-color: {BLUE_COLOR};
                color: {WHITE_COLOR};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {HOVER_BLUE};
            }}
        """)
        
        ok = dialog.exec()
        return dialog.textValue() if ok else None

    def process_merge(self, selected_names, original_group):
        """Process the merging of names"""
        original_names = ', '.join(selected_names)

        # merged_entry = {
        #     'original_names': original_names, 
        #     'original_group': original_group,
        # }
        self.merged_groups.append(selected_names)

        self.unselected_groups.remove(original_group)


        self.create_similar_names_groups()

        # Add to history table
        row_position = self.merged_history_table.rowCount()
        self.merged_history_table.insertRow(row_position)
        
        # Create and style table items
        original_names_item = QTableWidgetItem(original_names)
        
        self.merged_history_table.setItem(row_position, 0, original_names_item)
        
        # Add "Demerge" text directly to the third column
        demerge_label = QTableWidgetItem("Demerge")
        demerge_label.setForeground(QBrush(QColor(255,0,0)))
        demerge_label.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.merged_history_table.setItem(row_position, 1, demerge_label)
        
        # Modify the table to allow clicking the entire row for demerge
        self.merged_history_table.itemClicked.connect(self.handle_row_click)

    def handle_row_click(self, item):
        """Handle row click for demerging"""
        if item.column() == 1:  # Clicked in the Demerge column
            row = item.row()
            self.demerge_names(row)

    def show_success_message(self, message):
        """Show styled success message"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Success")
        msg.setText(message)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {WHITE_COLOR};
            }}
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 14px;
                padding: 10px;
            }}
            QPushButton {{
                background-color: {BLUE_COLOR};
                color: {WHITE_COLOR};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {HOVER_BLUE};
            }}
        """)
        msg.exec()

    def demerge_names(self, row):
        """Handle demerging of names"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle('Demerge Confirmation')
        msg.setText('Are you sure you want to demerge these names?')
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background-color: {WHITE_COLOR};
            }}
            QLabel {{
                color: {TEXT_COLOR};
                font-size: 14px;
                padding: 10px;
            }}
            QPushButton {{
                background-color: {BLUE_COLOR};
                color: {WHITE_COLOR};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {HOVER_BLUE};
            }}
        """)
        
        reply = msg.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            # Get the merged group to demerge
            merged_group = self.merged_groups[row]
            # get original groups from self.original_names bascially check every group and see if it contains all items  of merged group
            # if yes then that is the original group
            original_group = None

            for group in self.original_groups:
                if all(item in group for item in merged_group):
                    original_group = group
                    break
            
            # Add the group back to unselected groups
            self.unselected_groups.append(original_group)
            
            # Remove the group from merged groups
            self.merged_groups.pop(row)
            
            # Update the JSON 
            self.update_json()
            
            # Recreate the similar names groups UI
            self.create_similar_names_groups()
            
            # Remove the row from the history table
            self.merged_history_table.removeRow(row)
            
            self.count_label.setText("Total groups: " + str(len(self.unselected_groups)))

            # Switch to the Similar Names tab
            self.tab_widget.setCurrentIndex(0)
            
            # Show success message
            self.show_success_message("Successfully demerged names")

    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        
        # Update table column widths
        table_width = self.merged_history_table.width()
        self.merged_history_table.setColumnWidth(0, int(table_width * 0.4))
        self.merged_history_table.setColumnWidth(1, int(table_width * 0.4))
        self.merged_history_table.setColumnWidth(2, int(table_width * 0.2))

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application-wide font
    font = QFont("Segoe UI", 10)  # Use system font with reasonable size
    app.setFont(font)
    
    window = GroupSelector(sample_similar_names)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()