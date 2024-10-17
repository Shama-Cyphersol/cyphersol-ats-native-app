# cyphersol-ats-native-app

This project is a professional, internal-use Windows desktop application built using **PySide6**. It includes functionalities like file management, report generation, and user settings, specifically designed for team operations. The application runs offline with secure license validation during initial setup. The project is to be completed within a strict 5-day timeline.

## Project Overview

This app provides a user-friendly interface to manage files, view dashboards, generate reports, and manage settings. It is designed for internal use, with key features focused on offline operation, efficient Excel file handling, and report generation.

## Table of Contents

- [Timeline](#timeline)
- [Repository Structure](#repository-structure)
- [Libraries and Dependencies](#libraries-and-dependencies)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Tabs Overview](#tabs-overview)

---

## Timeline

**5 Days Development Deadline**

- **Day 1**: Setup environment, install dependencies, and create basic UI using PySide6.
- **Day 2**: Implement file opening, directory viewer, and basic Excel file handling.
- **Day 3**: Create the dashboard with necessary stats and tables, and implement report generation logic.
- **Day 4**: Build the settings module and integrate user/license management.
- **Day 5**: Testing, final adjustments, code obfuscation, and packaging.

---

## Repository Structure

```bash
inhouse-dashboard-app/
│
├── src/                            # Source code
│   ├── apps/                       # Application-specific components
│   │   ├── dashboard/              # Dashboard app
│   │   │   ├── __init__.py         # Package marker
│   │   │   ├── controllers.py       # Controllers for dashboard
│   │   │   ├── models.py            # Data models for dashboard
│   │   │   ├── services.py          # Services/Managers for dashboard
│   │   │   ├── views.py             # Views for dashboard
│   │   │   ├── ui/                  # UI components for dashboard
│   │   │   │   ├── dashboard.ui     # Dashboard UI file
│   │   │   │   └── ...              # Other dashboard-specific UI files
│   │   │   └── res/                 # Resources for dashboard
│   │   │       ├── qss/             # QSS styles specific to dashboard
│   │   │       │   ├── styles.qss   # Styles specific to dashboard
│   │   │       ├── icons/           # Dashboard-specific icons
│   │   │       │   ├── icon1.png    # Example icon
│   │   │       │   └── ...          # Other icons
│   │   │       ├── images/          # Dashboard-specific images
│   │   │       │   ├── image1.jpg    # Example image
│   │   │       │   └── ...          # Other images
│   │   │       └── ...              # Other resources
│   │   ├── reports/                 # Reports app
│   │   │   ├── __init__.py
│   │   │   ├── controllers.py
│   │   │   ├── models.py
│   │   │   ├── services.py
│   │   │   ├── views.py             # Views for reports
│   │   │   ├── ui/
│   │   │   │   ├── report_generator.ui
│   │   │   │   └── ...
│   │   │   └── res/                 # Resources for reports
│   │   │       ├── qss/             # QSS styles specific to reports
│   │   │       │   ├── styles.qss   # Styles specific to reports
│   │   │       ├── icons/           # Report-specific icons
│   │   │       │   ├── icon1.png
│   │   │       │   └── ...          # Other icons
│   │   │       ├── images/          # Report-specific images
│   │   │       │   ├── image1.jpg
│   │   │       │   └── ...          # Other images
│   │   │       └── ...              # Other resources
│   │   └── ...                      # Other apps
│   ├── core/                       # Core functionalities
│   │   ├── __init__.py
│   │   ├── config.py               # Configuration settings
│   │   ├── db.py                   # Database interactions
│   │   ├── app.py                  # Main application starting point
│   │   └── ...                     # Other core functionalities
│   ├── main.py                     # Main application entry point
│   ├── res/                        # Shared resources (global)
│   │   ├── qss/                    # Global QSS styles
│   │   │   ├── styles.qss          # Global styling
│   │   ├── icons/                  # Global icons
│   │   │   ├── icon1.png           # Example global icon
│   │   │   └── ...                 # Other global icons
│   │   ├── images/                 # Global images
│   │   │   ├── image1.jpg          # Example global image
│   │   │   └── ...                 # Other global images
│   ├── ui/                         # Global UI components
│   │   ├── global_component.ui      # Example global UI file
│   │   └── ...                      # Other global UI files
│
├── uploads/                        # Directory for uploaded media files
│   └── ...                          # Uploaded files
│
├── tests/                          # Test cases
│   ├── test_dashboard.py           # Tests for dashboard app
│   ├── test_reports.py             # Tests for reports app
│   └── ...                         # Other tests
│
├── README.md                       # Project documentation
├── requirements.txt                # Required Python packages
└── LICENSE                         # Project license
```

---

## Libraries and Dependencies

This project uses the following libraries:

1. **PySide6**: Used to build the desktop user interface.
   - **Installation**: `pip install PySide6`
   - **Purpose**: UI components and visual layout.
2. **pandas**: For Excel file handling and data manipulation.

   - **Installation**: `pip install pandas`
   - **Purpose**: Load, manipulate, and display Excel data in the UI.

3. **openpyxl**: A dependency for reading and writing Excel files.

   - **Installation**: `pip install openpyxl`
   - **Purpose**: Backend support for Excel operations.

4. **PyCryptodome**: Used for encryption of license keys and data security.

   - **Installation**: `pip install pycryptodome`
   - **Purpose**: Secure storage and encryption for license validation.

5. **PyInstaller**: For packaging the Python app into a standalone Windows executable.

   - **Installation**: `pip install pyinstaller`
   - **Purpose**: Convert the app to a distributable `.exe` format.

6. **Pyarmor**: For code obfuscation to protect the source code.
   - **Installation**: `pip install pyarmor`
   - **Purpose**: Protecting the code from reverse-engineering.

---

## Features

1. **File Opening/Directory Viewer**:

   - Load Excel files and directories.
   - Excel files are displayed in the UI for review and analysis.

2. **Dashboard**:

   - Real-time statistics on the number of reports generated.
   - Display different data insights like report history, and trends.

3. **Generate Report**:

   - A form-based input system for generating multiple reports.
   - Includes date auto-import or custom date range selection.
   - Toggle button for automatic date vs. manual input.

4. **Settings**:
   - Manage user information and license validation.
   - Display activation status and expiration date for the license.

---

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-team/inhous-dashboard-app.git
   ```

2. **Install Required Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**
   ```bash
   python src/main.py
   ```

---

## Usage

- **File Opening/Directory Viewer**: Use the tab to open directories and view Excel files.
- **Dashboard**: View stats and history of reports generated.
- **Generate Report**: Fill out the form to create reports with selected or custom date ranges.
- **Settings**: Manage user info and validate or update license details.

---

## Tabs Overview

### 1. File Opening/Directory Viewer

- This tab allows users to load and view files or directories.
- Excel files are displayed and can be manipulated via a table format.

### 2. Dashboard

- **Reports Generated**: The total count of reports created is displayed.
- **Stats Overview**:
  - Report generation trends.
  - Data summary from loaded files.
- **Table**: A history of last generated reports with columns for:
  - Date
  - File Name
  - Report Status

### 3. Generate Report

- **Form Layout**: User inputs report parameters via a vertical form layout.
- **Date Handling**: Toggle between automatic date import or manual custom date entry.
- **Generate Button**: Executes report generation based on form inputs.

### 4. Settings

- **User Info**: View and update user details.
- **License Management**: Displays license status (valid/expired), activation date, and other related information.

---

**Note**: This project is designed for internal use only and is not open-source.

```

---

This markdown format should fit your project needs perfectly, making the repository clear, concise, and efficient for internal team use with a strong focus on the 5-day timeline and specific features you need. Let me know if you need any further adjustments!
```
