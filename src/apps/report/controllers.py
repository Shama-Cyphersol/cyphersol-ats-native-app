import pandas as pd
import random
from datetime import datetime, timedelta

def generate_report(name, date):
    # Dummy function to generate a report
    print(f"Generating report: {name} for date: {date}")
    # In a real implementation, this would create the report and save it

def read_excel(file_path):
    # Read an Excel file and return a pandas DataFrame
    return pd.read_excel(file_path)

def write_excel(data, file_path):
    # Write a pandas DataFrame to an Excel file
    data.to_excel(file_path, index=False)


def get_recent_reports():
    reports = []
    for i in range(15):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        reports.append({
            'id': i + 1,
            'date': date,
            'name': f"Report {random.randint(1000, 9999)}",
        })
    return reports
