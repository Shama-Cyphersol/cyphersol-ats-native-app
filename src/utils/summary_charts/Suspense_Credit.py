# suspense_Credit.py
import sys
import pandas as pd
import plotly.express as px
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import tempfile

class SuspenseCredit(QWidget):
    def __init__(self):
        super().__init__()
        
        # Set up layout
        layout = QVBoxLayout(self)

        # Create the Plotly chart and convert to HTML
        data = {
            "Value Date": ["12-04-2023", "25-04-2023", "25-04-2023", "27-04-2023", "20-05-2023", "14-07-2023", "07-08-2023", 
                           "11-08-2023", "19-08-2023", "18-11-2023", "21-11-2023", "15-12-2023", "15-12-2023", "18-12-2023", 
                           "17-01-2024", "13-03-2024", "14-03-2024", "14-03-2024", "18-03-2024", "25-03-2024"],
            "Description": ["clg/chandrakantlaxman", "clg/pradeepssharma", "clg/naishadhjdalal", "clg/antketdeelip", "clg/rgsynthetics",
                            "clg/mohiniikapoor", "acxfrfromgl05051to05066", "clg/rgsynthetics", "clg/babunidoni", "clg/neerajmishra",
                            "clg/pranitaparagraut", "clg/savitameshr", "clg/vijayvitthalrao", "trfrfrom:sunilmarutishelke", 
                            "clg/vijaykarkhile", "clg/shivdastrbak", "clg/jitendrabubhai", "clg/apexakumarinatvarlal", 
                            "clg/kbgeneral", "clg/madhusudan"],
            "Credit": [25000, 325000, 55000, 50000, 410000, 200000, 5192.90, 180000, 500000, 450000, 95000, 100000, 50000, 25000, 
                       225000, 300000, 100000, 100000, 20000, 250000]
        }
        
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
        layout.addWidget(self.web_view)
