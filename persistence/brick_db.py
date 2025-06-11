from models import db, Brick

class BrickDB:
    @staticmethod
    def get_by_id(brick_id):
        return Brick.query.get(brick_id)

    @staticmethod
    def get_all():
        return Brick.query.all()

    @staticmethod
    def add(brick):
        db.session.add(brick)
        db.session.commit()

    @staticmethod
    def delete(brick):
        db.session.delete(brick)
        db.session.commit()

    @staticmethod
    def commit():
        db.session.commit()
