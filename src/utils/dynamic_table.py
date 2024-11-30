from PyQt6.QtWidgets import QVBoxLayout, QComboBox, QCheckBox, QWidget,QLabel, QMainWindow, QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt
import json
import pandas as pd

class DynamicDataTable(QMainWindow):
    def __init__(self, df, title="",table_for="", rows_per_page=10):
        super().__init__()
        
        self.df = df
        self.filtered_df = df
        self.title = title
        self.rows_per_page = rows_per_page
        self.table_for = table_for
        self.initUI()
    
    def initUI(self):
        # Main layout
        main_layout = QVBoxLayout()

        # # Dropdowns
        # self.entity_dropdown = QComboBox(self)
        # self.entity_dropdown.addItems(self.df["Entity"].unique())
        # self.entity_dropdown.setEditable(True)
        # self.entity_dropdown.lineEdit().setPlaceholderText("Select Entities")
        # self.entity_dropdown.currentTextChanged.connect(self.filter_data)
        
        # self.name_dropdown = QComboBox(self)
        # self.name_dropdown.addItems(self.df["Name"].unique())
        # self.name_dropdown.setEditable(True)
        # self.name_dropdown.lineEdit().setPlaceholderText("Select Names")
        # self.name_dropdown.currentTextChanged.connect(self.filter_data)

        # # Add the comboboxes to the layout
        # main_layout.addWidget(self.entity_dropdown)
        # main_layout.addWidget(self.name_dropdown)
        
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
    
    def filter_data(self):
        selected_entity = self.entity_dropdown.currentText()
        selected_name = self.name_dropdown.currentText()
        
        # Apply filter based on dropdown selection
        if selected_entity and selected_name:
            self.filtered_df = self.df[
                (self.df["Entity"] == selected_entity) &
                (self.df["Name"] == selected_name)
            ]
        elif selected_entity:
            self.filtered_df = self.df[self.df["Entity"] == selected_entity]
        elif selected_name:
            self.filtered_df = self.df[self.df["Name"] == selected_name]
        else:
            self.filtered_df = self.df  # No filtering if nothing is selected
            
        # Update table
        self.create_table()
    
    def create_table(self):
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
            
            # if self.table_for == "link_analysis":
            #     row_dict['_class'] = 'highlighted' if 'highlight' in self.filtered_df.columns and row['highlight'] == 1 or i in [2,5] else ''
            # else:
            row_dict['_class'] = 'highlighted' if 'highlight' in self.filtered_df.columns and row['highlight'] == 1 else ''
            table_data.append(row_dict)
                
        
        columns = [col for col in self.filtered_df.columns if col != 'highlight']
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
                const rowsPerPage = {self.rows_per_page};
                let currentPage = 1;
                const data = {json.dumps(table_data)};
                const columns = {json.dumps([col['id'] for col in column_headers])};
                const columnAlignments = {json.dumps({col['id']: col['align'] for col in column_headers})};
                const totalPages = Math.ceil(data.length / rowsPerPage);
                
                function updateTable() {{
                    const start = (currentPage - 1) * rowsPerPage;
                    const end = start + rowsPerPage;
                    const pageData = data.slice(start, end);
                    
                    const tableBody = document.getElementById('tableBody');
                    tableBody.innerHTML = '';
                    
                    if (data.length === 0) {{
                        tableBody.innerHTML = `
                            <tr>
                                <td colspan="${{columns.length}}" class="empty-table">
                                    No data available
                                </td>
                            </tr>
                        `;
                    }} else {{
                        pageData.forEach(row => {{
                            const tr = document.createElement('tr');
                            tr.className = row['_class'];

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

                // Initial table load
                updateTable();
            </script>
        </body>
        </html>
        '''
        
        self.web_view.setHtml(html_content)
        self.web_view.setFixedHeight(800)

# # Example usage (assuming you have a DataFrame named df with 'Entity' and 'Name' columns):
# app = QApplication([])
# df = pd.DataFrame({'Entity': ['Entity1', 'Entity2', 'Entity1'], 'Name': ['Person1', 'Person2', 'Person1'], 'Amount': [100, 200, 150]})
# window = DynamicDataTable(df, title="Filtered Transactions")
# window.show()
# app.exec()
