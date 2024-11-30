import json
import pickle
from datetime import datetime
import json
import os

def save_case_data(case_id, file_names, start_date, end_date,individual_names):
    today_date = datetime.now().strftime("%d-%m-%Y")
    case_data = {

        "case_id": case_id,
        "file_names": file_names,
        "start_date": start_date,
        "end_date": end_date,
        "report_name": "Report_"+case_id,
        "individual_names":individual_names,
        "date":today_date
    }

    if len(file_names) == 1:
        case_data["start_date"] = start_date[0]
        case_data["end_date"] = end_date[0]
    else:
        case_data["start_date"] = "-"
        case_data["end_date"] = "-"

    # Read existing data or initialize an empty list
    try:
        with open("src/data/json/cases.json", "r") as f:
            existing_data = json.load(f)
    except:
        existing_data = []

    # Append the new case data to the beginning of the list
    existing_data.append( case_data)

    # Write the updated data back to the file
    with open("src/data/json/cases.json", "w") as f:
        json.dump(existing_data, f, indent=4)

def load_all_case_data():
    with open("src/data/json/cases.json", "r") as f:
        return json.load(f)
    
def load_case_data(case_id):
    with open("src/data/json/cases.json", "r") as f:
        data = json.load(f)
        for case in data:
            if case["case_id"] == case_id:
                return case
        return None

def save_result(CA_ID,result):
    with open("src/data/results/"+CA_ID+".pkl", 'wb') as f:
        pickle.dump(result, f)

def load_result(CA_ID):
    with open("src/data/results/"+CA_ID+".pkl", 'rb') as f:
        return pickle.load(f)
    

def check_and_add_date():
    # Get today's date in dd-mm-yyyy format
    today_date = datetime.now().strftime("%d-%m-%Y")
    
    # Load existing data from the JSON file
    try:
        with open("src/data/json/cases.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("File not found.")
        return
    except json.JSONDecodeError:
        print("Error decoding JSON.")
        return

    # Check each entry and add date if missing
    for case in data:
        if "date" not in case:
            case["date"] = today_date

    # Save the updated data back to the JSON file
    with open("src/data/json/cases.json", "w") as f:
        json.dump(data, f, indent=4)

    print("Date checked and added where missing.")

   
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
    
    return results_data


# test = load_result("CA_ID_SLXPFRN8LHTVEQ51")
# test = test["cummalative_df"]["entity_df"]["Entity"]
# print(test)