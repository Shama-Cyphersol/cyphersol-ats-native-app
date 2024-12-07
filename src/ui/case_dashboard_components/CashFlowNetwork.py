from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QToolButton, QStackedWidget, QLabel, QComboBox, QSlider, QDoubleSpinBox, QSizePolicy, QApplication, QLineEdit
from PyQt6.QtGui import QIcon, QFont, QDoubleValidator
from PyQt6.QtCore import Qt, QUrl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, PathPatch, Patch, Arrow
import networkx as nx
import pandas as pd
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import sys
import io
import base64
from PyQt6.QtWebEngineWidgets import QWebEngineView
from matplotlib.lines import Line2D

class CustomNavigationToolbar(NavigationToolbar):
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)
        
        button_style = """
            QToolButton {
                background-color: #2C3E50;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px;
                margin: 1px;
            }
            QToolButton:hover {
                background-color: #34495E;
            }
            QToolButton:pressed {
                background-color: #1ABC9C;
            }
            QToolButton:checked {
                background-color: #16A085;
            }
            QToolButton:disabled {
                background-color: #95A5A6;
            }
        """
        
        for button in self.findChildren(QPushButton) + self.findChildren(QToolButton):
            button.setStyleSheet(button_style)
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

class CashFlowNetwork(QMainWindow):
    def __init__(self, data, CA_id=None):
        super().__init__()
        self.setGeometry(100, 100, 1200, 900)
        self.data = self.clean_data(data)
        self.backup_data = self.data
        self.max_frequency = self.calculate_max_frequency()
        self.G = None  # Store the networkx graph
        self.G_positions = None  # Store graph positions

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QWidget {
                background-color: #f0f0f0;
                color: #333333;
            }
            QLabel {
                color: #333333;
                font-weight: bold;
            }
            QLabel#emptyStateLabel {
                color: #666666;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton, QComboBox {
                background-color: #2C3E50;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 8px;
                min-width: 80px;
            }
            QPushButton:hover, QComboBox:hover {
                background-color: #34495E;
            }
            QPushButton:pressed {
                background-color: #1ABC9C;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid none;
                border-right: 5px solid none;
                border-top: 5px solid white;
                width: 0;
                height: 0;
                margin-right: 5px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #ffffff;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #2C3E50;
                border: none;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #34495E;
            }
        """)
        
        main_widget = QWidget()
        main_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        self.stacked_widget = QStackedWidget()
        
        graph_page = QWidget()
        graph_layout = QVBoxLayout(graph_page)
        
        controls_widget = QWidget()
        controls_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setContentsMargins(0, 0, 0, 0)
       
        self.figure = plt.figure(figsize=(12, 10))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        nav_toolbar = CustomNavigationToolbar(self.canvas, self)
   
        size_label = QLabel("Node Size:")
        self.node_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.node_size_slider.setRange(500, 5000)
        self.node_size_slider.setValue(2500)
        self.node_size_slider.valueChanged.connect(self.update_graph)
  
        controls_layout.addWidget(size_label)
        controls_layout.addWidget(self.node_size_slider)
        
        graph_layout.addWidget(controls_widget)
        graph_layout.addWidget(nav_toolbar)
        graph_layout.addWidget(self.canvas)
        
        empty_page = QWidget()
        empty_layout = QVBoxLayout(empty_page)
        
        empty_label = QLabel("Not enough data to display network graph.\nPlease ensure there are sufficient transactions with valid entities and connections.")
        empty_label.setObjectName("emptyStateLabel")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_label)
        
        reset_button = QPushButton("Reset Filters")
        reset_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        reset_button.clicked.connect(self.reset_filters)
        empty_layout.addWidget(reset_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.stacked_widget.addWidget(graph_page)
        self.stacked_widget.addWidget(empty_page)
        
        main_layout.addWidget(self.stacked_widget)
        
        self.setCentralWidget(main_widget)
        
        self.color_palette = {
            'Person': '#F1C40F',
            'Entity': '#3498DB',
            'CommonEntity': '#2ECC71'
        }
        
        self.k_value = QDoubleSpinBox()
        self.k_value.setValue(50)

        frequency_label = QLabel("Minimum Transactions:")
        self.frequency_slider = QSlider(Qt.Orientation.Horizontal)
        self.frequency_slider.setRange(1, self.max_frequency)
        self.frequency_slider.setValue((int(self.max_frequency / 3)))
        self.frequency_slider.valueChanged.connect(self.update_graph)
        self.frequency_value_label = QLabel(str(self.frequency_slider.value()))
        self.frequency_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        controls_layout.addWidget(frequency_label)
        controls_layout.addWidget(self.frequency_value_label)
        controls_layout.addWidget(self.frequency_slider)

        amount_label = QLabel("Amount:")
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter minimum amount")
        self.amount_input.setValidator(QDoubleValidator(0.0, float('inf'), 2))
        self.amount_input.textChanged.connect(self.update_graph)
        
        self.amount_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 5px;
                background-color: #ffffff;
                color: #333333;
                font-size: 12px;
            }
        """)
        controls_layout.addWidget(amount_label)
        controls_layout.addWidget(self.amount_input)
        
        self.web_view = QWebEngineView()
        self.web_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        # self.web_view.setMinimumHeight(300)
        main_layout.addWidget(self.web_view)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)  # Consistent padding
        main_layout.setSpacing(15)  # Add some space between elements
        self.canvas.mpl_connect('button_press_event', lambda event: self.on_node_click(event, self.G))



        self.setMinimumSize(800, 600)
        self.setFixedHeight(1300)
        
        if self.has_sufficient_data():
            self.stacked_widget.setCurrentIndex(0)
            self.create_graph()
        else:
            self.stacked_widget.setCurrentIndex(1)
        
    def reset_filters(self):
        self.frequency_slider.setValue(int(self.max_frequency / 3))
        self.amount_input.clear()
        self.node_size_slider.setValue(2000)
        self.data = self.backup_data
        self.update_graph()
        
    def calculate_max_frequency(self):
        """Calculate the maximum frequency of transactions for any entity"""
        entity_frequencies = self.backup_data['Entity'].value_counts()
        if len(entity_frequencies) > 0:
            return int(entity_frequencies.max())
        return 1  # Return 1 as minimum if no data
    
    def has_sufficient_data(self):
        """Check if there's enough data to create a meaningful network graph."""
        if len(self.data) < 1:
            return False
            
        # Check if we have at least one valid transaction
        valid_transactions = self.data[
            (self.data['Debit'].notna() | self.data['Credit'].notna()) &
            self.data['Entity'].notna() &
            self.data['Name'].notna()
        ]
        
        return len(valid_transactions) >= 1

    def clean_data(self, data):
        # Remove rows where Entity is null, empty, or just whitespace
        cleaned_data = data[
            data['Entity'].notna() &  # Remove null values
            (data['Entity'].str.strip() != '')  # Remove empty or whitespace-only strings
        ].copy()
        
        # Strip whitespace from Entity and Name columns
        cleaned_data['Entity'] = cleaned_data['Entity'].str.strip()
        
        return cleaned_data

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.stacked_widget.currentIndex() == 0:  # Only update if showing graph
            self.update_graph()






    def create_graph(self):
        """
        Generate the graph visualization with proper node and edge attributes,
        ensuring no missing 'color' or other key attributes.
        """
        # Clear the figure for a fresh draw
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.2)

        # Initialize the graph
        G = nx.DiGraph()
        node_sizes = {}
        edge_transaction_details = {}

        # Retrieve the entered amount
        amount_text = self.amount_input.text()
        entered_amount = float(amount_text) if amount_text else 0

        # Filter the data
        filtered_data = self.backup_data[
            (self.backup_data['Entity'].isin(
                self.backup_data['Entity'].value_counts()[
                    self.backup_data['Entity'].value_counts() >= self.frequency_slider.value()
                ].index
            )) & (
                (self.backup_data['Debit'] > entered_amount) |
                (self.backup_data['Credit'] > entered_amount)
            )
        ]

        if filtered_data.empty:
            self.stacked_widget.setCurrentIndex(1)  # Show empty state
            return

        self.data = filtered_data
        # Create a dictionary to track connections to entities
        entity_connections = {}

        # Add nodes and edges
        for _, row in self.data.iterrows():
            name = row['Name']
            entity = row['Entity']

            # Track which persons are connected to each entity
            if entity not in entity_connections:
                entity_connections[entity] = set()
            entity_connections[entity].add(name)

            # Add person node
            if name not in G:
                G.add_node(name, type='Person', size=self.node_size_slider.value() * 1.5,
                        color=self.color_palette.get('Person', 'blue'))

            # Add entity node
            if entity not in G:
                G.add_node(entity, type='Entity', size=self.node_size_slider.value(),
                        color=self.color_palette.get('Entity', 'gray'))

            # Track edge transactions
            if (name, entity) not in edge_transaction_details:
                edge_transaction_details[(name, entity)] = {'debit': 0, 'credit': 0}

            if not pd.isna(row['Debit']):
                edge_transaction_details[(name, entity)]['debit'] += row['Debit']
            if not pd.isna(row['Credit']):
                edge_transaction_details[(name, entity)]['credit'] += row['Credit']

        # Set node colors based on number of connections
        for entity, connected_persons in entity_connections.items():
            color = self.color_palette['CommonEntity'] if len(connected_persons) >= 2 else self.color_palette['Entity']
            G.nodes[entity]['color'] = color

        base_size = self.node_size_slider.value()

        if node_sizes:
            max_size = max(node_sizes.values())
            node_sizes = {k: (base_size/2) + (v / max_size) * base_size for k, v in node_sizes.items()}

        pos = nx.spring_layout(G, k=self.k_value.value())

        # Add edges
        for (start, end), details in edge_transaction_details.items():
            if details['debit'] > 0:
                G.add_edge(start, end, type='debit', amount=details['debit'])
            if details['credit'] > 0:
                G.add_edge(end, start, type='credit', amount=details['credit'])

        # Layout and drawing
        pos = nx.spring_layout(G, k=self.k_value.value() * 2)

        for node, (x, y) in pos.items():
            nx.draw_networkx_nodes(G, pos, nodelist=[node],
                                node_color=[G.nodes[node].get('color', 'black')],
                                node_size=G.nodes[node].get('size', self.node_size_slider.value()),
                                alpha=0.85, ax=ax)

            
        # Draw edges
        debit_edges = []
        credit_edges = []
        for (u, v, d) in G.edges(data=True):
            edge_color = 'red' if d.get('type') == 'debit' else 'green'
            curvature = 0.1 if edge_color == 'debit' else -0.1
            alpha = 0.6
            edge = nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color=edge_color, alpha=0.6, ax=ax, 
                                        connectionstyle=f"arc3,rad={curvature}", arrowsize=10)
            if isinstance(edge, list):
                for e in edge:
                    e.set_zorder(3)
                    if d.get('type') == 'debit':
                        debit_edges.extend(edge)
                    else:
                        credit_edges.extend(edge)
            else:
                edge.set_zorder(3)
                if d.get('type') == 'debit':
                    debit_edges.append(edge)
                else:
                    credit_edges.append(edge)

            amount = d.get('amount', 0)
    
            if amount > 0:
                 edge = nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color=edge_color, 
                                alpha=0.6, ax=ax, 
                                connectionstyle=f"arc3,rad={curvature}", 
                                arrowsize=10)
    
            # Calculate points
            x1, y1 = pos[u]
            x2, y2 = pos[v]

            # Compute edge angle and perpendicular offset
            dx = x2 - x1
            dy = y2 - y1
            angle = np.arctan2(dy, dx)

            # Place label at 1/3 point along the edge
            mid_x = x1 + dx * 0.5
            mid_y = y1 + dy * 0.5

            # Perpendicular offset
            perp_offset = 0.07
            label_x = mid_x - perp_offset * np.sin(angle)
            label_y = mid_y + perp_offset * np.cos(angle)

            # Rotate label to align with edge
            rotation = np.degrees(angle) % 360  # Adjust the rotation to keep the label upright
            if rotation > 90 and rotation <= 270:
                rotation += 180  # Flip the label if it would be upside down

            ax.text(label_x, label_y,
                    f"₹{amount:,.2f}",
                    fontsize=8,
                    color=edge_color,
                    ha='center',
                    va='center',
                    rotation=rotation,
                    bbox=dict(facecolor='white', edgecolor='none', alpha=0.7, pad=0.2))
        # Add labels
        labels = nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', 
                                       font_family='sans-serif', alpha=0.75, ax=ax)
        # edge_labels = nx.get_edge_attributes(G, 'amount')
        # edge_labels = {k: f'₹{abs(v):,.2f}' for k, v in edge_labels.items()}
        # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax, font_size=8, font_family='sans-serif')

        
        # Legend
        legend_elements = [
            Patch(facecolor=self.color_palette.get('Person', 'blue'), label='Person', alpha=0.85),
            Patch(facecolor=self.color_palette.get('Entity', 'gray'), label='Entity', alpha=0.85),
            Patch(facecolor=self.color_palette['CommonEntity'], label='Common Entity', alpha=0.85),
            Line2D([0], [0], color='green', lw=2, label='Credit'),
            Line2D([0], [0], color='red', lw=2, label='Debit'),
        ]

        ax.legend(handles=legend_elements, loc='upper center',
                bbox_to_anchor=(0.5, -0.1), ncol=4, fancybox=True, shadow=True,
                title='Legend', title_fontsize=12, fontsize=10)

        ax.axis('off')
        self.canvas.draw()
        self.G = G
        self.G_positions = pos



    
        
    def get_node_details(self, node_name):
        """
        Retrieve transaction details for a specific node
        """
        # Filter data for the specific node
        node_transactions = self.data[
            (self.data['Name'] == node_name) | (self.data['Entity'] == node_name)
        ]
        print("node_transactions ",node_transactions)
        return node_transactions
        
    def create_node_details_html(self, node_name):
        node_transactions = self.get_node_details(node_name)
        
        # Early return for empty dataset
        if node_transactions.empty:
            return f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Node Details</title>
                <style>
                    body {{ 
                        font-family: 'Arial', sans-serif; 
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background-color: #f4f6f7;
                        width: 100%;
                    }}
                    .no-data {{ 
                        color: #e74c3c; 
                        text-align: center; 
                        padding: 20px;
                        background-color: white;
                        border-radius: 10px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    }}
                </style>
            </head>
            <body>
                <div class="no-data">No transaction details found for {node_name}</div>
            </body>
            </html>
            """
        
        # Prepare HTML with enhanced styling and responsiveness
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Transaction Details for {node_name}</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    scroll-behavior: smooth;
                    
                }}
                body {{
                    background-color: white;
                    padding: 0;
                    margin: 0;

                }}
                .container {{
                    margin: 0 auto;
                    width: 100%;
                    padding: 20px;
                }}
                .header {{
                    text-align: center;
                    padding: 10px;
                    color: #2c3e50;
                    font-size: 1.2em;
                    font-weight: bold;
                    background-color: #f8fafc;
                }}
                .table-container {{
                    margin: 20px;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: 20px;
                    width: 100%;
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
                tr:nth-child(even) {{
                    background-color: #f8f9fa;
                }}
                tr:hover {{
                    background-color: #e7f1f9;
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
                @media screen and (max-width: 768px) {{
                    .container {{
                        padding: 10px;
                    }}
                    table {{
                        font-size: 0.9em;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Transaction Details for {node_name}</h2>
                </div>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Entity</th>
                                <th>Name</th>
                                <th>Description</th>
                                <th>Debit</th>
                                <th>Credit</th>
                                <th>Category</th>
                            </tr>
                        </thead>
                        <tbody id="transactionTableBody">
                            {self._generate_table_rows(node_transactions)}
                        </tbody>
                    </table>
                </div>
                <div class="pagination">
                    <button id="prevBtn" onclick="previousPage()">Previous</button>
                    <span id="pageInfo"></span>
                    <button id="nextBtn" onclick="nextPage()">Next</button>
                </div>
            </div>

            <script>
            const rowsPerPage = 10;
            let currentPage = 1;
            const transactionRows = document.querySelectorAll('#transactionTableBody tr');
            const totalPages = Math.ceil(transactionRows.length / rowsPerPage);
            const pageInfoElement = document.getElementById('pageInfo');
            const prevBtn = document.getElementById('prevBtn');
            const nextBtn = document.getElementById('nextBtn');

            function updateTable() {{
                const startIndex = (currentPage - 1) * rowsPerPage;
                const endIndex = startIndex + rowsPerPage;

                transactionRows.forEach((row, index) => {{
                    row.style.display = index >= startIndex && index < endIndex ? '' : 'none';
                }});

                pageInfoElement.textContent = `Page ${{currentPage}} of ${{totalPages}}`;
                prevBtn.disabled = currentPage === 1;
                nextBtn.disabled = currentPage === totalPages;
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

            // Initialize table
            updateTable();
            </script>
        </body>
        </html>
        """
        
        return html

    def _generate_table_rows(self, node_transactions):
        rows_html = ""
        for _, row in node_transactions.iterrows():
            rows_html += f"""
                 <tr>
                    <td>{row.get('Value Date', 'N/A')}</td>
                    <td>{row.get('Name', 'N/A')}</td>
                    <td>{row.get('Entity', 'N/A')}</td>
                    <td>{row.get('Description', 'N/A')}</td>
                    <td>₹{row.get('Debit', 0):,.2f}</td>
                    <td>₹{row.get('Credit', 0):,.2f}</td>
                    <td>{row.get('Category', 'N/A')}</td>
                </tr>
            """
        return rows_html

    def on_node_click(self, event, graph):
        """
        Handle node click events on the matplotlib canvas
        """
        if event.inaxes is None or self.G is None or self.G_positions is None:
            return
        
        # Check if click is near a node
        for node, (x, y) in self.G_positions.items():
            # Convert data coordinates to display coordinates
            display_coords = event.inaxes.transData.transform((x, y))
            click_coords = event.inaxes.transData.transform((event.xdata, event.ydata))

            # Calculate distance between click and node
            distance = np.sqrt(np.sum((display_coords - click_coords)**2))

            if distance < 30:  # Adjust threshold as needed
                # Generate node details HTML
                node_details_html = self.create_node_details_html(node)
                self.web_view.setHtml(node_details_html)
                
                # Dynamically adjust minimum height based on table rows
                node_transactions = self.get_node_details(node)
                num_rows = len(node_transactions)
                
                # Base height of 300, add 40 pixels per row up to a maximum of 600
                min_height = min(300 + (num_rows * 40), 600)
                self.web_view.setMinimumHeight(min_height)
                
                break




    def update_graph(self):
        if self.has_sufficient_data():
            self.frequency_value_label.setText(str(self.frequency_slider.value()))
            self.stacked_widget.setCurrentIndex(0)  # Show graph
            self.create_graph()
        else:
            self.stacked_widget.setCurrentIndex(1)  # Show empty state