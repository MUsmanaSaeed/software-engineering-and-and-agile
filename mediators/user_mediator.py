from persistence.user_db import UserDB
from models import User

class UserMediator:
    @staticmethod
    def get_user_by_id(user_id):
        return UserDB.get_by_id(user_id)

    @staticmethod
    def get_user_by_username(username):
        return UserDB.get_by_username(username)

    @staticmethod
    def get_all_users():
        return UserDB.get_all()

    @staticmethod
    def add_user(user_data):
        # Add business logic here
        user = User(**user_data)
        UserDB.add(user)
        return user

    @staticmethod
    def delete_user(user_id):
        user = UserDB.get_by_id(user_id)
        if user:
            UserDB.delete(user)
            return True
        return False

    @staticmethod
    def duplicate_username_exists(username, exclude_id=None):
        query = User.query.filter(User.userName.ilike(username))
        if exclude_id:
            query = query.filter(User.id != exclude_id)
        return query.first() is not None

    @staticmethod
    def update_user(user, user_data):
        for key, value in user_data.items():
            if value is not None:
                setattr(user, key, value)
        UserDB.commit()
        return user
