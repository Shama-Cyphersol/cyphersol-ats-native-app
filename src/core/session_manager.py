from ..core.repository import UserRepository

class SessionManager:
    _current_user = None  # Class-level variable to store the current user

    @classmethod
    def login_user(cls, user):
        """
        Logs in the user by storing their information in a class-level variable.
        :param user: A dictionary or user object with user details
        """


        cls._current_user = user
        print("User logged in successfully!", user.email, user.username)

    @classmethod
    def get_current_user(cls):
        """
        Retrieves the currently logged-in user.
        :return: The logged-in user or None if no user is logged in
        """
        return cls._current_user

    @classmethod
    def logout_user(cls):
        """
        Logs out the current user by clearing the class-level variable.
        """
        cls._current_user = None

    @classmethod
    def is_authenticated(cls):
        """
        Checks if a user is currently logged in.
        :return: True if a user is logged in, False otherwise
        """
        return cls._current_user is not None
    
    @classmethod
    def authenticate_user(cls, username, password):
        """
        Authenticates a user by checking their email and password.
        :param email: The email of the user
        :param password: The password of the user
        :return: True if the user is authenticated, False otherwise
        """
        user_repo = UserRepository()
        user = user_repo.get_user_by_username_and_password(username=username, password=password)

        if user:
            return user
        
        return None
