import keyring
print("Keyring Backend in Use:", keyring.get_keyring())

class LicenseManager:
    @staticmethod
    def store_license_key(license_key: str):
        # Store the license key securely under a fixed identifier 'Cyphersol_license_key'
        keyring.set_password("Cyphersol", "license_key", license_key)
        print("License key stored securely.")

    @staticmethod
    def get_license_key() -> str:
        # Retrieve the license key from the system keyring
        license_key = keyring.get_password("Cyphersol", "license_key")
        print("License Key present: ", license_key)
        if license_key:
            return license_key
        return None

# keyring.delete_password("Cyphersol", "license_key")