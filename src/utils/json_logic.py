import json
import pickle

import json

def save_case_data(case_id, file_names, start_date, end_date,individual_names):
    case_data = {
        "case_id": case_id,
        "file_names": file_names,
        "start_date": start_date,
        "end_date": end_date,
        "report_name": "Report_"+case_id,
        "individual_names":individual_names
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
    existing_data.insert(0, case_data)

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
    

test = load_result("CA_ID_0P35LS6N8C3EPYAL")
test2 = test["single_df"]["A0"]["data"]["new_tran_df"]
hey = test["cummalative_df"]["name_acc_df"].to_dict("list")
print(hey)
# test2.to_excel("test.xlsx")
