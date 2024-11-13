import random
from datetime import datetime, timedelta
from utils.json_logic import *

def get_report_count():
    cases = load_all_case_data()
    return len(cases)

def get_monthly_report_count():
    cases = load_all_case_data()
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    monthly_count = sum(
        1 for case in cases 
        if datetime.strptime(case['date'], "%d-%m-%Y").month == current_month 
        and datetime.strptime(case['date'], "%d-%m-%Y").year == current_year
    )
    
    return monthly_count


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
