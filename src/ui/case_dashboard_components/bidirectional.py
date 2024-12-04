from utils.dynamic_table import DynamicDataTable
import pickle
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot
import json
from PyQt6.QtCore import Qt
import pandas as pd

class BiDirectionalAnalysisWidget(QWidget):
    def __init__(self, result,case_id, parent=None):
        super().__init__(parent),
        self.result = result
        self.case_id = case_id
        self.bidirectional_analysis_data = result["cummalative_df"]["bidirectional_analysis"]
        # self.bidirectional_analysis_data = None
        # with open("src/data/dummy/bidirectional.pkl", 'rb') as f:
        #     dummy_data= pickle.load(f)
        #     self.bidirectional_analysis_data = dummy_data
        
        # print("self.bidirectional_analysis_data ",self.bidirectional_analysis_data)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
         # Check if lifo_fifo_analysis_data is empty
        self.is_data_empty = False
        try:
            if self.bidirectional_analysis_data.empty:
                self.is_data_empty = True
        except:
            if not self.bidirectional_analysis_data:
                self.is_data_empty = True
                

        if self.is_data_empty:
            self.show_no_data_message()
        else:
            # self.create_dropdowns()
            self.create_table()
        
        self.setLayout(self.layout)
    def show_no_data_message(self):
            # Create a QLabel with a message directing user to Name Manager
            no_data_label = QLabel(f"No data available. Please go to Name Manager tab and merge names for case id {self.case_id}")
            no_data_label.setStyleSheet("""
                color: #555;
                font-size: 16px;
                padding: 20px;
                text-align: center;
            """)
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_data_label.setWordWrap(True)
            self.layout.addWidget(no_data_label)
    def create_table(self):
        self.bidirectional_analysis_table = DynamicDataTable(
            # df=self.bidirectional_analysis_data,
            df=self.bidirectional_analysis_data,
            # title="Link Analysis Data Table",  # Optional
            rows_per_page=10 , # Optional,
        )
        self.layout.addWidget(self.bidirectional_analysis_table)
        

    def create_dropdowns(self):
        class Handler(QObject):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.widget = parent

            @pyqtSlot(str)
            def handleFilters(self, filters_json):
                filters = json.loads(filters_json)
                self.widget.apply_filters(filters)

        self.web_view = QWebEngineView()
        self.channel = QWebChannel(self.web_view.page())
        self.handler = Handler(self)
        self.channel.registerObject('handler', self.handler)
        self.web_view.page().setWebChannel(self.channel)

        entities = sorted(self.result["cummalative_df"]["entity_df"]['Entity'].dropna().unique())
        # entities = sorted(self.bidirectional_analysis_data['Entity One'].dropna().unique())

        entity_options = '\n'.join([f'<option value="{entity}">{entity}</option>' for entity in entities])

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Link Analysis Filters</title>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/css/select2.min.css" rel="stylesheet" />
            <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/js/select2.min.js"></script>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <style>
                :root {{
                    --primary-blue: #3498db;
                    --accent-red: #b82214;
                    --border-color: #e2e8f0;
                    --text-color: #1e293b;
                    --background: #f8fafc;
                }}

                body {{
                    margin: 0;
                    padding: 0;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: var(--background);
                    height: 100vh;
                }}

                .filters-container {{
                    padding: 1.5rem;
                    background: white;
                    border-bottom: 1px solid var(--border-color);
                    position: relative;
                    z-index: 1;
                    margin:0 0.5rem;
                }}

                .filter-group {{
                    margin-bottom: 0.5rem;
                    position: relative;
                }}

                .filter-group:last-child {{
                    margin-bottom: 0.5rem;
                }}

                label {{
                    display: block;
                    font-size: 0.875rem;
                    font-weight: 500;
                    color: var(--text-color);
                    margin-bottom: 0.5rem;
                }}

                /* Select2 Customization */
                .select2-container {{
                    width: 100% !important;
                    margin-bottom: 0.5rem;
                }}

                .select2-container--default .select2-selection--multiple {{
                    border: 1px solid var(--border-color);
                    border-radius: 0.375rem;
                    min-height: 2.5rem;
                    padding: 0.25rem;
                }}

                .select2-container--default.select2-container--focus .select2-selection--multiple {{
                    border-color: var(--primary-blue);
                    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
                }}

                .select2-container--default .select2-selection--multiple .select2-selection__choice {{
                    background-color: var(--primary-blue);
                    color: white;
                    border: none;
                    border-radius: 0.25rem;
                    padding: 0.25rem 0.5rem;
                    margin: 0.25rem;
                }}

                .select2-container--default .select2-selection--multiple .select2-selection__choice__remove {{
                    color: white;
                    margin-right: 0.5rem;
                }}

                .select2-dropdown {{
                    border-color: var(--border-color);
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    z-index: 9999;
                }}

                .select2-container--open .select2-dropdown {{
                    position: absolute;
                    z-index: 100000 !important;
                    background: white;
                    border: 1px solid #e2e8f0;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                }}

                .select2-container {{
                    position: relative;
                    z-index: 10000;
                }}

                .select2-results {{
                    max-height: 300px;
                    overflow-y: auto;
                }}

                /* Ensure the dropdown container is above other elements */
                .filters-container {{
                    position: relative;
                    z-index: 1000;
                    background: white;
                }}
                .select2-results__option {{
                    padding: 0.5rem;
                }}

                .select2-container--default .select2-results__option--highlighted[aria-selected] {{
                    background-color: var(--primary-blue);
                }}

                .buttons-container {{
                    display: flex;
                    gap: 1rem;
                    margin-top: 0.5rem;
                }}

                .button {{
                    flex: 1;
                    padding: 0.75rem 1rem;
                    border: none;
                    border-radius: 0.375rem;
                    font-weight: 500;
                    font-size: 0.875rem;
                    cursor: pointer;
                    transition: all 0.2s;
                }}

                .apply-btn {{
                    background: var(--primary-blue);
                    color: white;
                }}

                .apply-btn:hover {{
                    background: #3498db;
                }}

                .reset-btn {{
                    background: var(--accent-red);
                    color: white;
                }}

                .reset-btn:hover {{
                    background: #991b1b;
                }}
            </style>
        </head>
        <body>
            <div class="filters-container">
                <div class="filter-group">
                    <label for="entity-dropdown">Interest Entities</label>
                    <select id="entity-dropdown" multiple="multiple">
                        {entity_options}
                    </select>
                </div>
                <div class="buttons-container">
                    <button class="button apply-btn" onclick="applyFilters()">Apply Filters</button>
                    <button class="button reset-btn" onclick="resetFilters()">Reset</button>
                </div>
            </div>
            <script>
                let qtChannel = null;
                function initWebChannel() {{
                    new QWebChannel(qt.webChannelTransport, function(channel) {{
                        qtChannel = channel;
                    }});
                }}

                function initSelects() {{
                    $('#entity-dropdown').select2({{
                        placeholder: 'Select interested entities...',
                        allowClear: true,
                        closeOnSelect: false,
                        width: '100%',
                        dropdownParent: $('body')
                    }});
                }}

                function applyFilters() {{
                    if (!qtChannel) return;
                    
                    const selectedEntities = $('#entity-dropdown').val() || [];
                    
                    qtChannel.objects.handler.handleFilters(
                        JSON.stringify({{
                            entities: selectedEntities,
                        }})
                    );
                }}

                function resetFilters() {{
                    $('#entity-dropdown').val(null).trigger('change');
                    
                    if (qtChannel) {{
                        qtChannel.objects.handler.handleFilters(
                            JSON.stringify({{
                                names: [],
                                entities: [],
                            }})
                        );
                    }}
                }}

                $(document).ready(function() {{
                    initWebChannel();
                    initSelects();
                }});
            </script>
        </body>
        </html>
        """

        self.web_view.setHtml(html_content)
        self.web_view.setFixedHeight(250)  # Increased height to accommodate dropdowns
        self.layout.addWidget(self.web_view)


# def create_bidirectional_analysis(result):

#     dummy_data = None
#     with open("src/data/dummy/bidirectional.pkl", 'rb') as f:
#         dummy_data= pickle.load(f)

#     bidirectional_analysis_table = DynamicDataTable(
#         # df=result["cummalative_df"]["bidirectional_analysis"],
#         df=dummy_data,
#         # title="Link Analysis Data Table",  # Optional
#         rows_per_page=10 , # Optional,
#     )
#     # link_analysis_table.create_table(content_layout)
#     return bidirectional_analysis_table