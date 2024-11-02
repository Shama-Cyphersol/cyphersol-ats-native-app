import sys
import pandas as pd
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

class EODBalanceChart(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Daily Financial Trends")
        self.resize(1400, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create QWebEngineView
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        # Create the HTML content with the graph and radio buttons
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Daily Financial Values</title>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
            <style>
                body { 
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    flex-direction: column;
                    margin: 0; 
                    padding: 20px; 
                    font-family: Arial, sans-serif;
                    background-color: #f8fafc;
                }
                .chart-container { 
                    width: 80%;
                    height: calc(100vh - 40px);
                    background-color: white;
                    padding: 10px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .title {
                    text-align: center;
                    margin-bottom: 20px;
                    font-size: 20px;
                    font-weight: bold;
                    color: #1e293b;
                }
                .radio-group {
                    text-align: center;
                    margin-bottom: 20px;
                }
                .radio-group label {
                    margin-right: 15px;
                    font-size: 16px;
                }
            </style>
        </head>
        <body>
            <div class="radio-group">
                <label><input type="radio" name="month" value="Apr-2023" checked> Apr-2023</label>
                <label><input type="radio" name="month" value="May-2023"> May-2023</label>
                <label><input type="radio" name="month" value="Jun-2023"> Jun-2023</label>
                <label><input type="radio" name="month" value="Jul-2023"> Jul-2023</label>
                <label><input type="radio" name="month" value="Aug-2023"> Aug-2023</label>
                <label><input type="radio" name="month" value="Sep-2023"> Sep-2023</label>
                <label><input type="radio" name="month" value="Oct-2023"> Oct-2023</label>
                <label><input type="radio" name="month" value="Nov-2023"> Nov-2023</label>
                <label><input type="radio" name="month" value="Dec-2023"> Dec-2023</label>
                <label><input type="radio" name="month" value="Jan-2024"> Jan-2024</label>
                <label><input type="radio" name="month" value="Feb-2024"> Feb-2024</label>
                <label><input type="radio" name="month" value="Mar-2024"> Mar-2024</label>
            </div>
            
            <div class="chart-container">
                <div class="title">Daily Financial Values</div>
                <canvas id="financialChart"></canvas>
            </div>
            
            <script>
                const monthsData = {
                    'Apr-2023': [1373694.32, 1351195.32, 1351870.32, 651390.32, 306870.32, 250890.32, 252890.32, 255301.50, 255301.50, 256301.50, 250001.50, 265001.50],
                    'May-2023': [843219.00, 851219.00, 846973.36, 826873.36, 903740.36, 893711.36, 893711.36, 876960.44, 936959.44, 923044.44, 891544.44, 901518.44],
                    'Jun-2023': [293265.30, 284265.30, 254686.88, 254686.88, 254686.88, 254686.88, 614855.26, 254098.06, 254098.06, 254098.06, 260000.06, 270000.06],
                    'Jul-2023': [328268.02, 278168.02, 277313.40, 219853.40, 243855.26, 243855.26, 614855.26, 676355.26, 656355.26, 620000.26, 580000.26, 590000.26],
                    'Aug-2023': [852550.10, 107550.10, 907550.10, 905240.10, 52340.10, -52584.10, 787515.10, -87584.10, 97584.10, 87000.10, 91000.10, 89000.10],
                    'Sep-2023': [528480.80, 654480.80, 457480.80, 637480.80, 738480.80, 727480.80, 927480.80, 837480.80, 717480.80, 757480.80, 707480.80, 687480.80],
                    'Oct-2023': [946858.38, 869858.38, 832858.38, 723858.38, 832858.38, 923858.38, 823858.38, 909858.38, 809858.38, 757858.38, 767858.38, 779858.38],
                    'Nov-2023': [256351.90, 271351.90, 311351.90, 296351.90, 254351.90, 214351.90, 274351.90, 294351.90, 244351.90, 284351.90, 204351.90, 224351.90],
                    'Dec-2023': [254876.90, 254876.90, 243876.90, 225876.90, 219876.90, 239876.90, 257876.90, 267876.90, 279876.90, 217876.90, 237876.90, 249876.90],
                    'Jan-2024': [729480.20, 724480.20, 694480.20, 747480.20, 724480.20, 734480.20, 789480.20, 774480.20, 764480.20, 754480.20, 784480.20, 794480.20],
                    'Feb-2024': [647404.62, 674404.62, 734404.62, 654404.62, 674404.62, 674404.62, 654404.62, 624404.62, 614404.62, 614404.62, 624404.62, 614404.62],
                    'Mar-2024': [936858.38, 965858.38, 982858.38, 952858.38, 942858.38, 932858.38, 922858.38, 912858.38, 902858.38, 892858.38, 882858.38, 872858.38]
                };
                
                // Define colors for each month
                const monthColors = {
                    'Apr-2023': '#2563eb',
                    'May-2023': '#16a34a',
                    'Jun-2023': '#f59e0b',
                    'Jul-2023': '#ef4444',
                    'Aug-2023': '#8b5cf6',
                    'Sep-2023': '#ec4899',
                    'Oct-2023': '#10b981',
                    'Nov-2023': '#f97316',
                    'Dec-2023': '#3b82f6',
                    'Jan-2024': '#d97706',
                    'Feb-2024': '#06b6d4',
                    'Mar-2024': '#22d3ee'
                };
                
                // Default chart data
                let selectedMonth = 'Apr-2023';
                
                const config = {
                    type: 'line',
                    data: {
                        labels: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'],
                        datasets: [{
                            label: selectedMonth,
                            data: monthsData[selectedMonth],
                            backgroundColor: monthColors[selectedMonth],
                            borderColor: monthColors[selectedMonth],
                            borderWidth: 2,
                            fill: false,
                            pointBackgroundColor: '#ffffff',
                            pointBorderWidth: 2,
                            pointRadius: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: {
                                position: 'top'
                            }
                        },
                        scales: {
                            x: {
                                title: {
                                    display: true,
                                    text: 'Days'
                                }
                            },
                            y: {
                                title: {
                                    display: true,
                                    text: 'Amount'
                                }
                            }
                        }
                    }
                };
                
                const ctx = document.getElementById('financialChart').getContext('2d');
                let financialChart = new Chart(ctx, config);
                
                // Update chart when radio button changes
                document.querySelectorAll('input[name="month"]').forEach(radio => {
                    radio.addEventListener('change', function() {
                        selectedMonth = this.value;
                        financialChart.data.datasets[0].label = selectedMonth;
                        financialChart.data.datasets[0].data = monthsData[selectedMonth];
                        financialChart.data.datasets[0].backgroundColor = monthColors[selectedMonth];
                        financialChart.data.datasets[0].borderColor = monthColors[selectedMonth];
                        financialChart.update();
                    });
                });
            </script>
        </body>
        </html>
        """
        
        # Set HTML content in the QWebEngineView
        self.web_view.setHtml(html_content)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EODBalanceChart()
    window.show()
    sys.exit(app.exec())
