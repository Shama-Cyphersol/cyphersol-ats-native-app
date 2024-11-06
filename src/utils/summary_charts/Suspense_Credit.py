# suspense_Credit.py
import sys
import pandas as pd
import plotly.express as px
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import tempfile
import json

class SuspenseCredit(QWidget):
    def __init__(self,data,total_transactions):
        super().__init__()
        print("SuspenseCredit",data.head())
        print("total_transactions", total_transactions)
        # Set up layout
        layout = QVBoxLayout(self)

        # Create the Plotly chart and convert to HTML
        # data = {
        #     "Value Date": ["12-04-2023", "25-04-2023", "25-04-2023", "27-04-2023", "20-05-2023", "14-07-2023", "07-08-2023", 
        #                    "11-08-2023", "19-08-2023", "18-11-2023", "21-11-2023", "15-12-2023", "15-12-2023", "18-12-2023", 
        #                    "17-01-2024", "13-03-2024", "14-03-2024", "14-03-2024", "18-03-2024", "25-03-2024"],
        #     "Description": ["clg/chandrakantlaxman", "clg/pradeepssharma", "clg/naishadhjdalal", "clg/antketdeelip", "clg/rgsynthetics",
        #                     "clg/mohiniikapoor", "acxfrfromgl05051to05066", "clg/rgsynthetics", "clg/babunidoni", "clg/neerajmishra",
        #                     "clg/pranitaparagraut", "clg/savitameshr", "clg/vijayvitthalrao", "trfrfrom:sunilmarutishelke", 
        #                     "clg/vijaykarkhile", "clg/shivdastrbak", "clg/jitendrabubhai", "clg/apexakumarinatvarlal", 
        #                     "clg/kbgeneral", "clg/madhusudan"],
        #     "Credit": [25000, 325000, 55000, 50000, 410000, 200000, 5192.90, 180000, 500000, 450000, 95000, 100000, 50000, 25000, 
        #                225000, 300000, 100000, 100000, 20000, 250000]
        # }

        
        df = pd.DataFrame(data)
        # Swap x and y to display 'Credit' on x-axis and 'Description' on y-axis
        fig = px.bar(df, x='Credit', y='Description', color='Credit',
                     color_continuous_scale='Viridis', title='Credit Transactions')
        
        fig.update_layout(xaxis_title="Credit Amount (₹)", yaxis_title="Description", 
                          yaxis_tickangle=0, template="plotly_white")
        
        # Save the chart as an HTML file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        fig.write_html(temp_file.name)

        # Set up QWebEngineView to display the HTML chart
        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl.fromLocalFile(temp_file.name))
        self.web_view.setFixedHeight(700)

        layout.addWidget(self.web_view)
        self.create_html_table(layout, data)

    def create_html_table(self, layout, data):
        web_view = QWebEngineView()
        
        table_data = [
            {
                'date': row["Value Date"].strftime("%d-%m-%Y"),
                'description': row["Description"],
                'credit': f"₹{row['Credit']:.2f}",
            }
            for _, row in data.iterrows()
        ]

        html_content = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Suspense Credit Details</title>
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
                    # box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }}
                .table-container table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                .table-container th, .table-container td {{
                    padding: 10px;
                    text-align: center;
                    border-bottom: 1px solid #ddd;
                }}
                .table-container th {{
                    background-color: #3498db;
                    color: white;
                    font-weight: bold;
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
                .description-column {{
                    text-align: left;
                }}
                tr:hover {{
                    background-color: #f8fafc;
                }}
                
            </style>
        </head>
        <body>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Description</th>
                            <th>Credit</th>
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
                const rowsPerPage = 10;
                let currentPage = 1;
                const data = {json.dumps(table_data)};
                const totalPages = Math.ceil(data.length / rowsPerPage);

                function updateTable() {{
                    const start = (currentPage - 1) * rowsPerPage;
                    const end = start + rowsPerPage;
                    const pageData = data.slice(start, end);
                    
                    const tableBody = document.getElementById('tableBody');
                    tableBody.innerHTML = '';
                    
                    pageData.forEach(row => {{
                        const tr = `
                            <tr>
                                <td>${{row.date}}</td>
                                <td>${{row.description}}</td>
                                <td>${{row.credit}}</td>
                            </tr>
                        `;
                        tableBody.innerHTML += tr;
                    }});
                    
                    document.getElementById('pageInfo').textContent = `Page ${{currentPage}} of ${{totalPages}}`;
                    document.getElementById('prevButton').disabled = currentPage === 1;
                    document.getElementById('nextButton').disabled = currentPage === totalPages;
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
        
        web_view.setHtml(html_content)
        web_view.setMinimumHeight(600)
        layout.addWidget(web_view)
