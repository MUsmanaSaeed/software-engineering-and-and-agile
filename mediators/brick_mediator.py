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
        # Validate required fields
        required_fields = ['name', 'colour', 'material', 'strength', 'width', 'depth', 'height', 'type', 'voids', 'manufacturer_id']
        for field in required_fields:
            if field not in brick_data or brick_data[field] == '':
                raise ValueError(f"Field '{field}' is required.")
        # Duplicate name check
        name = brick_data['name']
        if BrickMediator.duplicate_name_exists(name):
            raise ValueError('A brick with this name already exists.')
        # Type conversions and value checks
        try:
            brick_data['width'] = float(brick_data['width'])
            brick_data['depth'] = float(brick_data['depth'])
            brick_data['height'] = float(brick_data['height'])
            brick_data['voids'] = int(brick_data['voids'])
            brick_data['manufacturerId'] = int(brick_data['manufacturer_id'])
        except Exception:
            raise ValueError('Invalid data type for one or more fields.')
        # Additional checks
        if brick_data['width'] <= 0:
            raise ValueError('Width must be greater than 0.')
        if brick_data['depth'] <= 0:
            raise ValueError('Depth must be greater than 0.')
        if brick_data['height'] <= 0:
            raise ValueError('Height must be greater than 0.')
        if not (0 <= brick_data['voids'] <= 100):
            raise ValueError('Voids must be between 0 and 100.')
        # Remove form field
        brick_data.pop('manufacturer_id', None)
        brick = Brick(**brick_data)
        BrickDB.add(brick)
        return brick

    @staticmethod
    def update_brick(brick, brick_data):
        # Validate required fields
        required_fields = ['name', 'colour', 'material', 'strength', 'width', 'depth', 'height', 'type', 'voids', 'manufacturer_id']
        for field in required_fields:
            if field not in brick_data or brick_data[field] == '':
                raise ValueError(f"Field '{field}' is required.")
        # Duplicate name check (exclude self)
        name = brick_data['name']
        if BrickMediator.duplicate_name_exists(name, exclude_id=brick.id):
            raise ValueError('A brick with this name already exists.')
        # Type conversions and value checks
        try:
            brick_data['width'] = float(brick_data['width'])
            brick_data['depth'] = float(brick_data['depth'])
            brick_data['height'] = float(brick_data['height'])
            brick_data['voids'] = int(brick_data['voids'])
            brick_data['manufacturerId'] = int(brick_data['manufacturer_id'])
        except Exception:
            raise ValueError('Invalid data type for one or more fields.')
        # Additional checks
        if brick_data['width'] <= 0:
            raise ValueError('Width must be greater than 0.')
        if brick_data['depth'] <= 0:
            raise ValueError('Depth must be greater than 0.')
        if brick_data['height'] <= 0:
            raise ValueError('Height must be greater than 0.')
        if not (0 <= brick_data['voids'] <= 100):
            raise ValueError('Voids must be between 0 and 100.')
        # Remove form field
        brick_data.pop('manufacturer_id', None)
        for key, value in brick_data.items():
            setattr(brick, key, value)
        BrickDB.commit()
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
    def delete_bricks_by_manufacturer(manufacturer_id):
        Brick.query.filter_by(manufacturerId=manufacturer_id).delete()
        BrickDB.commit()
