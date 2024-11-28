import requests
import json
import time

def validate_license(license_key, username, timestamp, api_key, url):
    # Construct the payload
    payload = {
        "license_key": license_key,
        "username": username,
        "timestamp": timestamp
    }
    
    # Set up the headers
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        # Make the POST request to the API
        response = requests.post(url, headers=headers, json=payload)
        
        # Raise an exception if the request returned an error code (4xx, 5xx)
        response.raise_for_status()
        
        # Print the response in JSON format (or you can handle it as per your needs)
        print("Response from server:", response.json())
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        # Print response content for debugging
        try:
            print("Response content:", response.text)
        except:
            pass
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred: {req_err}")

# Variables you need to update for actual use
license_key = "SOMEX4Y4ZLicenseKEY1732686454"
username = "1-bd7c6c56"
timestamp = time.time()  # Using current timestamp
api_key = "U08fir-OsEXdgMZKARdgz5oPvyRT6cIZioOeV_kZdLMeXsAc46_x.CAgICAgICAo="  # Note the '=' at the end
url = "http://43.204.61.215/validate-offline-license/"  # Replace with your actual API endpoint

# Run the validation
validate_license(license_key, username, timestamp, api_key, url)
