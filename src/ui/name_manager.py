import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QListWidget, QListWidgetItem, QPushButton, QWidget, 
                             QMessageBox, QLabel, QGroupBox, QCheckBox, QTabWidget, 
                             QTableWidget, QTableWidgetItem, QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtWidgets import QSizePolicy

# Define the color scheme
BLUE_COLOR = "#3498db"
WHITE_COLOR = "#FFFFFF"
LIGHT_BLUE = "#ECF0F1"
HOVER_BLUE = "#2980b9"
TEXT_COLOR = "#2c3e50"  # Dark color for text

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
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                width: 200px;  /* Fixed width for buttons */
            }}
            QPushButton:hover {{
                background-color: {HOVER_BLUE};
            }}
            QPushButton:pressed {{
                background-color: {BLUE_COLOR};
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
                cursor: pointer;
            }}
            QLabel:hover {{
                color: {HOVER_BLUE};
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class NameManagerTab(QMainWindow):
    def __init__(self, similar_names_groups=sample_similar_names):
        super().__init__()
        self.setWindowTitle("Similar Names Merger")
        self.setGeometry(100, 100, 900, 700)
        
        # Set the window style
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {WHITE_COLOR};
            }}
            QTabWidget::pane {{
                border: 1px solid #cccccc;
                background-color: {WHITE_COLOR};
                top: -1px;
            }}
            QTabBar::tab {{
                background-color: #f0f0f0;
                padding: 8px 20px;
                margin-right: 2px;
                color: #666;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {BLUE_COLOR};
                color: white;
                border-color: {BLUE_COLOR};
            }}
            QGroupBox {{
                background-color: {WHITE_COLOR};
                border: 1px solid #cccccc;
                border-radius: 6px;
                margin-top: 12px;
                padding: 15px;
            }}
            QCheckBox {{
                spacing: 8px;
                color: {TEXT_COLOR};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {BLUE_COLOR};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {BLUE_COLOR};
            }}
            QTableWidget {{
                border: 1px solid #cccccc;
                background-color: {WHITE_COLOR};
                gridline-color: #e0e0e0;
            }}
            QTableWidget::item {{
                padding: 5px;
                color: {TEXT_COLOR};  /* Set text color for table items */
            }}
            QHeaderView::section {{
                background-color: {BLUE_COLOR};
                color: white;
                padding: 8px;
                border: none;
            }}
            QHeaderView[orientation="horizontal"] {{
                border-bottom: 1px solid #cccccc;
            }}
        """)
        
        self.similar_names_groups = similar_names_groups
        self.merged_history = []
        
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Create tabs
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Similar Names Tab
        similar_names_tab = QWidget()
        similar_names_layout = QVBoxLayout()
        similar_names_tab.setLayout(similar_names_layout)
        
        # Merged History Tab
        merged_history_tab = QWidget()
        merged_history_layout = QVBoxLayout()
        merged_history_layout.setContentsMargins(0, 0, 0, 0)
        merged_history_tab.setLayout(merged_history_layout)
        
        # Add tabs
        self.tab_widget.addTab(similar_names_tab, "Similar Names")
        self.tab_widget.addTab(merged_history_tab, "Merged History")
        
        # Similar Names Container
        self.similar_groups_container = QVBoxLayout()
        similar_names_layout.addLayout(self.similar_groups_container)
        
        # Merged History Table
        self.merged_history_table = QTableWidget()
        self.merged_history_table.setColumnCount(3)
        self.merged_history_table.setHorizontalHeaderLabels(["Original Names", "Merged Name", "Actions"])
        self.merged_history_table.horizontalHeader().setStretchLastSection(False)
        self.merged_history_table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Set column widths
        table_width = self.width()
        self.merged_history_table.setColumnWidth(0, int(table_width * 0.4))
        self.merged_history_table.setColumnWidth(1, int(table_width * 0.4))
        self.merged_history_table.setColumnWidth(2, int(table_width * 0.2))
        
        merged_history_layout.addWidget(self.merged_history_table)
        
        # Button container for center alignment
        button_container = QHBoxLayout()
        button_container.addStretch()
        
        # Merge button using styled button
        merge_btn = StyledPushButton("Merge Selected Group")
        merge_btn.clicked.connect(self.merge_selected_names)
        button_container.addWidget(merge_btn)
        button_container.addStretch()
        
        similar_names_layout.addLayout(button_container)
        
        # Populate similar names groups
        self.create_similar_names_groups()
        
        # Ensure the table fills the available space
        self.merged_history_table.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

    def create_similar_names_groups(self):
        """Create UI for each group of similar names"""
        # Clear any existing groups
        for i in range(self.similar_groups_container.count()):
            item = self.similar_groups_container.itemAt(0)
            if item.widget():
                item.widget().deleteLater()
            self.similar_groups_container.removeItem(item)
        
        for group in self.similar_names_groups:
            # Create a group box for each set of similar names
            group_box = QGroupBox("Similar Names Group")
            group_layout = QVBoxLayout()
            
            # Create radio buttons instead of checkboxes to ensure only one group is selected
            name_radios = []
            radio_group = QWidget()
            radio_group_layout = QVBoxLayout()
            radio_group.setLayout(radio_group_layout)
            
            for name in group:
                radio = QCheckBox(name)
                radio_group_layout.addWidget(radio)
                name_radios.append(radio)
                
                # Ensure only one radio can be checked at a time
                radio.stateChanged.connect(self.handle_radio_state)
            
            group_box.setLayout(group_layout)
            group_layout.addWidget(radio_group)
            
            self.similar_groups_container.addWidget(group_box)
            
            # Store radios as an attribute of the group box for later reference
            group_box.name_radios = name_radios
        
        # Add stretch to push everything to the top
        self.similar_groups_container.addStretch(1)

    def handle_radio_state(self, state):
        """Ensure only one group can be selected at a time"""
        sender = self.sender()
        if state == Qt.CheckState.Checked:
            # Uncheck radios in other groups
            for i in range(self.similar_groups_container.count()):
                group_box = self.similar_groups_container.itemAt(i).widget()
                if not isinstance(group_box, QGroupBox):
                    continue
                
                for radio in group_box.name_radios:
                    if radio != sender:
                        radio.setChecked(False)
    
    def merge_selected_names(self):
        """Merge selected names within their respective groups"""
        selected_group = None
        
        # Find the selected group
        for i in range(self.similar_groups_container.count()):
            group_box = self.similar_groups_container.itemAt(i).widget()
            
            if not isinstance(group_box, QGroupBox):
                continue
            
            name_radios = group_box.name_radios
            selected_names = [radio.text() for radio in name_radios if radio.isChecked()]
            
            if selected_names:
                if selected_group is not None:
                    QMessageBox.warning(self, "Merge Error", "Please select only one group to merge at a time")
                    return
                selected_group = (group_box, selected_names)
        
        if selected_group:
            group_box, selected_names = selected_group
            
            # Create and style the input dialog
            dialog = QInputDialog(self)
            dialog.setWindowTitle("Merge Names")
            dialog.setLabelText("Enter the name to merge into:")
            dialog.setStyleSheet("""
                QInputDialog {
                    background-color: white;
                }
                QLineEdit {
                    padding: 5px;
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    background-color: white;
                    color: black;
                }
                QLabel {
                    color: black;
                }
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            
            ok = dialog.exec()
            merged_name = dialog.textValue()
            
            if ok and merged_name:
                original_names = ', '.join(selected_names)
                merged_entry = {
                    'original_names': original_names, 
                    'merged_name': merged_name,
                    'original_group': selected_names
                }
                self.merged_history.append(merged_entry)
                
                row_position = self.merged_history_table.rowCount()
                self.merged_history_table.insertRow(row_position)
                
                # Add items with explicit text color
                original_names_item = QTableWidgetItem(original_names)
                merged_name_item = QTableWidgetItem(merged_name)
                self.merged_history_table.setItem(row_position, 0, original_names_item)
                self.merged_history_table.setItem(row_position, 1, merged_name_item)
                
                # Create clickable label for demerge
                demerge_label = ClickableLabel("Demerge")
                demerge_label.mousePressEvent = lambda _, row=row_position: self.demerge_names(row)
                
                # Create a widget to center the label
                label_container = QWidget()
                label_layout = QHBoxLayout(label_container)
                label_layout.addWidget(demerge_label)
                label_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label_layout.setContentsMargins(0, 0, 0, 0)
                
                self.merged_history_table.setCellWidget(row_position, 2, label_container)
                
                self.similar_groups_container.removeWidget(group_box)
                group_box.deleteLater()
                
                self.similar_names_groups = [
                    group for group in self.similar_names_groups 
                    if not all(name in selected_names for name in group)
                ]
                
                self.tab_widget.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Merge Error", "No names selected for merging")
    
    def demerge_names(self, row):
        """Demerge names from the merged history"""
        reply = QMessageBox.question(
            self, 'Demerge Confirmation', 
            'Are you sure you want to demerge these names?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            merged_entry = self.merged_history[row]
            original_group = merged_entry['original_group']
            
            self.similar_names_groups.append(original_group)
            self.create_similar_names_groups()
            
            self.merged_history.pop(row)
            self.merged_history_table.removeRow(row)
            
            self.tab_widget.setCurrentIndex(0)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = NameManagerTab(sample_similar_names)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()