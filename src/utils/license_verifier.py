import requests
import uuid
import datetime
import hashlib
import json
import os
import logging
import time
import argparse
from typing import Dict, Optional
from pathlib import Path
import socket
import platform
from functools import lru_cache
from abc import ABC, abstractmethod
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('license_verifier.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SystemInfoExtractorInterface(ABC):
    @abstractmethod
    def get_machine_id(self):
        pass
        

class WindowsSystemInfoExtractor(SystemInfoExtractorInterface):
    def __init__(self):
        """Initialize WMI with proper error handling"""
        self.c = None
        try:
            if sys.platform == "win32":
                import wmi
                self.c = wmi.WMI(timeout=30)
        except Exception as e:
            logger.error(f"Failed to initialize WMI: {str(e)}")
            self.c = None

    def get_machine_id(self):
        """
        Generate a unique machine identifier using multiple hardware components.
        Cached to avoid repeated hardware queries.
        """
        try:
            identifiers = []
            
            # System info
            identifiers.append(platform.node())  # Computer hostname
            identifiers.append(platform.machine())  # Machine type
            
            # Network info
            try:
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)
                identifiers.extend([hostname, ip])
            except Exception as e:
                logger.warning(f"Failed to get network info: {str(e)}")
            
            if self.c:
                try:
                    # CPU Info
                    cpu_info = self.c.Win32_Processor()[0]
                    identifiers.append(cpu_info.ProcessorId.strip())
                    
                    # BIOS Info
                    bios = self.c.Win32_BIOS()[0]
                    identifiers.append(bios.SerialNumber.strip())
                    
                    # Motherboard Info
                    board = self.c.Win32_BaseBoard()[0]
                    identifiers.append(board.SerialNumber.strip())
                    
                    # HDD Info
                    for disk in self.c.Win32_DiskDrive():
                        if disk.SerialNumber:
                            identifiers.append(disk.SerialNumber.strip())
                except Exception as e:
                    logger.warning(f"Failed to get some WMI info: {str(e)}")
            
            # MAC Address (fallback)
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                          for elements in range(0,2*6,2)][::-1])
            identifiers.append(mac)
            
            # Filter out empty or None values
            identifiers = [str(id_) for id_ in identifiers if id_]
            
            if not identifiers:
                raise ValueError("No hardware identifiers could be retrieved")
            
            # Combine and hash all identifiers
            machine_id = ':'.join(identifiers)
            return hashlib.sha256(machine_id.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Error generating machine ID: {str(e)}")
            # Fallback to basic system info
            fallback_id = f"{platform.node()}:{uuid.getnode()}"
            return hashlib.sha256(fallback_id.encode()).hexdigest()
        

class MacOSSystemInfoExtractor(SystemInfoExtractorInterface):

    def __init__(self):
        pass

    def get_machine_id(self):
        return uuid.getnode()

    
class LicenseVerificationError(Exception):
    """Custom exception for license verification errors"""
    pass

class LicenseVerifier:
    # Test credentials
    TEST_LICENSE_KEY = "SOMEX4Y4ZLicenseKEY1732686454"
    TEST_USERNAME = "1-bd7c6c56"
    
    def __init__(self, config_path: Optional[str] = None, system_info_extractor: Optional[SystemInfoExtractorInterface] = None):
        """
        Initialize the license verifier.
        
        Args:
            config_path: Optional path to config file containing endpoint URL
        """
        self.config = self._load_config(config_path)
        self.offline_endpoint = "http://43.204.61.215/validate-offline-license/"
        self.system_info_extractor = system_info_extractor
            
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from file or use defaults"""
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config file: {str(e)}")
        return {}

    @lru_cache(maxsize=1)
    def get_machine_id(self) -> str:
        return self.system_info_extractor.get_machine_id()
   

    def verify_license(self, username: str, first_name: str, 
                      last_name: str, license_key: str) -> Dict:
        """
        Verify license with the server.
        
        Args:
            username: User's username
            first_name: User's first name
            last_name: User's last name
            license_key: License key to verify
            
        Returns:
            Dict containing verification status and additional information
            
        Raises:
            LicenseVerificationError: If verification fails
        """
        return self.validate_offline_license(license_key, username)
        
    def validate_offline_license(self, license_key: str, username: str) -> Dict:
        """
        Validate license key using offline validation endpoint.
        
        Args:
            license_key: License key to validate
            username: Username associated with the license
            
        Returns:
            Dict containing validation status and additional information
        """
        url = self.offline_endpoint
        timestamp = time.time()
        api_key = "U08fir-OsEXdgMZKARdgz5oPvyRT6cIZioOeV_kZdLMeXsAc46_x.CAgICAgICAo="
        
        # Construct the payload exactly like the working version
        payload = {
            "license_key": license_key,
            "username": username,
            "timestamp": timestamp
        }
        
        # Set up headers exactly like the working version
        headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            # Make the POST request to the API
            response = requests.post(url, headers=headers, json=payload)
            
            # Raise an exception if the request returned an error code
            response.raise_for_status()
            
            # Get the response
            result = response.json()
            print("Response from server:", result)  # Match the working version's output
            
            # Check status
            if result.get('status') == 'OK':
                return {
                    "verified": True,
                    "message": "License validated successfully",
                    "data": result
                }
            else:
                return {
                    "verified": False,
                    "message": "License validation failed",
                    "data": result
                }
                
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            try:
                print("Response content:", response.text)
            except:
                pass
            return {
                "verified": False,
                "message": f"HTTP error: {http_err}",
                "data": None
            }
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred: {conn_err}")
            return {
                "verified": False,
                "message": f"Connection error: {conn_err}",
                "data": None
            }
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error occurred: {timeout_err}")
            return {
                "verified": False,
                "message": f"Timeout error: {timeout_err}",
                "data": None
            }
        except requests.exceptions.RequestException as req_err:
            print(f"An error occurred: {req_err}")
            return {
                "verified": False,
                "message": f"Request error: {req_err}",
                "data": None
            }

def show_dashboard():
    """Function to handle dashboard display"""
    print("\n=== Welcome to the Dashboard ===")
    print("User authenticated successfully!")
    print("You now have access to all features.")

# def main():
#     parser = argparse.ArgumentParser(description='License Verification Tool')
#     parser.add_argument('--test', action='store_true', help='Run in test mode')
#     args = parser.parse_args()

#     verifier = LicenseVerifier()
    
#     if args.test:
#         # Using the exact working credentials
#         license_key = "SOMEX4Y4ZLicenseKEY1732686454"
#         username = "1-bd7c6c56"
        
#         print("\nTesting license validation with:")
#         print(f"License Key: {license_key}")
#         print(f"Username: {username}")
        
#         result = verifier.validate_offline_license(license_key, username)
        
#         if result["verified"]:
#             print("\nTest validation successful!")
#             show_dashboard()
#         else:
#             print("\nTest validation failed!")
#             print(f"Error: {result['message']}")
#     else:
#         print("Please run with --test flag to test the license verification")

# if __name__ == "__main__":
#     main()
