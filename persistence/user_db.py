from models import db, User

class UserDB:
    @staticmethod
    def get_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def get_by_username(username):
        return User.query.filter_by(userName=username).first()

    @staticmethod
    def get_all():
        return User.query.all()

    @staticmethod
    def add(user):
        db.session.add(user)
        db.session.commit()

    @staticmethod
    def delete(user):
        db.session.delete(user)
        db.session.commit()

    @staticmethod
    def commit():
        db.session.commit()
