from models import db, BrickOrder
from sqlalchemy.orm import joinedload

class BrickOrderDB:
    @staticmethod
    def get_by_id(order_id):
        return BrickOrder.query.options(joinedload(BrickOrder.brick)).get(order_id)

    @staticmethod
    def get_by_order_no(order_no):
        return BrickOrder.query.options(joinedload(BrickOrder.brick)).filter_by(orderNo=order_no).all()

    @staticmethod
    def get_all():
        return BrickOrder.query.options(joinedload(BrickOrder.brick)).all()

    @staticmethod
    def add(order):
        db.session.add(order)
        db.session.commit()

    @staticmethod
    def delete(order):
        db.session.delete(order)
        db.session.commit()

    @staticmethod
    def commit():
        db.session.commit()
