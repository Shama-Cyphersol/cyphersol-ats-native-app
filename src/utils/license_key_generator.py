import random
import string
import logging
import hashlib
import hmac
import base64
from typing import List, Tuple
from datetime import datetime, timedelta
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

SECRET_KEY = "SSKSJKFKNVIVVNRNIRNV003"

class LicenseKeyManager:
    def __init__(self, secret_key: str = SECRET_KEY):
        self.secret_key = secret_key.encode('utf-8')
    
    def _generate_signature(self, data: str) -> str:
        h = hmac.new(self.secret_key, data.encode('utf-8'), hashlib.sha256)
        return base64.b64encode(h.digest()).decode('utf-8')[:8]
    
    def generate_license_keys(self, num_keys: int = 1, days_valid: int = 365) -> List[Tuple[str, datetime]]:
        try:
            if num_keys < 1:
                logger.error("Number of keys must be at least 1")
                return []

            expiration_date = datetime.now() + timedelta(days=days_valid)
            exp_date_str = expiration_date.strftime("%Y%m")
            
            license_keys = []
            for _ in range(num_keys):
                random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
                base_data = f"{random_chars}{exp_date_str}"
                signature = self._generate_signature(base_data)
                parts = [
                    base_data[:4],
                    base_data[4:8],
                    base_data[8:12],
                    exp_date_str,
                    signature[:4]
                ]
                license_key = '-'.join(parts)
                license_keys.append((license_key, expiration_date))
                logger.info(f"Generated license key: {license_key} (expires: {expiration_date})")
            
            return license_keys
        
        except Exception as e:
            logger.error(f"Error generating license keys: {e}")
            return []
    
    def verify_license_key(self, license_key: str) -> bool:
        try:
            parts = license_key.replace('-', '')
            if len(parts) != 24:
                return False
            
            base_data = parts[:18]
            provided_signature = parts[18:]
            expected_signature = self._generate_signature(base_data)[:6]
            
            if provided_signature != expected_signature:
                logger.warning("Invalid license key signature")
                return False
            
            exp_date_str = parts[12:18]
            exp_date = datetime.strptime(exp_date_str, "%Y%m")
            
            if datetime.now() > exp_date:
                logger.warning("License key has expired")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying license key: {e}")
            return False

if __name__ == "__main__":
    manager = LicenseKeyManager()
    
    print("\nGenerating new license keys:")
    keys = manager.generate_license_keys(num_keys=3, days_valid=30)
    for key, exp_date in keys:
        print(f"Key: {key}")
        print(f"Expires: {exp_date}")
        
        is_valid = manager.verify_license_key(key)
        print(f"Verification: {'Valid' if is_valid else 'Invalid'}\n")
