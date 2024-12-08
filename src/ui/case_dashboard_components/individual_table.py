from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
                             QDialog, QPushButton,)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtCore import QObject, pyqtSlot
from ui.individual_dashboard import IndividualDashboard
from PyQt6.QtGui import QMovie


class WebBridge(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    @pyqtSlot(str, str, int)
    def rowClicked(self, name, account_number, row_id):
        self.parent.handle_row_click(name, account_number, row_id)

    @pyqtSlot(str)
    def log(self, message):
        print("JavaScript Log:", message)

class CustomWebPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        # print(f"JS Console ({level}): {message} [Line {lineNumber}] [{sourceID}]")
        print(f"JS Console conntected")


def create_individual_dashboard_table(case):
    data = []
    for i in range(len(case["individual_names"]["Name"])):
        data.append({
            "Name": case["individual_names"]["Name"][i],
            "Account Number": case["individual_names"]["Acc Number"][i],
            "Pdf Path": case["file_names"][i],
            "row_id": i
        })
    
    return IndividualDashboardTable(data, case["case_id"])

class IndividualDashboardTable(QWidget):
    def __init__(self, data, case_id):
        super().__init__()
        self.data = data
        self.case_id = case_id
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.web_view = QWebEngineView()
        self.web_page = CustomWebPage(self.web_view)
        self.web_view.setPage(self.web_page)
        self.web_view.setMinimumHeight(1000)
        
        self.channel = QWebChannel()
        self.web_page.setWebChannel(self.channel)
        
        self.bridge = WebBridge(self)
        self.channel.registerObject('bridge', self.bridge)

        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }
                
                .search-container {
                    margin: 10px;
                    padding: 10px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .search-input {
                    width: 300px;
                    padding: 10px;
                    border: 2px solid #3498db;
                    border-radius: 5px;
                    font-size: 14px;
                    outline: none;
                    transition: border-color 0.3s;
                }
                .search-input:focus {
                    border-color: #2980b9;
                }
                .name{
                    color: blue;
                    cursor: pointer;
                    text-decoration: underline;
                }
                
                table {
                    width: 100%;
                    border-collapse: collapse;
                    background-color: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 0 20px rgba(0,0,0,0.1);
                    table-layout: fixed; /* Ensures equal column width distribution */
                }

                /* Add these new styles */
                table th:first-child, table td:first-child {
                    width: 50px; /* Fixed width for serial number column */
                    flex-grow: 0;
                    text-align: center;
                }

                table th:nth-child(2), table td:nth-child(2) {
                    width: calc(30%); /* Name column gets 40% */
                }

                table th:nth-child(3), table td:nth-child(3) {
                    width: calc(30%); /* Account Number column gets 30% */
                }

                table th:nth-child(4), table td:nth-child(4) {
                    width: calc(40%); /* PDF Path column gets 30% */
                    max-width:0;
                    font-size: 14px;

                }
                
                td {
                    padding: 12px 15px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                    word-wrap: break-word;  /* Allow long words to break */
                    word-break: break-word; /* Break words at any point if needed */
                    white-space: normal;    /* Allow text to wrap */
                    overflow-wrap: break-word; /* Another method to break long words */
                }
                
                th {
                    background-color: #3498db;
                    color: white;
                    font-weight: bold;
                    padding: 12px;
                    text-align: center;
                    position: sticky;
                    top: 0;
                }
                
                tr:hover {
                    background-color: #f5f5f5;
                }
                
                .pagination {
                    margin-top: 20px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    gap: 15px;
                }
                
                button {
                    padding: 8px 16px;
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                
                button:disabled {
                    background-color: #ccc;
                    cursor: not-allowed;
                }
                
                button:hover:not(:disabled) {
                    background-color: #0056b3;
                }
                
                #pageInfo {
                    font-size: 14px;
                    color: #666;
                }
                
                .no-results {
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-style: italic;
                }
            </style>
            <script>
                let bridge = null;
                let initialized = false;
                let filteredData = [];
                const rowsPerPage = 10;
                let currentPage = 1;

                function initWebChannel() {
                    return new Promise((resolve) => {
                        if (typeof qt !== 'undefined') {
                            new QWebChannel(qt.webChannelTransport, function(channel) {
                                bridge = channel.objects.bridge;
                                bridge.log("WebChannel initialized");
                                resolve();
                            });
                        } else {
                            setTimeout(initWebChannel, 100);
                        }
                    });
                }

                function handleRowClick(name, accountNumber, rowId) {
                    if (bridge) {
                        bridge.rowClicked(name, accountNumber, rowId);
                    }
                }
                
                function handleSearch() {
                    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
                    
                    filteredData = window.tableData.filter(item => {
                        return item.Name.toLowerCase().includes(searchTerm) ||
                            item['Account Number'].toLowerCase().includes(searchTerm) ||
                            item['Pdf Path'].toLowerCase().includes(searchTerm);
                    });
                    currentPage = 1;
                    updateTable();
                }

                function updateTable(data) {
                    if (!initialized) {
                        bridge.log("Table update called before initialization");
                        return;
                    }

                    if (data) {
                        window.tableData = data;
                        filteredData = [...data];
                    }
                    
                    const totalPages = Math.ceil(filteredData.length / rowsPerPage);
                    const start = (currentPage - 1) * rowsPerPage;
                    const end = start + rowsPerPage;
                    const pageData = filteredData.slice(start, end);
                    
                    const tbody = document.getElementById('tableBody');
                    tbody.innerHTML = '';

                    if (filteredData.length === 0) {
                        tbody.innerHTML = `
                            <tr>
                                <td colspan="3" class="no-results">No matching results found</td>
                            </tr>
                        `;
                    } else {
                        pageData.forEach((item,index) => {
                            const row = document.createElement('tr');
                            row.onclick = () => handleRowClick(item.Name, item['Account Number'], item.row_id);
                            row.innerHTML = `
                                <td>${start + index + 1}</td>
                                <td class = "name">${item.Name}</td>
                                <td>${item['Account Number']}</td>
                                <td>${item['Pdf Path']}</td>
                            `;
                            tbody.appendChild(row);
                        });
                    }
                    
                    document.getElementById('pageInfo').textContent = filteredData.length > 0 ? 
                        `Page ${currentPage} of ${totalPages}` : '';
                    document.getElementById('prevBtn').disabled = currentPage === 1;
                    document.getElementById('nextBtn').disabled = currentPage === totalPages || filteredData.length === 0;
                }

                function nextPage() {
                    const totalPages = Math.ceil(filteredData.length / rowsPerPage);
                    if (currentPage < totalPages) {
                        currentPage++;
                        updateTable();
                    }
                }

                function previousPage() {
                    if (currentPage > 1) {
                        currentPage--;
                        updateTable();
                    }
                }

                document.addEventListener('DOMContentLoaded', async function() {
                    try {
                        await initWebChannel();
                        initialized = true;
                        bridge.log("Page fully initialized");
                        window.updateTableData && window.updateTableData();
                    } catch (error) {
                        console.error("Initialization error:", error);
                    }
                });
            </script>
        </head>
        <body>
            <div class="search-container">
                <input type="text" 
                    id="searchInput" 
                    class="search-input" 
                    placeholder="Search..."
                    oninput="handleSearch()">
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Sr no.</th>
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
        </body>
        </html>
        """
        
        self.web_view.setHtml(html_content)
        
        def check_initialization():
            self.web_page.runJavaScript(
                'typeof initialized !== "undefined" && initialized',
                lambda result: self.update_table_data() if result else QTimer.singleShot(100, check_initialization)
            )
        
        QTimer.singleShot(100, check_initialization)
        
        layout.addWidget(self.web_view)

    def update_table_data(self):
        js_code = f"""
            window.tableData = {self.data};
            if (typeof updateTable === 'function') {{
                updateTable(window.tableData);
            }}
        """
        self.web_page.runJavaScript(js_code)

    def handle_row_click(self, name, account_number, row_id):
        # Show the loader
        spinner_label = QLabel(self)
        spinner_movie = QMovie("assets/spinner.gif")  # Ensure the file path is correct
        spinner_label.setMovie(spinner_movie)
        spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Style and size the spinner
        spinner_label.setFixedSize(100, 100)  # Adjust size as needed
        spinner_label.setStyleSheet("background-color: rgba(255, 255, 255, 200); border-radius: 10px;")

        # Center the spinner in the parent widget
        spinner_label.move(
            (self.width() - spinner_label.width()) // 2,
            (self.height() - spinner_label.height()) // 2,
        )

        spinner_label.show()
        spinner_movie.start()
        
        individual_dashboard = IndividualDashboard(
            case_id=self.case_id,
            name=name,
            row_id=row_id
        )
        
        new_window = QDialog(self)
        new_window.setWindowTitle("Individual Dashboard")
        new_window.setModal(False)
        new_window.showMaximized()
        
        new_window.setWindowFlag(Qt.WindowType.WindowMinimizeButtonHint)
        new_window.setWindowFlag(Qt.WindowType.WindowMaximizeButtonHint)
        new_window.setWindowFlag(Qt.WindowType.WindowCloseButtonHint)
        
        layout = QVBoxLayout()
        layout.addWidget(individual_dashboard)
        new_window.setLayout(layout)
        # add a delay to show the spinner
        QTimer.singleShot(0, lambda: self.show_individual_dashboard(new_window, spinner_label))
        # new_window.show()

        # # Hide the spinner
        # spinner_label.movie().stop()
        # spinner_label.hide()

    def show_individual_dashboard(self, new_window, spinner_label):
        new_window.show()
        spinner_label.movie().stop()
        spinner_label.hide()
        