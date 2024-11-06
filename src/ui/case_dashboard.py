from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QHeaderView, QGraphicsDropShadowEffect,
                             QScrollArea, QDialog,QPushButton,QSizePolicy)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
from .individual_dashboard import IndividualDashboard
import pandas as pd
import os
from utils.json_logic import *
from .cash_flow import CashFlowNetwork
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot
import json


class CaseDashboard(QWidget):
    def __init__(self,case_id):
        super().__init__()
        self.case_id = case_id
        self.case = load_case_data(case_id)
        print("self.case",self.case)
        self.init_ui()

    def init_ui(self):
        # Create main layout for the scroll area
        main_layout = QVBoxLayout()
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # Create a widget to hold the main content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Case Dashboard Overview")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        content_layout.addWidget(title)

        # Fund Flow Chart
        content_layout.addWidget(self.create_section_title("Fund Flow Chart"))
        content_layout.addWidget(self.create_network_graph())
        
        # Entity Distribution Chart
        # content_layout.addWidget(self.create_section_title("Entity Distribution"))
        content_layout.addWidget(self.create_entity_distribution_chart())

        # Individual Table
        content_layout.addWidget(self.create_section_title("Individual Person Table"))
        content_layout.addWidget(self.create_dummy_data_table_individual())

        # # Entity Table
        # content_layout.addWidget(self.create_section_title("Entity Table"))
        # content_layout.addWidget(self.create_dummy_data_table_entity())

        # Set content widget in scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        self.setLayout(main_layout)

    def create_section_title(self, title):
        label = QLabel(title)
        label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        label.setStyleSheet("color: #2c3e50; margin-top: 20px;")
        return label

    def create_recent_reports_table(self):
        table = QTableWidget(5, 3)
        table.setHorizontalHeaderLabels(["Date", "Report Name", "Status"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 10px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border: none;
                padding: 8px;
            }
            QTableWidget::setItem {
                text-align: center;
            }
        """)

        # Dummy data for demonstration
        recent_reports = [
            {"date": "2024-10-01", "name": "Report A", "status": "Complete"},
            {"date": "2024-10-02", "name": "Report B", "status": "Pending"},
            {"date": "2024-10-03", "name": "Report C", "status": "Complete"},
            {"date": "2024-10-04", "name": "Report D", "status": "Pending"},
            {"date": "2024-10-05", "name": "Report E", "status": "Complete"},
        ]

        for row, report in enumerate(recent_reports):
            table.setItem(row, 0, QTableWidgetItem(report['date']))
            table.setItem(row, 1, QTableWidgetItem(report['name']))
            table.setItem(row, 2, QTableWidgetItem(report['status']))

        self.add_shadow(table)
        return table

    def create_dummy_data_table_individual(self):
        data = []
        for i in range(len(self.case["individual_names"]["Name"])):
            data.append({ "Name": self.case["individual_names"]["Name"][i], "Account Number": self.case["individual_names"]["Acc Number"][i], "Pdf Path": self.case["file_names"][i]})
        headers = ["Name","Account Number","Pdf Path"]
        table_widget = PaginatedTableWidget(headers, data, rows_per_page=10,case_id=self.case_id)
        
        self.add_shadow(table_widget)
        return table_widget
    
    def create_table_individual(self):
        data = []
        for i in range(len(self.case["individual_names"]["Name"])):
            data.append({
                "ID": i+1, 
                "Name": self.case["individual_names"]["Name"][i], 
                "Account Number": self.case["individual_names"]["Acc Number"][i], 
                "Pdf Path": self.case["file_names"][i]
            })
        table_widget = IndividualTableWidget(data=data, case_id=self.case_id)
        return table_widget

    def create_dummy_data_table_entity(self):
        # Extended dummy data
        dummy_data = [
            {"id": "1", "Entity Name": "Entry A", "status": "Active"},
            {"id": "2", "Entity Name": "Entry B", "status": "Inactive"},
            {"id": "3", "Entity Name": "Entry C", "status": "Active"},
            {"id": "4", "Entity Name": "Entry D", "status": "Inactive"},
            {"id": "5", "Entity Name": "Entry E", "status": "Active"},
            {"id": "6", "Entity Name": "Entry F", "status": "Active"},
            {"id": "7", "Entity Name": "Entry G", "status": "Inactive"},
            {"id": "8", "Entity Name": "Entry H", "status": "Active"},
            {"id": "9", "Entity Name": "Entry I", "status": "Inactive"},
            {"id": "10", "Entity Name": "Entry J", "status": "Active"},
            {"id": "11", "Entity Name": "Entry K", "status": "Inactive"},
            {"id": "12", "Entity Name": "Entry L", "status": "Active"},
        ]
        
        headers = ["Date", "Entity Name", "Status"]
        table_widget = PaginatedTableWidget(headers, dummy_data,case_id=self.case_id, rows_per_page=10)
        self.add_shadow(table_widget)
        return table_widget

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

    def add_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 0)
        widget.setGraphicsEffect(shadow)

    def filter_transactions_by_frequency(self,result):
        # Get the process_df and entity frequency dataframe
        process_df = result["cummalative_df"]["process_df"]
        entity_freq_df = result["cummalative_df"]["entity_df"]
        
        # Convert entity frequency data to a dictionary for easier lookup
        # Assuming the first column is 'Entity' and second is 'Frequency'
        entity_freq_dict = dict(zip(entity_freq_df.iloc[:, 0], entity_freq_df.iloc[:, 1]))
        
        # Get base filtered dataframe with required columns and non-null entities
        filtered_df = process_df[['Name', 'Value Date', 'Debit', 'Credit', 'Entity']].dropna(subset=['Entity'])
        
        # Filter based on entity frequency
        min_frequency = 20
        filtered_df = filtered_df[filtered_df['Entity'].map(lambda x: entity_freq_dict.get(x, 0) > min_frequency)]
        
        return CashFlowNetwork(data=filtered_df)
    
    def create_network_graph(self):
        result = load_result(self.case_id)
        try:
            # df = result["cummalative_df"]["process_df"]
            # filtered_df = df[['Name', "Value Date",'Debit', 'Credit', 'Entity']].dropna(subset=['Entity'])
            # threshold = 10000
            # filtered_df = df[(df['Debit'] >= threshold) | (df['Credit'] >= threshold)]
            # return CashFlowNetwork(data=filtered_df)
            return self.filter_transactions_by_frequency(result)
        
        except Exception as e:
            print("Error",e)
            # import a excel
            df  = pd.read_excel("src/data/network_process_df.xlsx")
            filtered_df = df[['Name', "Value Date",'Debit', 'Credit', 'Entity']].dropna(subset=['Entity'])
            threshold = 10000
            filtered_df = df[(df['Debit'] >= threshold) | (df['Credit'] >= threshold)]
            return CashFlowNetwork(data=filtered_df)
        
    def create_entity_distribution_chart(self):
        result = load_result(self.case_id)
        try:
            entity_df = result["cummalative_df"]["entity_df"]
            # Remove rows where Entity is empty
            entity_df = entity_df[entity_df.iloc[:, 0] != ""]
            # Take top 10 entities by frequency
            entity_df_10 = entity_df.nlargest(10, entity_df.columns[1])
            return EntityDistributionChart(data={"piechart_data":entity_df_10,"table_data":entity_df})
        except Exception as e:
            print("Error creating entity distribution chart:", e)
            # Create dummy data if there's an error
            dummy_data = pd.DataFrame({
                'Entity': ['Entity1', 'Entity2', 'Entity3'],
                'Frequency': [10, 8, 6]
            })
            return EntityDistributionChart(data={"piechart_data":dummy_data,"table_data":dummy_data})
 

class PaginatedTableWidget(QWidget):
    def __init__(self, headers, data, case_id,rows_per_page=10):
        super().__init__()
        self.headers = headers
        self.all_data = data
        self.rows_per_page = rows_per_page
        self.current_page = 0
        self.case_id = case_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create table
        self.table = QTableWidget(self.rows_per_page, len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Disable scrollbars
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Calculate exact height needed for 10 rows plus header
        header_height = self.table.horizontalHeader().height()+20
        row_height = 35  # Set a fixed height for each row
        total_height = header_height + (row_height * self.rows_per_page)
        self.table.verticalHeader().setVisible(False)
        
        # Set row heights
        for i in range(self.rows_per_page):
            self.table.setRowHeight(i, row_height)
            
        # Set fixed table height
        self.table.setFixedHeight(total_height)
        
        # Style the table
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 10px;
                color: black;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border: none;
                padding: 8px;
            }
            QTableWidget::setItem {
                text-align: center; !important /* Center text in cells */
            }
            QTableWidget::item {
                color: black;
                padding: 5px;
            }
        """)

        # Create pagination controls
        pagination_layout = QHBoxLayout()
        
        
        
        # Previous page button
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.previous_page)
        self.prev_button.setStyleSheet(self.button_styles())
        
        self.page_label = QLabel()
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setStyleSheet("color: #34495e; font-weight: bold; font-size: 14px;")
        
        # Next page button
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setStyleSheet(self.button_styles())
        
        # Add widgets to pagination layout
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_button)
        pagination_layout.addStretch()
        
        # Add widgets to main layout
        layout.addWidget(self.table)
        layout.addLayout(pagination_layout)
        
        # Initial load
        self.update_table()
        
        # Connect cell click signal
        self.table.cellClicked.connect(self.on_cell_click)
    
    def button_styles(self):
        return """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 5px;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """
    
    def update_table(self):
        start_idx = self.current_page * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, len(self.all_data))
        
        self.table.setRowCount(self.rows_per_page)
        self.table.clearContents()
        
        for row, data in enumerate(self.all_data[start_idx:end_idx]):
            for col, key in enumerate(data.keys()):
                item = QTableWidgetItem(str(data[key]))
                
                # Center align the ID column
                if key == "ID":
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                self.table.setItem(row, col, item)
        
        total_pages = (len(self.all_data) + self.rows_per_page - 1) // self.rows_per_page
        self.page_label.setText(f"Page {self.current_page + 1} of {total_pages}")
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < total_pages - 1)
        
    def next_page(self):
        self.current_page += 1
        self.update_table()
        
    def previous_page(self):
        self.current_page -= 1
        self.update_table()
        
    def change_rows_per_page(self, value):
        self.rows_per_page = int(value)
        self.current_page = 0
        
        # Recalculate height
        header_height = self.table.horizontalHeader().height()
        row_height = 35
        total_height = header_height + (row_height * self.rows_per_page)
        
        # Update table size
        self.table.setRowCount(self.rows_per_page)
        self.table.setFixedHeight(total_height)
        
        # Reset row heights
        for i in range(self.rows_per_page):
            self.table.setRowHeight(i, row_height)
            
        self.update_table()

    # def get_latest_excel_as_df(directory_path="/src/data/cummalative_excels"):
    #     # Step 1: List all Excel files in the directory
    #     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    #     print("BASE_DIR",BASE_DIR)
    #     directory_path = os.path.join(BASE_DIR, directory_path)
    #     print("directory_path",directory_path)
    #     excel_files = [f for f in os.listdir(directory_path) if f.endswith(('.xlsx', '.xls'))]
        
    #     # Step 2: Identify the latest file based on the modification time
    #     if not excel_files:
    #         raise FileNotFoundError("No Excel files found in the specified directory.")

    #     latest_file = max(excel_files, key=lambda f: os.path.getmtime(os.path.join(directory_path, f)))
    #     latest_file_path = os.path.join(directory_path, latest_file)
        
    #     # Step 3: Load the latest Excel file into a DataFrame
    #     df = pd.read_excel(latest_file_path)
    #     return df

    def on_cell_click(self, row, column):
        start_idx = self.current_page * self.rows_per_page
        actual_row = start_idx + row
        
        if actual_row < len(self.all_data):
            if column == 1:
                name = self.all_data[actual_row]["Name"]
                print(f"Clicked on name: {name}")
                print("row",row)
                cash_flow_network = IndividualDashboard(case_id=self.case_id,name=name,row_id=row)
                # Create a new dialog and set the CashFlowNetwork widget as its central widget
                self.new_window = QDialog(self)
                self.new_window.setModal(False)  # Set the dialog as non-modal

                # Set the minimum size of the dialog
                # self.new_window.setMinimumSize(1000, 800)  # Set the minimum width and height
                # make the dialog full screen
                self.new_window.showMaximized()
                # show minimize and resize option on the Qdialog window
                self.new_window.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint)
                self.new_window.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint)
                self.new_window.setWindowFlag(Qt.WindowType.WindowCloseButtonHint)
                

                # Create a layout for the dialog and add the CashFlowNetwork widget
                layout = QVBoxLayout()
                layout.addWidget(cash_flow_network)
                self.new_window.setLayout(layout)

                # Show the new window
                self.new_window.show()

   
