from .db import Database
from typing import Optional, List
from .models import User, StatementInfo, Case, Entity, MergedGroup
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

class UserRepository:
    def __init__(self):
        """
        Initializes the UserRepository with a database session.
        :param session: SQLAlchemy Session object
        """
        self.session = Database.get_session()

    def get_user(self) -> List[User]:
        """
        Retrieves all users.
        :return: List of all User objects
        """
        return self.session.query(User).all()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieves a user by their ID.
        :param user_id: ID of the user to retrieve
        :return: User object if found, None otherwise
        """
        return self.session.query(User).filter_by(id=user_id).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Retrieves a user by their username.
        :param username: Username of the user to retrieve
        :return: User object if found, None otherwise
        """
        return self.session.query(User).filter_by(username=username).first()
    

    def get_user_by_username_and_password(self, username: str, password: str) -> Optional[User]:
        """
        Retrieves a user by their username and password.
        :param username: Username of the user to retrieve
        :param password: Password of the user to retrieve
        :return: User object if found, None otherwise
        """
        return self.session.query(User).filter_by(username=username, password=password).first()


    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieves a user by their email address.
        :param email: Email of the user to retrieve
        :return: User object if found, None otherwise
        """
        return self.session.query(User).filter_by(email=email).first()

    def create_user(self, user_data: dict) -> Optional[User]:
        """
        Creates a new user.
        :param user_data: Dictionary containing user details
        :return: The created User object if successful, None otherwise
        """
        try:
            user = User(**user_data)
            self.session.add(user)
            self.session.commit()

            print("User created successfully:", user)
            return user
        except IntegrityError as e:
            self.session.rollback()
            print(f"Error creating user: {e}")
            return None

    def update_user(self, user: User, updated_data: dict) -> Optional[User]:
        """
        Updates an existing user's details.
        :param user: User object to update
        :param updated_data: Dictionary of updated details
        :return: Updated User object
        """
        for key, value in updated_data.items():
            setattr(user, key, value)
        try:
            self.session.commit()
            return user
        except Exception as e:
            self.session.rollback()
            print(f"Error updating user: {e}")
            return None

    def delete_user(self, user: User) -> bool:
        """
        Deletes a user.
        :param user: User object to delete
        :return: True if successful, False otherwise
        """
        try:
            self.session.delete(user)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error deleting user: {e}")
            return False

class StatementInfoRepository:
    def __init__(self):
        """
        Initializes the repository with a session from the Database singleton.
        """
        self.session: Session = Database.get_session()

    def get_statement_info(self) -> List[StatementInfo]:
        """
        Retrieves all statement information records.
        :return: List of all StatementInfo objects
        """
        return self.session.query(StatementInfo).all()

    def create_statement_info(self, statement_info_data: dict) -> Optional[StatementInfo]:
        """
        Creates a new statement information record.
        :param statement_info_data: Dictionary containing statement information details
        :return: The created StatementInfo object if successful, None otherwise
        """
        try:
            statement_info = StatementInfo(**statement_info_data)
            self.session.add(statement_info)
            self.session.commit()
            print("Statement info created successfully:", statement_info)
            return statement_info
        except IntegrityError as e:
            self.session.rollback()
            print(f"Error creating statement info: {e}")
            return None

    def update_statement_info(self, statement_info: StatementInfo, updated_data: dict) -> Optional[StatementInfo]:
        """
        Updates an existing statement information record.
        :param statement_info: StatementInfo object to update
        :param updated_data: Dictionary of updated details
        :return: Updated StatementInfo object
        """
        for key, value in updated_data.items():
            setattr(statement_info, key, value)
        try:
            self.session.commit()
            return statement_info
        except Exception as e:
            self.session.rollback()
            print(f"Error updating statement info: {e}")
            return None

    def delete_statement_info(self, statement_info: StatementInfo) -> bool:
        """
        Deletes a statement information record.
        :param statement_info: StatementInfo object to delete
        :return: True if successful, False otherwise
        """
        try:
            self.session.delete(statement_info)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error deleting statement info: {e}")
            return False

    def get_statement_info_by_id(self, statement_info_id: int) -> Optional[StatementInfo]:
        """
        Retrieves a statement information record by its ID.
        :param statement_info_id: ID of the statement information record
        :return: StatementInfo object if found, None otherwise
        """
        return self.session.query(StatementInfo).filter_by(id=statement_info_id).first()

    def get_statement_info_by_case_id(self, case_id: int) -> List[StatementInfo]:
        """
        Retrieves statement information records associated with a specific case ID.
        :param case_id: Case ID to filter by
        :return: List of StatementInfo objects
        """
        return self.session.query(StatementInfo).filter_by(case_id=case_id).all()


class EntityRepository:
    def __init__(self):
        """
        Initializes the repository with a session from the Database singleton.
        """
        self.session: Session = Database.get_session()

    def get_entity_by_id(self, entity_id: int) -> Optional[Entity]:
        """
        Retrieves an entity by its ID.
        :param entity_id: ID of the entity
        :return: Entity object if found, None otherwise
        """
        return self.session.query(Entity).filter_by(id=entity_id).first()

    def create_entity(self, entity_data: dict) -> Optional[Entity]:
        """
        Creates a new entity record.
        :param entity_data: Dictionary containing entity details
        :return: The created Entity object if successful, None otherwise
        """
        try:
            entity = Entity(**entity_data)
            self.session.add(entity)
            self.session.commit()
            return entity
        except IntegrityError as e:
            self.session.rollback()
            print(f"Error creating entity: {e}")
            return None

    def update_entity(self, entity: Entity, updated_data: dict) -> Optional[Entity]:
        """
        Updates an existing entity record.
        :param entity: Entity object to update
        :param updated_data: Dictionary of updated details
        :return: Updated Entity object if successful, None otherwise
        """
        for key, value in updated_data.items():
            setattr(entity, key, value)
        try:
            self.session.commit()
            return entity
        except Exception as e:
            self.session.rollback()
            print(f"Error updating entity: {e}")
            return None

    def delete_entity(self, entity: Entity) -> bool:
        """
        Deletes an entity record.
        :param entity: Entity object to delete
        :return: True if successful, False otherwise
        """
        try:
            self.session.delete(entity)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error deleting entity: {e}")
            return False

    def get_entity_by_case_id(self, case_id: int) -> List[Entity]:
        """
        Retrieves all entities associated with a specific case ID.
        :param case_id: Case ID to filter by
        :return: List of Entity objects
        """
        return self.session.query(Entity).filter_by(case_id=case_id).all()

    def get_entity_by_entity_id(self, entity_id: int) -> List[Entity]:
        """
        Retrieves entities by their entity ID.
        :param entity_id: Entity ID to filter by
        :return: List of Entity objects
        """
        return self.session.query(Entity).filter_by(entity_id=entity_id).all()



class CaseRepository:

    def __init__(self):
        """
        Initializes the repository with a session from the Database singleton.
        """
        self.session: Session = Database.get_session()

    def get_case_by_id(self, case_id: int) -> Optional[Case]:
        """
        Retrieves a case by its ID.
        :param case_id: ID of the case
        :return: Case object if found, None otherwise
        """
        return self.session.query(Case).filter_by(case_id=case_id).first()
    
    def create_case(self, case_data: dict) -> Optional[Case]:
        """
        Creates a new case record.
        :param case_data: Dictionary containing case details
        :return: The created Case object if successful, None otherwise
        """
        try:
            case = Case(**case_data)
            self.session.add(case)
            self.session.commit()
            return case
        except IntegrityError as e:
            self.session.rollback()
            print(f"Error creating case: {e}")
            return None
        
    def update_case(self, case: Case, updated_data: dict) -> Optional[Case]:
        """
        Updates an existing case record.
        :param case: Case object to update
        :param updated_data: Dictionary of updated details
        :return: Updated Case object if successful, None otherwise
        """
        for key, value in updated_data.items():
            setattr(case, key, value)
        try:
            self.session.commit()
            return case
        except Exception as e:
            self.session.rollback()
            print(f"Error updating case: {e}")
            return None
        
    def delete_case(self, case: Case) -> bool:
        """
        Deletes a case record.
        :param case: Case object to delete
        :return: True if successful, False otherwise
        """
        try:
            self.session.delete(case)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"Error deleting case: {e}")
            return False
        

class MergedEntitiesRepository:

    def __init__(self):
        """
        Initializes the repository with a session from the Database singleton.
        """
        self.session: Session = Database.get_session()

    def get_merged_entities_by_id(self, merged_entity_id) -> List[MergedGroup]:
        """
        Retrieves merged entities by their entity IDs.
        :return: List of MergedEntities objects
        """
        return self.session.query(MergedGroup).filter_by(id=merged_entity_id).first()
        
    def get_merged_entities_by_case_id(self, case_id: int) -> List[MergedGroup]:
        """
        Retrieves merged entities by their case ID.
        :param case_id: Case ID to filter by
        :return: List of MergedEntities objects
        """
        return self.session.query(MergedGroup).filter_by(case_id=case_id).all()
    
    def create_merged_entities(self, merged_group_data: dict) -> Optional[MergedGroup]:
        """
        Creates a new merged entities record.
        :param merged_entities_data: Dictionary containing merged entities details
        :return: The created MergedEntities object if successful, None otherwise
        """
        
        try:
            merged_entities = MergedGroup(**merged_group_data)
            self.session.add(merged_entities)
            self.session.commit()
            return merged_entities
        except IntegrityError as e:
            self.session.rollback()
            print(f"Error creating merged entities: {e}")
            return None
