import random
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class IndividualDashboard(QWidget):
    def __init__(self, case_id,name,parent=None):
        super().__init__(parent)
        self.case_id= case_id
        self.name= name
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Add a title
        title = QLabel("Individual Dashboard")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("margin-top: 20px; margin-bottom: 20px;")
        title.setStyleSheet("""
            QLabel {
                color: #34495e;
                margin-top: 20px;
                margin-bottom: 20px;
            }
        """)
        main_layout.addWidget(title)

        # Create the graph widgets
        main_layout.addWidget(self.create_line_graph())
        main_layout.addWidget(self.create_bar_graph())
        main_layout.addWidget(self.create_pie_chart())

        self.setLayout(main_layout)

    def create_line_graph(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Create a line graph
        figure = plt.figure()
        canvas = FigureCanvas(figure)
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        canvas.setMinimumSize(400, 300)

        x = [i for i in range(10)]
        y = [random.uniform(0, 10) for _ in range(10)]
        plt.plot(x, y)
        plt.title("Line Graph")
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")

        layout.addWidget(canvas)
        widget.setLayout(layout)
        return widget

    def create_bar_graph(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Create a bar graph
        figure = plt.figure()
        canvas = FigureCanvas(figure)
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        canvas.setMinimumSize(400, 300)

        labels = ["A", "B", "C", "D", "E"]
        values = [random.randint(1, 10) for _ in range(5)]
        plt.bar(labels, values)
        plt.title("Bar Graph")
        plt.xlabel("Categories")
        plt.ylabel("Values")

        layout.addWidget(canvas)
        widget.setLayout(layout)
        return widget

    def create_pie_chart(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Create a pie chart
        figure = plt.figure()
        canvas = FigureCanvas(figure)
        canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        canvas.setMinimumSize(400, 300)

        labels = ["A", "B", "C", "D", "E"]
        values = [random.randint(1, 10) for _ in range(5)]
        plt.pie(values, labels=labels, autopct="%1.1f%%")
        plt.title("Pie Chart")

        layout.addWidget(canvas)
        widget.setLayout(layout)
        return widget
