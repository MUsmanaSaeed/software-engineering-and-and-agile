from persistence.brick_db import BrickDB
from models import Brick

class BrickMediator:
    @staticmethod
    def get_brick_by_id(brick_id):
        return BrickDB.get_by_id(brick_id)

    @staticmethod
    def get_all_bricks():
        return BrickDB.get_all()

    @staticmethod
    def add_brick(brick_data):
        # Example: check for duplicate name, etc.
        # Add business logic here
        brick = Brick(**brick_data)
        BrickDB.add(brick)
        return brick

    @staticmethod
    def delete_brick(brick_id):
        brick = BrickDB.get_by_id(brick_id)
        if brick:
            BrickDB.delete(brick)
            return True
        return False

    @staticmethod
    def duplicate_name_exists(name, exclude_id=None):
        # Case-insensitive duplicate check, optionally excluding a brick by id
        query = Brick.query.filter(Brick.name.ilike(name))
        if exclude_id:
            query = query.filter(Brick.id != exclude_id)
        return query.first() is not None

    @staticmethod
    def update_brick(brick, brick_data):
        for key, value in brick_data.items():
            setattr(brick, key, value)
        BrickDB.commit()
        return brick

    @staticmethod
    def delete_bricks_by_manufacturer(manufacturer_id):
        Brick.query.filter_by(manufacturerId=manufacturer_id).delete()
        BrickDB.commit()
