from ..core.repository import UserRepository
import os
import json
from cryptography.fernet import Fernet
from appdirs import user_data_dir

class SessionManager:
    _current_user = None  # Class-level variable to store the current user
    _session_file = os.path.join(user_data_dir("CyphersolApp", "Cyphersol"), "session_data.json")
    _key = b'BViQkhY8z7IvWf7peLlUuLEqU9IpoL5i5tI-Xmb1NKo='
    _cipher = Fernet(_key)

    @classmethod
    def login_user(cls, user):
        """
        Logs in the user by storing their information in a class-level variable and saving it to disk.
        :param user: A dictionary or user object with user details
        """
        cls._current_user = user

        user_info = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }

        # print(f"User logged in successfully! Username: {user['username']}, Email: {user['email']}")
        cls._save_session_to_disk(user)

    @classmethod
    def get_current_user(cls):
        """
        Retrieves the currently logged-in user.
        :return: The logged-in user or None if no user is logged in
        """
        if cls._current_user is None:
            cls._current_user = cls._load_session_from_disk()
        return cls._current_user

    @classmethod
    def logout_user(cls):
        """
        Logs out the current user by clearing the class-level variable and deleting the session file.
        """
        cls._current_user = None
        cls._clear_session_on_disk()
        print("User logged out successfully!")

    @classmethod
    def is_authenticated(cls):
        """
        Checks if a user is currently logged in.
        :return: True if a user is logged in, False otherwise
        """
        return cls.get_current_user() is not None

    @classmethod
    def authenticate_user(cls, username, password):
        """
        Authenticates a user by checking their username and password.
        :param username: The username of the user
        :param password: The password of the user
        :return: The user object if authenticated, None otherwise
        """
        user_repo = UserRepository()
        user = user_repo.get_user_by_username_and_password(username=username, password=password)

        if user:
            return user
        return None

    @classmethod
    def is_logged_in(cls):
        """
        Checks if a session already exists on disk.
        :return: True if a session file exists and can be decrypted, False otherwise
        """
        try:
            if os.path.exists(cls._session_file):
                cls._current_user = cls._load_session_from_disk()
                return cls._current_user is not None
        except Exception as e:
            print(f"Error checking session: {e}")
        return False

    @classmethod
    def _save_session_to_disk(cls, user_data):
        """
        Encrypt and save the user session to a file.
        :param user_data: The user data to save
        """
        try:
            os.makedirs(os.path.dirname(cls._session_file), exist_ok=True)
            encrypted_data = cls._cipher.encrypt(json.dumps(user_data).encode())
            with open(cls._session_file, "wb") as file:
                file.write(encrypted_data)
        except Exception as e:
            print(f"Error saving session: {e}")

    @classmethod
    def _load_session_from_disk(cls):
        """
        Load and decrypt the user session from a file.
        :return: The decrypted session data or None if not found
        """
        try:
            if os.path.exists(cls._session_file):
                with open(cls._session_file, "rb") as file:
                    encrypted_data = file.read()
                    data = cls._cipher.decrypt(encrypted_data).decode()
                    return json.loads(data)
        except Exception as e:
            print(f"Error loading session: {e}")
        return None

    @classmethod
    def _clear_session_on_disk(cls):
        """
        Clear the saved session file from disk.
        """
        try:
            if os.path.exists(cls._session_file):
                os.remove(cls._session_file)
        except Exception as e:
            print(f"Error clearing session: {e}")