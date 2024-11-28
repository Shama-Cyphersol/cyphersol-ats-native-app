from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QToolButton, QStackedWidget, QLabel, QComboBox, QSlider, QDoubleSpinBox, QSizePolicy, QApplication
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, PathPatch, Patch, Arrow
import networkx as nx
import pandas as pd
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import sys

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
        # print("data - ",self.data.head())
        self.max_frequency = self.calculate_max_frequency()

        # Add style for the empty state message
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
        
        # Create stacked widget to switch between graph and empty state
        self.stacked_widget = QStackedWidget()
        
        # Create graph page
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
        self.node_size_slider.setValue(2000)
        self.node_size_slider.valueChanged.connect(self.update_graph)
  
        controls_layout.addWidget(size_label)
        controls_layout.addWidget(self.node_size_slider)
        
        graph_layout.addWidget(controls_widget)
        graph_layout.addWidget(nav_toolbar)
        graph_layout.addWidget(self.canvas)
        
        # Create empty state page
        empty_page = QWidget()
        empty_layout = QVBoxLayout(empty_page)
        
        empty_label = QLabel("Not enough data to display network graph.\nPlease ensure there are sufficient transactions with valid entities and connections.")
        empty_label.setObjectName("emptyStateLabel")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(empty_label)
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(graph_page)
        self.stacked_widget.addWidget(empty_page)
        
        main_layout.addWidget(self.stacked_widget)
        
        self.setCentralWidget(main_widget)
        
        self.color_palette = {
            'Person': '#F1C40F',  # Yellow
            'Entity': '#3498DB',  # Blue
            'CommonEntity': '#2ECC71'  # Green
        }
        
        self.k_value = QDoubleSpinBox()
        self.k_value.setValue(50)

        # Add frequency slider
        frequency_label = QLabel("Minimum Transactions:")
        self.frequency_slider = QSlider(Qt.Orientation.Horizontal)
        self.frequency_slider.setRange(1, self.max_frequency)
        self.frequency_slider.setValue((int(self.max_frequency/3)))
        self.frequency_slider.valueChanged.connect(self.update_graph)
        self.frequency_value_label = QLabel(str(self.frequency_slider.value()))
        self.frequency_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        controls_layout.addWidget(frequency_label)
        controls_layout.addWidget(self.frequency_value_label)
        controls_layout.addWidget(self.frequency_slider)

        self.setMinimumSize(800, 600)
        self.setFixedHeight(1000)
        
        # Check if we have enough data before creating the graph
        if self.has_sufficient_data():
            self.stacked_widget.setCurrentIndex(0)  # Show graph
            self.create_graph()
        else:
            self.stacked_widget.setCurrentIndex(1)  # Show empty state
        
        
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
        self.figure.clear()
        
        # Create main axes for the graph
        ax = self.figure.add_subplot(111)
        self.figure.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.2)

        G = nx.DiGraph()

        node_sizes = {}
        edge_weights = {}

        # Filter the data based on the frequency slider value
        self.data = self.backup_data[self.backup_data['Entity'].isin(
            self.backup_data['Entity'].value_counts()[self.backup_data['Entity'].value_counts() >= self.frequency_slider.value()].index
        )]


        # First pass: Add all nodes and edges
        unique_names = self.data['Name'].unique()
        name_sizes = {name: self.node_size_slider.value() * 1.5 for name in unique_names}
        name_colors = {name: self.color_palette['Person'] for name in unique_names}

        # Create a dictionary to track connections to entities
        entity_connections = {}

        for _, row in self.data.iterrows():
            name = row['Name']
            entity = row['Entity']
            
            # Track which persons are connected to each entity
            if entity not in entity_connections:
                entity_connections[entity] = set()
            entity_connections[entity].add(name)

            if name not in G:
                G.add_node(name, type='Person', size=name_sizes.get(name, self.node_size_slider.value()), 
                        color=name_colors.get(name, self.color_palette['Person']))
            if entity not in G:
                G.add_node(entity, type='Entity', size=self.node_size_slider.value())

            if not pd.isna(row['Debit']):
                G.add_edge(name, entity, amount=-row['Debit'], weight=row['Debit'], transaction_type='debit')
                edge_weights[(name, entity)] = row['Debit']
                node_sizes[name] = node_sizes.get(name, 0) + row['Debit']
                node_sizes[entity] = node_sizes.get(entity, 0) + row['Debit']
            if not pd.isna(row['Credit']):
                G.add_edge(entity, name, amount=row['Credit'], weight=row['Credit'], transaction_type='credit')
                edge_weights[(entity, name)] = row['Credit']
                node_sizes[name] = node_sizes.get(name, 0) + row['Credit']
                node_sizes[entity] = node_sizes.get(entity, 0) + row['Credit']

        # Set node colors based on number of connections
        for entity, connected_persons in entity_connections.items():
            color = self.color_palette['CommonEntity'] if len(connected_persons) >= 2 else self.color_palette['Entity']
            G.nodes[entity]['color'] = color

        base_size = self.node_size_slider.value()

        if node_sizes:
            max_size = max(node_sizes.values())
            node_sizes = {k: (base_size/2) + (v / max_size) * base_size for k, v in node_sizes.items()}

        pos = nx.spring_layout(G, k=self.k_value.value())

        # Draw nodes
        person_nodes = []
        entity_nodes = []
        common_entity_nodes = []
        for node, (x, y) in pos.items():
            node_type = G.nodes[node]['type']
            if node_type == 'Person':
                color = G.nodes[node]['color']
            else:
                color = G.nodes[node]['color']
            
            size = G.nodes[node]['size'] if node_type == 'Person' else node_sizes.get(node, base_size)
            node_collection = nx.draw_networkx_nodes(G, pos, nodelist=[node], node_color=[color], 
                                                   node_size=size, alpha=0.85, ax=ax)
            node_collection.set_zorder(2 if node_type == 'Person' else 1)
            
            if node_type == 'Person':
                person_nodes.append(node_collection)
            elif color == self.color_palette['CommonEntity']:
                common_entity_nodes.append(node_collection)
            else:
                entity_nodes.append(node_collection)

        # Draw edges
        debit_edges = []
        credit_edges = []
        for (u, v, d) in G.edges(data=True):
            edge_color = 'red' if d.get('transaction_type') == 'debit' else 'green'
            alpha = 0.6
            edge = nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color=edge_color, alpha=alpha, ax=ax, 
                                        connectionstyle="arc3,rad=0.1", arrowsize=20)
            if isinstance(edge, list):
                for e in edge:
                    e.set_zorder(3)
                    if d.get('transaction_type') == 'debit':
                        debit_edges.extend(edge)
                    else:
                        credit_edges.extend(edge)
            else:
                edge.set_zorder(3)
                if d.get('transaction_type') == 'debit':
                    debit_edges.append(edge)
                else:
                    credit_edges.append(edge)

        # Add labels
        labels = nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', 
                                       font_family='sans-serif', alpha=0.75, ax=ax)
        
        # Create legend elements
        legend_elements = [
            Patch(facecolor=self.color_palette['Person'], label='Statement Person', alpha=0.85),
            Patch(facecolor=self.color_palette['Entity'], label='Entity', alpha=0.85),
            Patch(facecolor=self.color_palette['CommonEntity'], label='Common Entity', alpha=0.85),
            Patch(facecolor='red', label='Debit Transaction', alpha=0.6),
            Patch(facecolor='green', label='Credit Transaction', alpha=0.6),
        ]

        # Add the legend
        ax.legend(handles=legend_elements, 
                 loc='upper center',
                 bbox_to_anchor=(0.5, -0.1),
                 ncol=5,
                 fancybox=True,
                 shadow=True,
                 title='Network Elements',
                 title_fontsize=12,
                 fontsize=10)

        ax.axis('off')
        self.canvas.draw()

    def update_graph(self):
        if self.has_sufficient_data():
            self.frequency_value_label.setText(str(self.frequency_slider.value()))
            self.stacked_widget.setCurrentIndex(0)  # Show graph
            self.create_graph()
        else:
            self.stacked_widget.setCurrentIndex(1)  # Show empty state

            