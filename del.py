from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,QToolButton, QStackedWidget, QLabel, QComboBox, QSlider,QDoubleSpinBox
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np

class CustomNavigationToolbar(NavigationToolbar):
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)
        
        # Define the style for all toolbar buttons
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
        
        # Apply the style to all buttons in the toolbar
        for button in self.findChildren(QPushButton) + self.findChildren(QToolButton):
            button.setStyleSheet(button_style)

data = pd.DataFrame([
        {'Value Date': '01-04-2022', 'Description': 'openingbalance', 'Debit': 0.00, 'Credit': 3397.13, 'Balance': 3397.13, 'Category': 'Opening Balance'},
        {'Value Date': '01-04-2022', 'Description': 'mbrentref209108561454', 'Debit': 3000.00, 'Credit': 0.00, 'Balance': 397.13, 'Category': 'Rent Paid'},
        {'Value Date': '01-04-2022', 'Description': 'upi/saisuvidhasho/209125626472/paymentfromph', 'Debit': 140.00, 'Credit': 0.00, 'Balance': 257.13, 'Category': 'UPI-Dr'},
        {'Value Date': '01-04-2022', 'Description': 'mbsenttogane62491633408impsref209121360374', 'Debit': 200.00, 'Credit': 0.00, 'Balance': 57.13, 'Category': 'Creditor'},
        {'Value Date': '01-04-2022', 'Description': 'rev:imps62491633408ref209121360374', 'Debit': 0.00, 'Credit': 200.00, 'Balance': 257.13, 'Category': 'Refund/Reversal'},
        {'Value Date': '03-04-2022', 'Description': 'recd:imps/209310634191/mrsmeena/kkbk/x8247/ineti', 'Debit': 0.00, 'Credit': 3000.00, 'Balance': 3057.13, 'Category': 'Debtor'},
        {'Value Date': '03-04-2022', 'Description': 'upi/kfcsapphirefo/209376260786/ye', 'Debit': 250.00, 'Credit': 0.00, 'Balance': 807.13, 'Category': 'Food Expense/Hotel'},
        {'Value Date': '04-04-2022', 'Description': 'ib:receivedfromruteshslodaya06580010004867', 'Debit': 0.00, 'Credit': 18269.00, 'Balance': 18516.13, 'Category': 'Suspense'},
        {'Value Date': '05-04-2022', 'Description': 'mbloanref209507057778', 'Debit': 6000.00, 'Credit': 0.00, 'Balance': 7316.13, 'Category': 'Loan given'},
        {'Value Date': '07-04-2022', 'Description': 'upi/irctcwebupi/209730050986/oid100003321095', 'Debit': 2568.60, 'Credit': 0.00, 'Balance': 3387.03, 'Category': 'Travelling Expense'},
    ])

# data = pd.DataFrame([
#         {'Value Date': '01-04-2022', 'Description': 'openingbalance', 'Debit': 0.00, 'Credit': 3397.13, 'Balance': 3397.13, 'Category': 'A'},
#         {'Value Date': '01-04-2022', 'Description': 'mbrentref209108561454', 'Debit': 3000.00, 'Credit': 0.00, 'Balance': 397.13, 'Category': 'B'},
#         {'Value Date': '01-04-2022', 'Description': 'upi/saisuvidhasho/209125626472/paymentfromph', 'Debit': 140.00, 'Credit': 0.00, 'Balance': 257.13, 'Category': 'C'},
#         {'Value Date': '01-04-2022', 'Description': 'mbsenttogane62491633408impsref209121360374', 'Debit': 200.00, 'Credit': 0.00, 'Balance': 57.13, 'Category': 'A'},
#         {'Value Date': '01-04-2022', 'Description': 'rev:imps62491633408ref209121360374', 'Debit': 0.00, 'Credit': 200.00, 'Balance': 257.13, 'Category': 'B'},
#         {'Value Date': '03-04-2022', 'Description': 'recd:imps/209310634191/mrsmeena/kkbk/x8247/ineti', 'Debit': 0.00, 'Credit': 3000.00, 'Balance': 3057.13, 'Category': 'C'},
#         {'Value Date': '03-04-2022', 'Description': 'upi/kfcsapphirefo/209376260786/ye', 'Debit': 250.00, 'Credit': 0.00, 'Balance': 807.13, 'Category': 'A'},
#         {'Value Date': '04-04-2022', 'Description': 'ib:receivedfromruteshslodaya06580010004867', 'Debit': 0.00, 'Credit': 18269.00, 'Balance': 18516.13, 'Category': 'B'},
#         {'Value Date': '05-04-2022', 'Description': 'mbloanref209507057778', 'Debit': 6000.00, 'Credit': 0.00, 'Balance': 7316.13, 'Category': 'C'},
#         {'Value Date': '07-04-2022', 'Description': 'upi/irctcwebupi/209730050986/oid100003321095', 'Debit': 2568.60, 'Credit': 0.00, 'Balance': 3387.03, 'Category': 'D'},
#     ])

