import pandas as pd

def read_excel(file_path):
    # Read an Excel file and return a pandas DataFrame
    return pd.read_excel(file_path)

def write_excel(data, file_path):
    # Write a pandas DataFrame to an Excel file
    data.to_excel(file_path, index=False)
