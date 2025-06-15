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
    def validate_user_data(user_data, is_edit=False, current_user=None, session_user_id=None):
        error_fields = []
        error_messages = []
        userName = user_data.get('userName', '')
        password = user_data.get('password', None)
        isAdmin = user_data.get('isAdmin', False)
        # Username length check
        if len(userName) < 3:
            error_fields.append('userName')
            error_messages.append('Username must be at least 3 characters long.')
        # Password length check (only if provided or not editing)
        if (not is_edit or (password is not None and password != '')) and (not password or len(password) < 8):
            error_fields.append('password')
            error_messages.append('Password must be at least 8 characters long.')
        # Duplicate username check
        if not is_edit or (current_user and current_user.userName != userName):
            if UserMediator.duplicate_username_exists(userName, exclude_id=current_user.id if current_user else None):
                if 'userName' not in error_fields:
                    error_fields.append('userName')
                error_messages.append('Username already exists.')
        # Admin self-removal check
        if is_edit and current_user and session_user_id and current_user.id == session_user_id and not isAdmin:
            error_fields.append('isAdmin')
            error_messages.append('Admins cannot remove their own admin rights.')
        # Prevent registration as admin
        if not is_edit and isAdmin:
            error_fields.append('isAdmin')
            error_messages.append('Cannot register as admin.')
        if error_fields:
            return False, error_messages, error_fields
        return True, [], []

    @staticmethod
    def add_user(user_data, by_admin=False):
        # Determine if admin creation is allowed
        allow_admin = by_admin and user_data.get('isAdmin', False)
        # For admin creation by admin, validate as normal user (isAdmin=False) to skip the 'Cannot register as admin.' error
        validate_data = {**user_data, 'isAdmin': False} if allow_admin else user_data
        valid, error_messages, error_fields = UserMediator.validate_user_data(validate_data)
        if not valid:
            return False, None, error_messages, error_fields
        from werkzeug.security import generate_password_hash
        user_data['password'] = generate_password_hash(user_data['password'])
        user = User(
            userName=user_data['userName'],
            password=user_data['password'],
            isAdmin=allow_admin or user_data.get('isAdmin', False)
        )
        UserDB.add(user)
        return True, user, [], []

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
    def update_user(user, user_data, session_user_id=None):
        valid, error_messages, error_fields = UserMediator.validate_user_data(
            user_data, is_edit=True, current_user=user, session_user_id=session_user_id
        )
        if not valid:
            return False, None, error_messages, error_fields
        from werkzeug.security import generate_password_hash
        user.userName = user_data['userName']
        user.isAdmin = user_data['isAdmin']
        if user_data.get('password'):
            user.password = generate_password_hash(user_data['password'])
        UserDB.commit()
        return True, user, [], []

    @staticmethod
    def add_admin_user(user_data):
        # Deprecated: use add_user(user_data, by_admin=True) instead
        return UserMediator.add_user(user_data, by_admin=True)