class EntityDistributionChart(QWidget):
    def __init__(self, data):
        super().__init__()
        self.piechart_data = data["piechart_data"]
        self.table_data = data["table_data"]
        self.current_page = 1
        self.rows_per_page = 10
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Create web view
        self.web = QWebEngineView()
        layout.addWidget(self.web)
        
        # Process data for chart
        piechart_data = {}
        for _, row in self.piechart_data.iterrows():
            piechart_data[str(row.iloc[0])] = int(row.iloc[1])

        # Process data for chart
        table_data = {}
        for _, row in self.table_data.iterrows():
            table_data[str(row.iloc[0])] = int(row.iloc[1])

        # Generate HTML content
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Entity Distribution</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.7.0/chart.min.js"></script>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                }}
                .chart-container {{
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin: 20px;
                    min-height: 400px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }}
                .header {{
                    text-align: center;
                    padding: 10px;
                    color: #2c3e50;
                    font-size: 1.2em;
                    font-weight: bold;
                }}
                .table-container {{
                    margin: 20px;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: 20px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                    border: 1px solid #e2e8f0; /* Add vertical line between cells */
                }}
                th, td {{
                    padding: 12px;
                    border-bottom: 1px solid #e2e8f0;
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                    font-weight: bold;
                    text-align: center;
                }}
                tr:hover {{
                    background-color: #f8fafc;
                }}
                .table-header {{
                    text-align: center;
                    padding: 10px;
                    color: #2c3e50;
                    font-size: 1.2em;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .pagination {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin-top: 20px;
                    gap: 10px;
                }}
                .pagination button {{
                    padding: 8px 16px;
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: bold;
                }}
                .pagination button:disabled {{
                    background-color: #bdc3c7;
                    cursor: not-allowed;
                }}
                .pagination span {{
                    font-weight: bold;
                    color: #2c3e50;
                }}
                #entityChart {{
                    max-width: 100%;
                    height: 100%;
                }}
                .tr-list td {{
                    width: 50%;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                    text-align: center;
                }}
                .key{{
                    border-right: 1px solid #e2e8f0; /* Add vertical line between cells */
                }}
            </style>
        </head>
        <body>
            <div class="header">Top 10 Entities by Transaction Frequency</div>
            <div class="chart-container">
                <canvas id="entityChart"></canvas>
            </div>
            
            <div class="table-container">
                <div class="table-header">Complete Entity Frequency List</div>
                <table>
                    <thead>
                        <tr>
                            <th>Entity</th>
                            <th>Frequency</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody">
                    </tbody>
                </table>
                <div class="pagination">
                    <button id="prevBtn" onclick="previousPage()">Previous</button>
                    <span id="pageInfo"></span>
                    <button id="nextBtn" onclick="nextPage()">Next</button>
                </div>
            </div>
            
            <script>
                const piechart_data = {json.dumps(piechart_data)};
                const table_data = {json.dumps(table_data)};
                const colors = [
                    '#10B981', '#6366F1', '#F59E0B', '#D946EF', '#0EA5E9',
                    '#34D399', '#8B5CF6', '#EC4899', '#F97316', '#14B8A6'
                ];
                
                // Pie Chart
                const ctx = document.getElementById('entityChart').getContext('2d');
                new Chart(ctx, {{
                    type: 'pie',
                    data: {{
                        labels: Object.keys(piechart_data),
                        datasets: [{{
                            data: Object.values(piechart_data),
                            backgroundColor: colors,
                            borderColor: '#ffffff',
                            borderWidth: 2
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'right',
                                labels: {{
                                    padding: 20,
                                    font: {{
                                        size: 12,
                                        family: "'Segoe UI', sans-serif"
                                    }},
                                    generateLabels: function(chart) {{
                                        const data = chart.data;
                                        const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                                        return data.labels.map((label, i) => {{
                                            const value = data.datasets[0].data[i];
                                            const percentage = ((value / total) * 100).toFixed(1);
                                            return {{
                                                text: `${{label}} (${{percentage}}%)`,
                                                fillStyle: colors[i],
                                                strokeStyle: colors[i],
                                                lineWidth: 0,
                                                hidden: false,
                                                index: i
                                            }};
                                        }});
                                    }}
                                }}
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                        const value = context.raw;
                                        const percentage = ((value / total) * 100).toFixed(1);
                                        return `${{context.label}}: ${{value}} transactions (${{percentage}}%)`;
                                    }}
                                }}
                            }}
                        }},
                        layout: {{
                            padding: 20
                        }},
                        animation: {{
                            animateScale: true,
                            animateRotate: true
                        }}
                    }}
                }});

                // Table Pagination
                const rowsPerPage = 10;
                let currentPage = 1;
                const data = Object.entries(table_data).sort((a, b) => b[1] - a[1]);
                const totalPages = Math.ceil(data.length / rowsPerPage);

                function updateTable() {{
                    const start = (currentPage - 1) * rowsPerPage;
                    const end = start + rowsPerPage;
                    const pageData = data.slice(start, end);
                    
                    const tableBody = document.getElementById('tableBody');
                    tableBody.innerHTML = '';
                    
                    pageData.forEach(([entity, frequency]) => {{
                        const row = `
                            <tr class="tr-list">
                                <td class="key">${{entity}}</td>
                                <td>${{frequency}}</td>
                            </tr>
                        `;
                        tableBody.innerHTML += row;
                    }});
                    
                    document.getElementById('pageInfo').textContent = `Page ${{currentPage}} of ${{totalPages}}`;
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
        
        self.web.setMinimumHeight(1200)  # Set minimum height instead of fixed height
        self.web.setHtml(html_content)

class IndividualTableWidget(QWidget):
    def __init__(self, data, case_id):
        super().__init__()
        self.all_data = data
        self.case_id = case_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Create web view
        self.web = QWebEngineView()
        layout.addWidget(self.web)
        
        # Convert data to format needed for JavaScript
        table_data = []
        for item in self.all_data:
            table_data.append({
                'id': item['ID'],
                'name': item['Name'],
                'account': item['Account Number'],
                'pdf': item['Pdf Path']
            })

        # Generate HTML content
        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Individual Person Table</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/qt-webengine-channel/6.4.0/qwebchannel.js"></script>
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
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: 20px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }}
                th, td {{
                    padding: 12px;
                    border-bottom: 1px solid #e2e8f0;
                    border-right: 1px solid #e2e8f0;
                }}
                th:last-child, td:last-child {{
                    border-right: none;
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                    font-weight: bold;
                }}
                tr:hover {{
                    background-color: #f8fafc;
                    cursor: pointer;
                }}
                .table-header {{
                    text-align: center;
                    padding: 10px;
                    color: #2c3e50;
                    font-size: 1.2em;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .pagination {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin-top: 20px;
                    gap: 10px;
                }}
                .pagination button {{
                    padding: 8px 16px;
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-weight: bold;
                }}
                .pagination button:disabled {{
                    background-color: #bdc3c7;
                    cursor: not-allowed;
                }}
                .pagination span {{
                    font-weight: bold;
                    color: #2c3e50;
                }}
                .tr-list td {{
                    text-align: center;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }}
                .clickable-name {{
                    color: #3498db;
                    text-decoration: underline;
                    cursor: pointer;
                }}
                .clickable-name:hover {{
                    color: #2980b9;
                }}
            </style>
        </head>
        <body>
            <div class="table-container">
                <div class="table-header">Individual Person List</div>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Account Number</th>
                            <th>PDF Path</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody">
                    </tbody>
                </table>
                <div class="pagination">
                    <button id="prevBtn" onclick="previousPage()">Previous</button>
                    <span id="pageInfo"></span>
                    <button id="nextBtn" onclick="nextPage()">Next</button>
                </div>
            </div>
            
            <script>
                let qt = null;

                const data = {table_data};
                const rowsPerPage = 10;
                let currentPage = 1;
                const totalPages = Math.ceil(data.length / rowsPerPage);

                function handleNameClick(name) {{
                    if (qt) {{
                        qt.nameClicked(name);
                    }}
                }}

                function updateTable() {{
                    const start = (currentPage - 1) * rowsPerPage;
                    const end = start + rowsPerPage;
                    const pageData = data.slice(start, end);
                    
                    const tableBody = document.getElementById('tableBody');
                    tableBody.innerHTML = '';
                    
                    pageData.forEach(item => {{
                        const row = `
                            <tr class="tr-list">
                                <td>${{item.id}}</td>
                                <td class="clickable-name" onclick="handleNameClick('${{item.name}}')">${{item.name}}</td>
                                <td>${{item.account}}</td>
                                <td>${{item.pdf}}</td>
                            </tr>
                        `;
                        tableBody.innerHTML += row;
                    }});
                    
                    document.getElementById('pageInfo').textContent = `Page ${{currentPage}} of ${{totalPages}}`;
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

                updateTable();
            </script>
        </body>
        </html>
        '''
        
        # Set minimum height for the web view
        self.web.setMinimumHeight(600)
        class Handler(QObject):
            def __init__(self, case_id, parent=None):
                super().__init__(parent)
                self.case_id = case_id
                self.parent_widget = parent

            @pyqtSlot(str)
            def nameClicked(self, name):
                dialog = QDialog(self.parent_widget)
                dialog.setWindowTitle("Individual Dashboard")
                dialog.showMaximized()
                dialog.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint)
                dialog.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint)
                dialog.setWindowFlag(Qt.WindowType.WindowCloseButtonHint)
                
                layout = QVBoxLayout()
                individual_dashboard = IndividualDashboard(case_id=self.case_id, name=name, row_id=0)
                layout.addWidget(individual_dashboard)
                dialog.setLayout(layout)
                dialog.show()
        
        # Create channel and handler
        channel = QWebChannel()
        handler = Handler(parent=self, case_id=self.case_id)
        channel.registerObject('qt', handler)
        self.web.page().setWebChannel(channel)
        
        # Load the HTML content
        self.web.setHtml(html_content)

       