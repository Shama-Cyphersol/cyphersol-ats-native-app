import json
import pickle
import os
from datetime import datetime

import json

def save_case_data(case_id, file_names, start_date, end_date, individual_names):
    # Ensure we have valid data
    if not individual_names.get("Name"):
        individual_names["Name"] = ["Unknown"]
    if not individual_names.get("Acc Number"):
        individual_names["Acc Number"] = ["Not Found"]

    case_data = {
        "case_id": case_id,
        "file_names": file_names,
        "start_date": start_date[0] if isinstance(start_date, list) and start_date else "-",
        "end_date": end_date[0] if isinstance(end_date, list) and end_date else "-",
        "report_name": f"Report_{case_id}",
        "individual_names": individual_names
    }

    # Ensure the directory exists
    os.makedirs(os.path.dirname("src/data/json/cases.json"), exist_ok=True)

    # Read existing data or initialize an empty list
    try:
        with open("src/data/json/cases.json", "r") as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    # Append the new case data to the beginning of the list
    existing_data.insert(0, case_data)

    # Write the updated data back to the file
    with open("src/data/json/cases.json", "w") as f:
        json.dump(existing_data, f, indent=4)

def load_all_case_data():
    with open("src/data/json/cases.json", "r") as f:
        return json.load(f)
    
def load_case_data(case_id):
    """Load specific case data from cases.json"""
    try:
        with open("src/data/json/cases.json", "r") as f:
            cases = json.load(f)
            
        # Find the case with matching ID
        for case in cases:
            if case['case_id'] == case_id:
                print(f"Found case data: {case}")
                return case
                
        print(f"Case ID {case_id} not found")
        return None
    except Exception as e:
        print(f"Error loading case data: {str(e)}")
        return None

def save_result(CA_ID,result):
    with open("src/data/results/"+CA_ID+".pkl", 'wb') as f:
        pickle.dump(result, f)

def load_result(CA_ID):
    with open("src/data/results/"+CA_ID+".pkl", 'rb') as f:
        return pickle.load(f)
    
def save_ner_results(case_id, processed_results):
    """Save NER processing results separately"""
    results_data = {
        "case_id": case_id,
        "timestamp": datetime.now().isoformat(),
        "documents": []
    }
    
    for result in processed_results:
        if hasattr(result, '__dict__'):
            doc_dict = {
                "filename": result.filename,
                "entities": [
                    {
                        "text": ent.text,
                        "label": ent.label,
                        "start_char": ent.start_char,
                        "end_char": ent.end_char
                    }
                    for ent in result.entities
                ] if hasattr(result, 'entities') else [],
                "error": result.error if hasattr(result, 'error') else None
            }
            results_data["documents"].append(doc_dict)
    
    # Ensure the directory exists
    os.makedirs("src/data/ner_results", exist_ok=True)
    
    with open(f"src/data/ner_results/{case_id}.json", "w") as f:
        json.dump(results_data, f, indent=4)
