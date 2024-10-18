import random
from datetime import datetime, timedelta

def get_report_count():
    return random.randint(100, 1000)

def get_monthly_report_count():
    return random.randint(10, 100)

def get_recent_reports():
    reports = []
    for i in range(5):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        reports.append({
            'date': date,
            'name': f"Report {random.randint(1000, 9999)}",
            'status': random.choice(['Completed', 'In Progress', 'Pending'])
        })
    return reports
