
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QDateTime, Qt
import sys
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class SuspenseDebit(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transaction Analysis Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create the main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create QWebEngineView
        web_view = QWebEngineView()
        layout.addWidget(web_view)
        
        # Process data
        data = {
            'Date': ['03-04-2023', '06-04-2023', '06-04-2023', '11-04-2023', 
                    '12-04-2023', '17-04-2023', '20-04-2023'],
            'Description': ['clg/universaldentalsystem/iob', 'clg/ruchikanirmaljain/boi',
                          'clg/rohanpradipraut/hdf5', 'clg/nayanadandwate/bob',
                          'clg/doshimarketingcorporat/kmb', 'clg/ruchikanirmaljain/boi',
                          'clg/msnayanaashokdandwate/idfc'],
            'Amount': [4125.00, 1980.00, 54000.00, 6300.00, 11000.00, 10170.00, 3465.00]
        }
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Transaction Timeline', 'Transaction Amounts', 'Distribution of Expenses'),
            specs=[[{"type": "scatter"}, {"type": "bar"}],
                  [{"type": "pie", "colspan": 2}, None]],
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )
        
        # Add line chart
        fig.add_trace(
            go.Scatter(
                x=df['Date'],
                y=df['Amount'],
                mode='lines+markers',
                name='Transaction Amount',
                line=dict(color='#2E86C1', width=2),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
        
        # Add bar chart
        fig.add_trace(
            go.Bar(
                x=df['Date'],
                y=df['Amount'],
                name='Transaction Amount',
                marker_color='#3498DB'
            ),
            row=1, col=2
        )
        
        # Add pie chart
        fig.add_trace(
            go.Pie(
                labels=df['Description'].apply(lambda x: x.split('/')[1]),  # Use only the main part of description
                values=df['Amount'],
                hole=0.3,
                marker=dict(colors=['#2E86C1', '#3498DB', '#1ABC9C', '#16A085', 
                                  '#27AE60', '#2ECC71', '#F1C40F'])
            ),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            title_text="Transaction Analysis Dashboard",
            showlegend=False,
            height=750,
            template='plotly_white',
            annotations=[
                dict(text="Transaction Timeline", x=0.225, y=1.1, showarrow=False, font_size=16),
                dict(text="Transaction Amounts", x=0.775, y=1.1, showarrow=False, font_size=16),
                dict(text="Distribution of Expenses", x=0.5, y=0.48, showarrow=False, font_size=16)
            ]
        )
        
        # Style specific updates
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        
        # Convert the figure to HTML and display it in the QWebEngineView
        html = fig.to_html(include_plotlyjs='cdn')
        web_view.setHtml(html)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SuspenseDebit()
    window.show()
    sys.exit(app.exec())