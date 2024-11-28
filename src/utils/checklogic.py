import logging
import wmi #windows management instrumentation
import platform #it is useful for getting all the system level information
from typing import List , Optional

logging.basicConfig(
    level=logging.INFO,
    format = '%(asctime)s - %(levelname)s - %(message)s',
    handlers = [logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class LicenseVerifier:
    def __init__(self):
        try:
            self.wmi_client = wmi.WMI()
            print("The client was initialised")
        except Exception as e:
            self.wmi_client = None
            print(f"There has been an exception :{e}")
    

    def _get_system_info(self) -> List[str]:
        try:
            system_info = [
                platform.node(),
                platform.machine(),
                platform.processor(),
            ]
        
            logger.info(f"System info collected : {system_info}")
            return system_info
        except Exception as e:
            logger.error("Working on it")
        

verifier = LicenseVerifier()
system = verifier._get_system_info()
print(system)