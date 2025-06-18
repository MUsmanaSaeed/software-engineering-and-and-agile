from models import db, BrickOrder
from sqlalchemy.orm import joinedload

class BrickOrderDB:
    @staticmethod
    def get_by_id(order_id):
        order = db.session.get(BrickOrder, order_id)
        if order:
            db.session.refresh(order, ['brick'])
        return order

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
