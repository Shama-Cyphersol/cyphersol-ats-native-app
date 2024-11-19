from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QPushButton
from utils.dynamic_table import DynamicDataTable
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, QObject, pyqtSlot
import json

class LinkAnalysisWidget(QWidget):
    def __init__(self, result, parent=None):
        super().__init__(parent)
        self.result = result
        # Apply initial filtering for valid transactions
        self.link_analysis_data = self.filter_valid_transactions(result["cummalative_df"]["link_analysis_df"])
        self.layout = QVBoxLayout(self)
        
        # Create dropdowns
        self.create_dropdowns()
        
        # Create table
        self.create_table()
        
        self.setLayout(self.layout)
    
    def filter_valid_transactions(self, df):
        """Filter transactions that have non-zero values and non-null entities"""
        # Filter for rows where either credit or debit is non-zero/non-null
        valid_transactions = df[
            (
                (df['Total_Credit'].notna() & (df['Total_Credit'] != 0)) |
                (df['Total_Debit'].notna() & (df['Total_Debit'] != 0))
            ) &
            (df['Entity'].notna() & (df['Entity'].str.strip() != ""))  # Ensure Entity is not null and not empty string
        ]
        return valid_transactions
        
    def create_dropdowns(self):
        # Create handler for JavaScript communication
        class Handler(QObject):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.widget = parent

            @pyqtSlot(str)
            def handleFilters(self, filters_json):
                filters = json.loads(filters_json)
                self.widget.apply_filters(filters)

        # Create a QWebEngineView for the HTML dropdowns
        self.web_view = QWebEngineView()
        
        # Initialize web channel
        self.channel = QWebChannel(self.web_view.page())
        self.handler = Handler(self)
        self.channel.registerObject('handler', self.handler)
        self.web_view.page().setWebChannel(self.channel)
        
        # Get unique values from Name and Entity columns (from filtered data)
        names = self.link_analysis_data['Name'].unique().tolist()
        entities = self.link_analysis_data['Entity'].unique().tolist()
        
        # Create options HTML for both dropdowns
        name_options = '\n'.join([f'<option value="{name}">{name}</option>' for name in names])
        entity_options = '\n'.join([f'<option value="{entity}">{entity}</option>' for entity in entities])
        
        # HTML content remains the same as before
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/css/select2.min.css" rel="stylesheet" />
            <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/js/select2.min.js"></script>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <style>
                .container {{
                    padding: 15px;
                    font-family: Arial, sans-serif;
                }}
                .dropdown-group {{
                    margin-bottom: 15px;
                }}
                label {{
                    display: block;
                    margin-bottom: 5px;
                    font-weight: bold;
                }}
                .select2-container {{
                    width: 300px !important;
                    margin-bottom: 10px;
                }}
                .apply-btn {{
                    background-color: #3498db;
                    color: white;
                    padding: 10px 20px;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                    height: 40px;
                    width: 150px;
                    margin-top:18px;
                }}
                .apply-btn:hover {{
                    background-color: #3498db;
                }}
                .filters-container {{
                    display: flex;
                    gap: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="filters-container">
                    <div class="dropdown-group">
                        <label for="name-dropdown">Names:</label>
                        <select id="name-dropdown" multiple="multiple">
                            {name_options}
                        </select>
                    </div>
                    
                    <div class="dropdown-group">
                        <label for="entity-dropdown">Entities:</label>
                        <select id="entity-dropdown" multiple="multiple">
                            {entity_options}
                        </select>
                    </div>
                    <div class="dropdown-group">
                        <button class="apply-btn" onclick="applyFilters()">Apply Filters</button>
                    </div>
                </div>
            </div>
            <script>
                let qtChannel = null;
                function initWebChannel() {{
                    new QWebChannel(qt.webChannelTransport, function(channel) {{
                        qtChannel = channel;
                        console.log("WebChannel initialized");
                    }});
                }}
                
                function initSelects() {{
                    $('#name-dropdown').select2({{
                        placeholder: 'Select Names',
                        allowClear: true,
                        width: '100%'
                    }});
                    $('#entity-dropdown').select2({{
                        placeholder: 'Select Entities',
                        allowClear: true,
                        width: '100%'
                    }});
                }}

                function applyFilters() {{
                    if (!qtChannel) {{
                        console.error("Channel not initialized");
                        return;
                    }}
                    
                    const selectedNames = $('#name-dropdown').val() || [];
                    const selectedEntities = $('#entity-dropdown').val() || [];
                    
                    qtChannel.objects.handler.handleFilters(
                        JSON.stringify({{
                            names: selectedNames,
                            entities: selectedEntities
                        }})
                    );
                }}

                $(document).ready(function() {{
                    initWebChannel();
                    initSelects();
                }});
            </script>
        </body>
        </html>
        """
        
        # Set the HTML content to the web view
        self.web_view.setHtml(html_content)
        self.web_view.setFixedHeight(200)  # Adjust height as needed
        self.layout.addWidget(self.web_view)

    def apply_filters(self, filters):
        """Apply the selected filters to the table data"""
        # Start with the pre-filtered valid transactions
        filtered_data = self.link_analysis_data.copy()
        
        selected_names = filters['names']
        selected_entities = filters['entities']
        
        # Apply name filter if names are selected
        if selected_names:
            filtered_data = filtered_data[filtered_data['Name'].isin(selected_names)]
            
        # Apply entity filter if entities are selected
        if selected_entities:
            filtered_data = filtered_data[filtered_data['Entity'].isin(selected_entities)]
        
        # Update the table with filtered data
        if hasattr(self, 'link_analysis_table'):
            self.layout.removeWidget(self.link_analysis_table)
            self.link_analysis_table.deleteLater()
        
        self.link_analysis_table = DynamicDataTable(
            df=filtered_data,
            rows_per_page=10,
            table_for="link_analysis",
        )
        self.layout.addWidget(self.link_analysis_table)
        
    def create_table(self):
        self.link_analysis_table = DynamicDataTable(
            df=self.link_analysis_data,
            rows_per_page=10,
            table_for="link_analysis",
        )
        self.layout.addWidget(self.link_analysis_table)
    
    def update_table(self, new_result):
        """Method to update the table with new data"""
        self.result = new_result
        # Apply filtering to the new data
        self.link_analysis_data = self.filter_valid_transactions(new_result["cummalative_df"]["link_analysis_df"])
        # Remove existing table
        if hasattr(self, 'link_analysis_table'):
            self.layout.removeWidget(self.link_analysis_table)
            self.link_analysis_table.deleteLater()
        # Create new table with updated data
        self.create_table()
        # Update dropdowns with new data
        self.create_dropdowns()