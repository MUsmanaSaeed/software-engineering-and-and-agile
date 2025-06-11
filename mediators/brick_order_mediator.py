from persistence.brick_order_db import BrickOrderDB
from models import BrickOrder

class BrickOrderMediator:
    @staticmethod
    def get_order_by_id(order_id):
        return BrickOrderDB.get_by_id(order_id)

    @staticmethod
    def get_orders_by_order_no(order_no):
        return BrickOrderDB.get_by_order_no(order_no)

    @staticmethod
    def get_all_orders():
        return BrickOrderDB.get_all()

    @staticmethod
    def add_order(order_data):
        # Add business logic here
        order = BrickOrder(**order_data)
        BrickOrderDB.add(order)
        return order

    @staticmethod
    def delete_order(order_id):
        order = BrickOrderDB.get_by_id(order_id)
        if order:
            BrickOrderDB.delete(order)
            return True
        return False

    @staticmethod
    def get_all_order_nos():
        from models import db, BrickOrder
        return [o[0] for o in db.session.query(BrickOrder.orderNo).distinct().all()]

    @staticmethod
    def mark_received(order_id):
        order = BrickOrderDB.get_by_id(order_id)
        if order:
            order.bricks_received = order.bricks_ordered
            from datetime import datetime
            order.received_date = datetime.today().date()
            BrickOrderDB.commit()
            return True
        return False

    @staticmethod
    def cancel_order(order_id):
        order = BrickOrderDB.get_by_id(order_id)
        if order:
            from datetime import datetime
            order.canceled_date = datetime.today().date()
            BrickOrderDB.commit()
            return True
        return False
