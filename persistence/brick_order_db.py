from models import db, BrickOrder

class BrickOrderDB:
    @staticmethod
    def get_by_id(order_id):
        return BrickOrder.query.get(order_id)

    @staticmethod
    def get_by_order_no(order_no):
        return BrickOrder.query.filter_by(orderNo=order_no).all()

    @staticmethod
    def get_all():
        return BrickOrder.query.all()

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
