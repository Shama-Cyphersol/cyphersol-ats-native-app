import json
import pickle
from datetime import datetime
import json
import os
from ..core.repository import *
from ..core.session_manager import SessionManager
# from .refresh import cummalative_person_sheets
from ..utils.refresh import cummalative_person_sheets

def ensure_result_directory_exists(directory_path):
    # Check if the directory exists
    if not os.path.exists(directory_path):
        # Create the directory if it doesn't exist
        os.makedirs(directory_path)

def save_case_data(case_id, file_names, individual_names):
    today_date = datetime.now().strftime("%d-%m-%Y")

    user = SessionManager.get_current_user()

    case_data = {
        'case_id': case_id,
        "user_id": user.id,
    }

    case_repo = CaseRepository()
    case = case_repo.get_case_by_id(case_id)
    if not case:
        print("Case not found. Creating a new case...")
        case = case_repo.create_case(case_data)

    print("Case created:", case)

    name = individual_names.get("Name") or []
    acc_number = individual_names.get("Acc Number") or []
    ifsc_code = individual_names.get("ifsc_code") or []
    bank_name = individual_names.get("bank_name") or []
    total_items = max(len(file_names), len(acc_number), len(name), len(ifsc_code), len(bank_name))

    for index in range(total_items):
        statement_data = {
            "case_id": case.case_id,
            "account_name": name[index] or "" if index < len(name) else "",
            "account_number": acc_number[index] or "" if index < len(acc_number) else "",
            "local_filename": file_names[index] or "" if index < len(file_names) else "",
            "ifsc_code": ifsc_code[index] or "" if index < len(ifsc_code) else "",
            "bank_name": bank_name[index] or "" if index < len(bank_name) else "",
        }

        statement_info = StatementInfoRepository()
        statement_info = statement_info.create_statement_info(statement_data)

    case_data = {
        "case_id": case_id,
        "file_names": file_names,
        # "start_date": start_date,
        # "end_date": end_date,
        "individual_names":individual_names,
        "date": today_date
    }

    # if len(file_names) == 1:
    #     case_data["start_date"] = start_date[0]
    #     case_data["end_date"] = end_date[0]
    # else:
    #     case_data["start_date"] = "-"
    #     case_data["end_date"] = "-"

    # Read existing data or initialize an empty list
    try:
        with open("src/data/json/cases.json", "r") as f:
            existing_data = json.load(f)
    except:
        existing_data = []

    # Append the new case data to the beginning of the list
    existing_data.insert(0, case_data)
    # existing_data.append( case_data)

    # Write the updated data back to the file
    with open("src/data/json/cases.json", "w") as f:
        json.dump(existing_data, f, indent=4)
    
    return case_data

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

def update_case_data(case_id, new_case_data):
    """
    Updates an existing case's data in the JSON file.
    
    :param case_id: The ID of the case to update
    :param new_case_data: A dictionary containing the new case data
    :return: True if updated successfully, False otherwise
    """
    try:
        # Load existing data
        with open("src/data/json/cases.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: Case data file not found.")
        return False

    case_found = False

    # Update the case if it exists
    for i, case in enumerate(data):
        if case["case_id"] == case_id:
            # Replace the old case data with the new one
            data[i] = {**case, **new_case_data}  # Merge existing data with new data
            case_found = True
            break

    if not case_found:
        print(f"Error: Case with ID {case_id} not found.")
        return False

    # Write the updated data back to the file
    with open("src/data/json/cases.json", "w") as f:
        json.dump(data, f, indent=4)

    return True

def delete_case_data(case_id):
    # Load existing data
    data = load_all_case_data()

    # Find the case with the matching ID
    for i, case in enumerate(data):
        if case["case_id"] == case_id:
            # Remove the case from the list
            data.pop(i)
            break
    else:
        print(f"Error: Case with ID {case_id} not found.")
        return False

    # Write the updated data back to the file
    with open("src/data/json/cases.json", "w") as f:
        json.dump(data, f, indent=4)

    return True


def save_result(CA_ID,result):
    with open("src/data/results/"+CA_ID+".pkl", 'wb') as f:
        pickle.dump(result, f)

