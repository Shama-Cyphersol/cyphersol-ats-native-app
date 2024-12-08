from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QMessageBox, QApplication, QMainWindow)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot
import json
import sys
import pandas as pd
from PyQt6.QtWebEngineCore import QWebEnginePage
from ...utils.refresh import fund_tracking_get_funds

class DynamicDataTableRowClick(QMainWindow):
    def __init__(self, df, handle_row_click,title="",table_for="", rows_per_page=10):
        super().__init__()
        
        self.df = df
        self.filtered_df = df
        self.handle_row_click = handle_row_click
        self.title = title
        self.rows_per_page = rows_per_page
        self.table_for = table_for
        self.initUI()
    
    def initUI(self):
        # Main layout
        main_layout = QVBoxLayout()

        # Web view for table
        self.web_view = QWebEngineView()
        main_layout.addWidget(self.web_view)
        
        # Create a widget to hold the layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        # Initial table display
        self.create_table()
        return container
    
    def create_table(self):
        # Create a handler for row clicks
        class Handler(QObject):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.widget = parent

            @pyqtSlot(str)
            def handleRowClick(self, row_json):
                row_data = json.loads(row_json)
                self.widget.on_row_clicked(row_data)

        # Ensure web channel is set up correctly
        self.channel = QWebChannel()
        self.handler = Handler(self)
        
        # Important: register the handler BEFORE setting the web channel
        self.channel.registerObject('handler', self.handler)
        
        # Set the web channel on the page
        self.web_view.page().setWebChannel(self.channel)

        # Update table as before
        self.update_table()

    def update_table(self):
        table_data = []
        for i, (_, row) in enumerate(self.filtered_df.iterrows()):
            row_dict = {}
            for column in self.filtered_df.columns:
                value = row[column]
                
                if pd.isna(value):
                    row_dict[column] = ""
                elif isinstance(value, (int, float)):
                    row_dict[column] = f"{float(value):,.2f}" if column.lower() in ['debit', 'credit', 'balance', 'amount'] else str(value)
                elif isinstance(value, pd.Timestamp):
                    row_dict[column] = value.strftime('%Y-%m-%d')
                else:
                    row_dict[column] = str(value)
            
            table_data.append(row_dict)
                
        
        columns = [col for col in self.filtered_df.columns if col not in ['row_id']]
        # Handle empty DataFrame case
        if len(self.filtered_df) == 0:
            # Default all alignments to center if no data is present
            column_headers = [{'id': col, 'name': col.replace('_', ' ').title(), 'align': 'center'} for col in columns]
        else:
            # Original logic for non-empty DataFrame
            column_headers = [
                {
                    'id': col, 
                    'name': col.replace('_', ' ').title(), 
                    'align': 'left' if isinstance(self.filtered_df[col].iloc[0], str) else 'center'
                } 
                for col in columns
            ]        
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Link Analysis Filters</title>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/css/select2.min.css" rel="stylesheet" />
            <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.13/js/select2.min.js"></script>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <title>{self.title}</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}
                .table-container {{
                    margin: 20px;
                    background: white;
                    border-radius: 10px;
                    padding: 20px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    overflow-x: auto;

                }}
                .table-header {{
                    text-align: center;
                    padding: 15px;
                    color: #2c3e50;
                    font-size: 1.2rem;
                    font-weight: bold;
                    margin-bottom: 15px;
                    border-bottom: 2px solid #eef2f7;
                    visibility: {'hidden' if self.title=="" else 'visible'};
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                    min-width: 100%;
                }}
                th, td {{
                    padding: 12px;
                    border-bottom: 1px solid #e2e8f0;
                    min-width:150px
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                    font-weight: bold;
                    position: sticky;
                    top: 0;
                    padding: 12px;
                }}
                tr:hover {{
                    background-color: #f8fafc;
                    transition: background-color 0.2s ease;
                    cursor: pointer;
                }}
                .text-left {{
                    text-align: left;
                }}
                .text-center {{
                    text-align: center;
                }}
                .pagination {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-top: 20px;
                    padding: 10px 0;
                    border-top: 1px solid #e2e8f0;
                }}
                .pagination-controls {{
                    display: flex;
                    gap: 10px;
                    align-items: center;
                }}
                .pagination button {{
                    padding: 8px 16px;
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: bold;
                    transition: background-color 0.2s ease;
                }}
                .pagination button:hover {{
                    background-color: #2980b9;
                }}
                .pagination button:disabled {{
                    background-color: #bdc3c7;
                    cursor: not-allowed;
                }}
                .pagination-info {{
                    font-weight: bold;
                    color: #333333;
                }}
                .empty-table {{
                    text-align: center;
                    padding: 40px;
                    color: #666;
                    font-style: italic;
                }}
                .highlighted {{
                    background-color: #ffe6e6;
                }}
                .highlighted:hover {{
                    background-color: #ffe0e9;
                }}
                
            </style>
        </head>
        <body>
            <div class="table-container">
                <div class="table-header">{self.title}</div>
                <table>
                    <thead>
                        <tr>
                            {
                                ''.join([
                                    f'<th class="{"text-left" if col["align"] == "left" else "text-center"}">{col["name"]}</th>'
                                    for col in column_headers
                                ])
                            }
                        </tr>
                    </thead>
                    <tbody id="tableBody">
                    </tbody>
                </table>
                <div class="pagination">
                    <div class="pagination-info">
                        <span id="totalRecords"></span>
                    </div>
                    <div class="pagination-controls">
                        <button id="prevBtn" onclick="previousPage()">Previous</button>
                        <span id="pageInfo"></span>
                        <button id="nextBtn" onclick="nextPage()">Next</button>
                    </div>
                </div>
            <script>
                let qtChannel = null;
                
                function initWebChannel() {{
                    // Robust check for Qt WebChannel availability
                    if (typeof qt !== 'undefined' && qt.webChannelTransport) {{
                        try {{
                            new QWebChannel(qt.webChannelTransport, function(channel) {{
                                qtChannel = channel;
                                console.log("Web channel initialized successfully");
                            }});
                        }} catch (error) {{
                            console.error("Web channel initialization error:", error);
                        }}
                    }} else {{
                        console.warn("Qt WebChannel not available");
                    }}
                }}

                const rowsPerPage = {self.rows_per_page};
                let currentPage = 1;
                const data = {json.dumps(table_data)};
                const columns = {json.dumps([col['id'] for col in column_headers])};
                const columnAlignments = {json.dumps({col['id']: col['align'] for col in column_headers})};
                const totalPages = Math.ceil(data.length / rowsPerPage);
                
                function handleRowClick(rowIndex) {{
                    const rowData = data[rowIndex];
                    if (qtChannel) {{
                        qtChannel.objects.handler.handleRowClick(JSON.stringify(rowData));
                    }}
                }}
                
                function updateTable() {{
                    const start = (currentPage - 1) * rowsPerPage;
                    const end = start + rowsPerPage;
                    const pageData = data.slice(start, end);
                    
                    const tableBody = document.getElementById('tableBody');
                    tableBody.innerHTML = '';
                    
                    if (data.length === 0) {{
                        tableBody.innerHTML = `
                            <tr >
                                <td colspan="${{columns.length}}" class="empty-table">
                                    No data available
                                </td>
                            </tr>
                        `;
                    }} else {{
                        pageData.forEach((row,index )=> {{
                            const tr = document.createElement('tr');
                            tr.className = row['_class'];
                            tr.onclick = () => handleRowClick(index);

                            columns.forEach(column => {{
                                const td = document.createElement('td');
                                td.className = columnAlignments[column] === 'left' ? 'text-left' : 'text-center';
                                td.textContent = row[column] || '';
                                tr.appendChild(td);
                            }});
                            
                            tableBody.appendChild(tr);
                        }});
                    }}

                   
                    document.getElementById('pageInfo').textContent = 
                        `Page ${{currentPage}} of ${{totalPages}}`;
                    document.getElementById('totalRecords').textContent = 
                        `Total Records: ${{data.length}}`;
                    document.getElementById('prevBtn').disabled = currentPage === 1;
                    document.getElementById('nextBtn').disabled = currentPage === totalPages;
                }}

                function nextPage() {{
                    if (currentPage < totalPages) {{
                        currentPage++;
                        updateTable();
                    }}
                }}

                function previousPage() {{
                    if (currentPage > 1) {{
                        currentPage--;
                        updateTable();
                    }}
                }}

                $(document).ready(function() {{
                    initWebChannel();
                    updateTable();
                }});

            </script>
        </body>
        </html>
        '''
        
        self.web_view.setHtml(html_content)
        self.web_view.setMinimumHeight(600)
   
    def on_row_clicked(self, row_data):
        self.handle_row_click(row_data)
        # msg = QMessageBox(self)
        # msg.setIcon(QMessageBox.Icon.Information)
        # msg.setWindowTitle("Row Clicked")
        
        # details = "\n".join([f"{key}: {value}" for key, value in row_data.items()])
        # msg.setText("Transaction Details:\n" + details)
        # msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        
        # msg.setStyleSheet("""
        #     QMessageBox {
        #         background-color: #f8fafc;
        #         color: #1e293b;
        #     }
        #     QMessageBox QLabel {
        #         color: #1e293b;
        #         font-size: 14px;
        #         padding: 10px;
        #     }
        #     QPushButton {
        #         background-color: #3498db;
        #         color: white;
        #         border: none;
        #         border-radius: 4px;
        #         padding: 8px 16px;
        #         min-width: 80px;
        #     }
        #     QPushButton:hover {
        #         background-color: #2980b9;
        #     }
        # """)

        # msg.exec()
    
class FundTrackingComponent(QWidget):
    def __init__(self, case_id, process_df, parent=None):
        super().__init__(parent)
        self.case_id = case_id
        self.process_df = process_df
        # add a new col in the process_df to store the row_id
        self.process_df["row_id"] = self.process_df.index
        self.initial_transactions_table_data = pd.DataFrame()

        self.setWindowTitle("Fund Tracking")
        self.layout = QVBoxLayout(self)
        # self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setContentsMargins(0,0,0,0)
        # self.layout.setSpacing(10)
        self.layout.setSpacing(0)

        self.create_filters()
        self.create_table()

        self.setLayout(self.layout)
    
    def create_filters(self):
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

        names = sorted(self.process_df['Name'].dropna().unique())
        categories = sorted(self.process_df['Category'].dropna().unique())

        name_options = '\n'.join([f'<option value="{name}">{name}</option>' for name in names])
        categories_options = '\n'.join([f'<option value="{category}">{category}</option>' for category in categories])

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
                /* CSS styles */
                :root {{
                    --primary-blue: #3498db;
                    --accent-red: #b82214;
                    --border-color: #e2e8f0;
                    --text-color: #1e293b;
                    --background: white;
                }}

                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: var(--background);
                    margin: 20px;
                    padding: 20px;
                }}

                .filters-container {{
                    background: white;
                    border: 1px solid var(--border-color);
                    border-radius: 0.375rem;
                    padding: 1rem;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                }}

                .fields-container {{
                    display: flex;
                    justify-content: space-between;
                    gap: 1rem;
                    margin-bottom: 1rem;
                }}

                .filter-group {{
                    flex: 1;
                    min-width: 0;
                }}

                label {{
                    display: block;
                    font-size: 0.875rem;
                    font-weight: 500;
                    color: var(--text-color);
                    margin-bottom: 0.5rem;
                }}

                #transaction-date,
                .select2-container--default .select2-selection--single {{
                    width: 100%;
                    padding: 0.5rem;
                    border: 1px solid var(--border-color);
                    border-radius: 0.375rem;
                    font-size: 0.875rem;
                    box-sizing: border-box;
                    background-color: white;
                    appearance: none;
                }}

                #transaction-date::-webkit-calendar-picker-indicator {{
                    cursor: pointer;
                    filter: opacity(0.6);
                    transition: filter 0.2s ease-in-out;
                }}

                #transaction-date::-webkit-calendar-picker-indicator:hover {{
                    filter: opacity(1);
                }}

                #transaction-date:focus,
                .select2-container--default .select2-selection--single:focus {{
                    outline: none;
                    border-color: var(--primary-blue);
                    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
                }}

                .select2-container--default .select2-selection--single {{
                    height: auto;
                }}

                .select2-container--default .select2-selection--single .select2-selection__rendered {{
                    line-height: 1.5;
                    padding-left: 0;
                }}

                .select2-container--default .select2-selection--single .select2-selection__arrow {{
                    height: 100%;
                }}

                .buttons-container {{
                    display: flex;
                    gap: 1rem;
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
                    background: #2978b5;
                }}

                .reset-btn {{
                    background: var(--accent-red);
                    color: white;
                }}

                .reset-btn:hover {{
                    background: #991b1b;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="filters-container">
            <div class="filter-groups">
                <div class="fields-container">
                    <div class="filter-group">
                        <label for="transaction-date">Transaction Date</label>
                        <input type="date" id="transaction-date" />
                    </div>
                    <div class="filter-group">
                        <label for="name-dropdown">Names</label>
                        <select id="name-dropdown" class="select2">
                            {name_options}
                        </select>
                    </div>
                    <div class="filter-group">
                        <label for="category-dropdown">Categories</label>
                        <select id="category-dropdown" class="select2">
                            {categories_options}
                        </select>
                    </div>
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
                        placeholder: 'Select name...',
                        allowClear: true,
                        closeOnSelect: true,
                        width: '100%',
                        dropdownParent: $('.filters-container')
                    }});

                    $('#category-dropdown').select2({{
                        placeholder: 'Select category...',
                        allowClear: true,
                        closeOnSelect: true,
                        width: '100%',
                        dropdownParent: $('body')
                    }});
                }}

                function applyFilters() {{
                    if (!qtChannel) return;
                    
                    const selectedNames = $('#name-dropdown').val() || [];
                    const selectedCategory = $('#category-dropdown').val() || [];
                    const transactionDate = $('#transaction-date').val();
                    
                    qtChannel.objects.handler.handleFilters(
                        JSON.stringify({{
                            name: selectedNames,
                            date: transactionDate,
                            category: selectedCategory,
                        }})
                    );
                }}

                function resetFilters() {{
                    $('#name-dropdown').val(null).trigger('change');
                    $('#category-dropdown').val(null).trigger('change');
                    $('#transaction-date').val('');
                    
                    if (qtChannel) {{
                        qtChannel.objects.handler.handleFilters(
                            JSON.stringify({{
                                name: [],
                                date: '',
                                category: [],
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
        self.web_view.setFixedHeight(250)  
        self.layout.addWidget(self.web_view)

    def create_table(self):
        self.initial_transactions_table = DynamicDataTableRowClick(self.initial_transactions_table_data,self.handle_row_click,title="Select a Transaction")
        self.layout.addWidget(self.initial_transactions_table)

    # def update_table(self, df):
    #     table_data = []
    #     for _, row in df.iterrows():
    #         row_dict = {col: str(row[col]) if pd.notna(row[col]) else "" for col in df.columns}
    #         table_data.append(row_dict)

    #     columns = df.columns.tolist()
    #     html_content = f'''
    #     <!DOCTYPE html>
    #     <html>
    #     <head>
    #         <meta charset="UTF-8">
    #         <meta name="viewport" content="width=device-width, initial-scale=1.0">
    #         <title>Fund Tracking Transactions</title>
    #         <style>
    #             * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
    #             .table-container {{ margin: 20px; background: white; border-radius: 10px; padding: 20px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    #             table {{ width: 100%; border-collapse: collapse; }}
    #             th, td {{ padding: 12px; border-bottom: 1px solid #e2e8f0; }}
    #             th {{ background-color: #3498db; color: white; }}
    #             tr:hover {{ background-color: #f0f4f8; cursor: pointer; }}
    #             .empty-table {{ text-align: center; padding: 40px; color: #666; }}
    #         </style>
    #     </head>
    #     <body>
    #         <div class="table-container">
    #             <table>
    #                 <thead>
    #                     <tr>
    #                         {''.join([f'<th>{col}</th>' for col in columns])}
    #                     </tr>
    #                 </thead>
    #                 <tbody id="tableBody">
    #                 </tbody>
    #             </table>
    #         </div>
    #         <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    #         <script>
    #             let qtChannel = null;

    #             function initWebChannel() {{
    #                 if (typeof qt !== 'undefined' && qt.webChannelTransport) {{
    #                     new QWebChannel(qt.webChannelTransport, function(channel) {{
    #                         qtChannel = channel;
    #                     }});
    #                 }}
    #             }}

    #             const data = {json.dumps(table_data)};
    #             const columns = {json.dumps(columns)};
                
    #             function updateTable() {{
    #                 const tableBody = document.getElementById('tableBody');
    #                 print("hey")
    #                 tableBody.innerHTML = '';
    #                 data.forEach((row, index) => {{
    #                     const tr = document.createElement('tr');
    #                     tr.onclick = () => handleRowClick(index);
    #                     columns.forEach(col => {{
    #                         const td = document.createElement('td');
    #                         td.textContent = row[col] || '';
    #                         tr.appendChild(td);
    #                     }});
    #                     tableBody.appendChild(tr);
    #                 }});
    #             }}

    #             function handleRowClick(rowIndex) {{
    #                 const rowData = data[rowIndex];
    #                 print("hey2")
    #                 if (qtChannel) {{
    #                     qtChannel.objects.handler.handleRowClick(JSON.stringify(rowData));
    #                 }}
    #             }}

    #             initWebChannel(); // Call to initialize the web channel
    #             updateTable(); // Call to update the table
    #         </script>
    #     </body>
    #     </html>
    #     '''
        
    #     self.table_web_view.setHtml(html_content)
    #     self.table_web_view.setFixedHeight(400)

    def update_table(self, df):
        self.initial_transactions_table_data = df

        if hasattr(self, 'initial_transactions_table'):
            self.layout.removeWidget(self.initial_transactions_table)
            self.initial_transactions_table.deleteLater()

        self.create_table()

    def apply_filters(self, filters):
        filtered_data = self.process_df.copy()
        
        selected_name = filters['name']
        selected_category = filters['category']
        selected_date = filters['date']

        if selected_name:
            filtered_data = filtered_data[filtered_data['Name'].isin([selected_name])]
        if selected_category:
            filtered_data = filtered_data[filtered_data['Category'].isin([selected_category])]
        if selected_date:
            filtered_data = filtered_data[filtered_data['Value Date'] == selected_date]

        if filtered_data.empty:
            self.show_popup("No data matches the selected filters")
            self.update_table(pd.DataFrame())
            return
        self.update_table(filtered_data)    
    def on_row_clicked(self, row_data):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Row Clicked")
        
        details = "\n".join([f"{key}: {value}" for key, value in row_data.items()])
        msg.setText("Transaction Details:\n" + details)
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
                background-color: #2980b9;
            }
        """)

        msg.exec()
    
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
                background-color: #2980b9;
            }
        """)

        msg.exec()

    def handle_row_click(self, row_data):
        print("row_data",row_data)
        row_id = int(row_data['row_id'])
        data = fund_tracking_get_funds(self.process_df,row_id)
        print("data ", data)
        self.add_new_table(data,row_id)
        
    
    def add_new_table(self,df,row_id):
        new_transactions_table = DynamicDataTableRowClick(df,self.handle_row_click,title="Forward Transactions")
        self.layout.addWidget(new_transactions_table)
        # new_transactions_table.show()

# Example usage
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Sample DataFrame for demonstration
    sample_df = pd.DataFrame({
        'Name': ['John Doe', 'Jane Smith', 'Alice Johnson'],
        'Category': ['Salary', 'Investment', 'Expense'],
        'Value Date': ['2023-06-15', '2023-06-20', '2023-06-25'],
        'Amount': [5000.00, 10000.00, 500.00]
    })
    
    fund_tracking = FundTrackingComponent(case_id='test_case', process_df=sample_df)
    fund_tracking.show()
    
    sys.exit(app.exec())