class NetworkGraphTabTest(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.setWindowTitle("Transaction Network Graph")
        self.setGeometry(100, 100, 1200, 900)
        
        # Set the stylesheet for the entire application
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                color: #333333;
            }
            QLabel {
                color: #333333;
            }
            QPushButton, QComboBox, QDoubleSpinBox {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                padding: 5px;
                color: #333333;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 1px solid #5c5c5c;
            }
        """)
        
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Create matplotlib figure
        self.figure = plt.figure(figsize=(12, 10))
        self.canvas = FigureCanvas(self.figure)
        
        # Add navigation toolbar
        nav_toolbar = CustomNavigationToolbar(self.canvas, self)
        
        # Create controls
        controls_layout = QHBoxLayout()
        
        # # Layout selector
        # self.layout_selector = QComboBox()
        # self.layout_selector.addItems(["Spring", "Circular", "Shell", "Spectral"])
        # self.layout_selector.currentTextChanged.connect(self.update_graph)
        # controls_layout.addWidget(QLabel("Layout:"))
        # controls_layout.addWidget(self.layout_selector)
        
        # Node size slider
        self.node_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.node_size_slider.setRange(500, 5000)
        self.node_size_slider.setValue(2000)
        self.node_size_slider.valueChanged.connect(self.update_graph)
        controls_layout.addWidget(QLabel("Node Size:"))
        controls_layout.addWidget(self.node_size_slider)
        
        # # Spring layout k value
        self.k_value = QDoubleSpinBox()
        # self.k_value.setRange(0.1, 100)
        self.k_value.setValue(50)
        # self.k_value.setSingleStep(0.1)
        # self.k_value.valueChanged.connect(self.update_graph)
        # controls_layout.addWidget(QLabel("Spring Layout k:"))
        # controls_layout.addWidget(self.k_value)
        
        # Add controls and canvas to main layout
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(nav_toolbar)
        main_layout.addWidget(self.canvas)
        
        self.setCentralWidget(main_widget)

        # Define professional color palette
        self.color_palette = {
            'Opening Balance': '#2C3E50',  # Dark blue-gray
            'Rent Paid': '#E74C3C',  # Professional red
            'UPI-Dr': '#3498DB',  # Clean blue
            'Creditor': '#9B59B6',  # Royal purple
            'Refund/Reversal': '#27AE60',  # Forest green
            'Debtor': '#F1C40F',  # Golden yellow
            'Food Expense/Hotel': '#E67E22',  # Burnt orange
            'Suspense': '#95A5A6',  # Light gray
            'Loan given': '#D35400',  # Deep orange
            'Travelling Expense': '#16A085'  # Teal
        }
        
        # Call method to draw network
        self.create_graph()

    def create_graph(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        # Create a directed graph
        G = nx.DiGraph()

        # Add nodes (categories) and edges (transactions)
        category_colors = {}
        node_sizes = {}
        edge_weights = {}
        for index, row in data.iterrows():
            if row['Category'] not in category_colors:
                category_colors[row['Category']] = plt.cm.Set3(len(category_colors) / 12.)
            if row['Debit'] > 0:
                G.add_edge('Opening Balance', row['Category'], weight=row['Debit'])
                edge_weights[('Opening Balance', row['Category'])] = row['Debit']
            if row['Credit'] > 0:
                G.add_edge(row['Category'], 'Opening Balance', weight=row['Credit'])
                edge_weights[('Opening Balance', row['Category'])] = row['Credit']
            node_sizes[row['Category']] = node_sizes.get(row['Category'], 0) + abs(row['Debit'] - row['Credit'])

        # Get the base size from the slider
        base_size = self.node_size_slider.value()
        
        # Normalize node sizes using the slider value as the base
        if node_sizes:  # Check if there are any nodes
            max_size = max(node_sizes.values())
            node_sizes = {k: (base_size/2) + (v / max_size) * base_size for k, v in node_sizes.items()}
            node_sizes['Opening Balance'] = base_size * 1.5  # Make the central node proportionally larger


        pos = nx.spring_layout(G, k=self.k_value.value())
        # # Get layout based on user selection
        # layout_func = self.layout_selector.currentText()
        # if layout_func == "Spring":
        #     pos = nx.spring_layout(G, k=self.k_value.value())
        # elif layout_func == "Circular":
        #     pos = nx.circular_layout(G)
        # elif layout_func == "Shell":
        #     pos = nx.shell_layout(G)
        # else:  # Spectral
        #     pos = nx.spectral_layout(G)
        
        # Draw nodes
        for node, (x, y) in pos.items():
            color = category_colors.get(node, 'skyblue')
            size = node_sizes.get(node, base_size)
            node_collection = nx.draw_networkx_nodes(G, pos, nodelist=[node], node_color=[color], node_size=size, alpha=0.85, ax=ax)
            node_collection.set_zorder(1)  # Set nodes to be drawn first


        # Draw edges with curved arrows
        edges = []
        for (u, v, d) in G.edges(data=True):
            edge_color = 'gray'
            edge_width = 1 + (edge_weights.get((u, v), 0) / max(edge_weights.values())) * 5
            # Draw each edge individually and set its zorder
            edge = nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], 
                                        edge_color='#7F8C8D',  # Professional gray
                                        width=edge_width, 
                                        alpha=0.5,
                                        ax=ax,
                                        connectionstyle="arc3,rad=0.1", 
                                        arrowsize=20)
            
            # If edge is a list of path collections
            if isinstance(edge, list):
                for e in edge:
                    e.set_zorder(3)
            else:
                edge.set_zorder(3)
            edges.append(edge)

        # Add labels
        labels = nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=ax,font_family='sans-serif')
        for label in labels.values():
            label.set_zorder(3)  # Set labels to be drawn last

        # Add edge labels
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax, font_size=8,font_family='sans-serif')

        # Add a colorbar legend
        unique_colors = list(set(category_colors.values()))
        unique_categories = [cat for cat, color in category_colors.items() if color in unique_colors]
        cmap = plt.cm.colors.ListedColormap(unique_colors)
        norm = plt.cm.colors.BoundaryNorm(range(len(unique_colors)+1), cmap.N)
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        # cbar = plt.colorbar(sm, ax=ax, orientation='vertical', aspect=30, pad=0.1)
        # cbar.set_ticks(np.arange(0.5, len(unique_colors)))
        # cbar.set_ticklabels(unique_categories)
        # cbar.set_label('Transaction Categories', rotation=270, labelpad=15)

        # Remove axis
        ax.axis('off')

        # Render the plot
        self.canvas.draw()

    def update_graph(self):
            self.create_graph()