def load_result(CA_ID):
    directory_path = "src/data/results"
    
    ensure_result_directory_exists(directory_path)
    
    try:
        with open("src/data/results/"+CA_ID+".pkl", 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        print("File not found.")
        return {}
    

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

def update_name_merge_object(case_id, new_obj):
    # Open the NER results JSON file
    with open(f"src/data/json/merged_names.json", "r") as f:
        data = json.load(f)
    
    # Find the index of the object with the matching case_id
    for index, item in enumerate(data):
        if item.get('case_id') == case_id:
            # Update the existing object with the new object
            data[index] = new_obj
            break
    else:
        # If no matching case_id is found, you might want to append the new object
        # or raise an exception, depending on your requirements
        raise ValueError(f"No NER result found for case_id: {case_id}")
    
    # Write the updated data back to the file
    with open(f"src/data/json/merged_names.json", "w") as f:
        json.dump(data, f, indent=4)


def create_name_merge_object(obj):
    # open name_merge.json which is an array and append this obj
    with open(f"src/data/json/merged_names.json","r") as f:
        data = json.load(f)
        data.append(obj)
    with open(f"src/data/json/merged_names.json","w") as f:
        json.dump(data,f,indent=4)
        

def find_merge_name_object(case_id):
    with open(f"src/data/json/merged_names.json","r") as f:
        data = json.load(f)
        for obj in data:
            if obj["case_id"] == case_id:
                return obj
        return None
    
def delete_name_merge_object(case_id):
    with open(f"src/data/json/merged_names.json","r") as f:
        data = json.load(f)
        for i,obj in enumerate(data):
            if obj["case_id"] == case_id:
                data.pop(i)
                break
    with open(f"src/data/json/merged_names.json","w") as f:
        json.dump(data,f,indent=4)

def get_process_df(case_id):
    data = load_result(case_id)
    return data["cummalative_df"]["process_df"]

def update_process_df(case_id,new_process_df):
    # rerun refresh function with new process_df
    try:
        data = load_result(case_id)
        name_acc_df = data["cummalative_df"]["name_acc_df"]
        new_cummalative_df = cummalative_person_sheets(new_process_df,name_acc_df)
        
        data["cummalative_df"] = new_cummalative_df
        save_result(case_id,data)
        return True
    except:
        print("Error updating process_df")
        return False
    
def fetch_units():
    with open("src/data/json/units.json","r") as f:
        return json.load(f)
    
def add_unit(unit):
    units = fetch_units()
    units.append(unit)
    with open("src/data/json/units.json","w") as f:
        json.dump(units,f,indent=4)

def get_last_serial_number():
    with open("src/data/json/serial_number_history.json","r") as f:
        data = json.load(f)
        return data[0]

def update_serial_number_history(old_serial_number):
    serial_number = get_last_serial_number()
    # print("old_serial_number",old_serial_number)
    old_serial_number = int(old_serial_number)
    # print("old_serial_number",old_serial_number)
    if serial_number == old_serial_number:
        print("updating serial number")
        serial_number = [serial_number+1]
        with open("src/data/json/serial_number_history.json","w") as f:
            json.dump(serial_number,f,indent=4)



# test = load_result("CA_ID_BCZV8JZ9A7KNP7W2")
# cummalative_df =  test["cummalative_df"]["process_df"]
# cummalative_df.to_excel("delhey.xlsx")
# print(cummalative_df.head(15))

# test = load_result("CA_ID_SLXPFRN8LHTVEQ51")
# test = test["cummalative_df"]["bidirectional_analysis"]["bda_weekly_analysis"]
# print(test.keys())


# fifo = test["cummalative_df"]["fifo"]["fifo_weekly"]
# # test = test["cummalative_df"]["fifo"]["bda_weekly_analysis"]
# print(fifo)

# cases = load_all_case_data()
# for case in cases:
#     acc_numbers = case["individual_names"]["Acc Number"]

# obj = find_merge_name_object("ATS_unit_1_00014")
# print(obj.keys())
