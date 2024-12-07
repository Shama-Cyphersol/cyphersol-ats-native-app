from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QMessageBox
from utils.dynamic_table import DynamicDataTable
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QUrl, QObject, pyqtSlot
import json
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel

class LinkAnalysisWidget(QWidget):
    def __init__(self, result,case_id,parent=None):
        super().__init__(parent)
        self.result = result
        self.case_id = case_id
        self.link_analysis_data = self.filter_valid_transactions(result["cummalative_df"]["link_analysis_df"])
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.is_data_empty = False
        try:
            if self.link_analysis_data.empty:
                self.is_data_empty = True
        except:
            if not self.link_analysis_data:
                self.is_data_empty = True

         # Check if lifo_fifo_analysis_data is empty
        if self.is_data_empty:
            no_data_label = QLabel(f"No data available. Please go to Name Manager tab and merge names for case id {self.case_id}")
            no_data_label.setStyleSheet("""
                color: #555;
                font-size: 16px;
                padding: 20px;
                text-align: center;
            """)
            no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.layout.addWidget(no_data_label)
        else:
            self.create_dropdowns()
            self.create_table()
            self.setLayout(self.layout)

    def filter_valid_transactions(self, df):
        if df.empty:
            return df
        valid_transactions = df[
            (
                (df['Total_Credit'].notna() & (df['Total_Credit'] != 0)) |
                (df['Total_Debit'].notna() & (df['Total_Debit'] != 0))
            ) &
            (df['Entity'].notna() & (df['Entity'].str.strip() != ""))
        ]
        return valid_transactions

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

        names = sorted(self.link_analysis_data['Name'].dropna().unique())
        entities = sorted(self.link_analysis_data['Entity'].dropna().unique())

        name_options = '\n'.join([f'<option value="{name}">{name}</option>' for name in names])
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
                }}

                .filters-container {{
                    padding: 1.5rem;
                    background: white;
                    border-bottom: 1px solid var(--border-color);
                    position: relative;
                    z-index: 1;
                }}

                .filter-group {{
                    margin-bottom: 1.5rem;
                    position: relative;
                }}

                .filter-group:last-child {{
                    margin-bottom: 1rem;
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
                .filter-groups {{
                    display: flex;
                    flex: 1;
                    margin-right: 1rem;
                }}
                .filter-group {{
                    flex: 1;
                    margin-right: 1rem;
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
                    margin-top: 1rem;
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
                    max-width: 10rem;
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
                <div class="filter-groups">
                    <div class="filter-group">
                        <label for="name-dropdown">Names</label>
                        <select id="name-dropdown" multiple="multiple">
                            {name_options}
                        </select>
                    </div>
                    <div class="filter-group">
                        <label for="entity-dropdown">Entities</label>
                        <select id="entity-dropdown" multiple="multiple">
                            {entity_options}
                    </select>
                    </div>
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
                    $('#name-dropdown').select2({{
                        placeholder: 'Select names...',
                        allowClear: true,
                        closeOnSelect: false,
                        width: '100%',
                        dropdownParent: $('.filters-container')
                    }});

                    $('#entity-dropdown').select2({{
                        placeholder: 'Select entities...',
                        allowClear: true,
                        closeOnSelect: false,
                        width: '100%',
                        dropdownParent: $('body')
                    }});
                }}

                function applyFilters() {{
                    if (!qtChannel) return;
                    
                    const selectedNames = $('#name-dropdown').val() || [];
                    const selectedEntities = $('#entity-dropdown').val() || [];
                    
                    qtChannel.objects.handler.handleFilters(
                        JSON.stringify({{
                            names: selectedNames,
                            entities: selectedEntities,
                        }})
                    );
                }}

                function resetFilters() {{
                    $('#name-dropdown').val(null).trigger('change');
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

    def apply_filters(self, filters):
        filtered_data = self.link_analysis_data.copy()
        selected_names = filters['names']
        selected_entities = filters['entities']

        if selected_names:
            filtered_data = filtered_data[filtered_data['Name'].isin(selected_names)]
        if selected_entities:
            filtered_data = filtered_data[filtered_data['Entity'].isin(selected_entities)]

        if filtered_data.empty:
            self.show_popup("No data matches the selected filters")
            return

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
        self.result = new_result
        self.link_analysis_data = self.filter_valid_transactions(new_result["cummalative_df"]["link_analysis_df"])

        if hasattr(self, 'link_analysis_table'):
            self.layout.removeWidget(self.link_analysis_table)
            self.link_analysis_table.deleteLater()

        self.create_dropdowns()
        self.create_table()

    def show_popup(self, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Filter Warning")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)

        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f8fafc;
                color: #1e293b;
            }
            QMessageBox QLabel {
                color: #1e293b;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)

        msg.exec()

        