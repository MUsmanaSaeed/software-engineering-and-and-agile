from persistence.manufacturer_db import ManufacturerDB
from models import Manufacturer
import re

class ManufacturerMediator:
    @staticmethod
    def get_manufacturer_by_id(manufacturer_id):
        return ManufacturerDB.get_by_id(manufacturer_id)

    @staticmethod
    def get_manufacturer_by_name(name):
        return ManufacturerDB.get_by_name(name)

    @staticmethod
    def get_all_manufacturers():
        return ManufacturerDB.get_all()

    @staticmethod
    def __add_manufacturer(manufacturer_data):
        # Add business logic here
        manufacturer = Manufacturer(**manufacturer_data)
        ManufacturerDB.add(manufacturer)
        return manufacturer

    @staticmethod
    def duplicate_name_exists(name, exclude_id=None):
        query = Manufacturer.query.filter(Manufacturer.name.ilike(name))
        if exclude_id:
            query = query.filter(Manufacturer.id != exclude_id)
        return query.first() is not None

    @staticmethod
    def __update_manufacturer(manufacturer, manufacturer_data):
        for key, value in manufacturer_data.items():
            setattr(manufacturer, key, value)
        ManufacturerDB.commit()
        return manufacturer

    @staticmethod
    def __delete_manufacturer(manufacturer_id, is_admin):
        manufacturer = ManufacturerDB.get_by_id(manufacturer_id)
        if not manufacturer:
            return False
        has_bricks = len(manufacturer.bricks) > 0
        if has_bricks and not is_admin:
            return 'admin_required'
        from mediators.brick_mediator import BrickMediator
        BrickMediator.delete_bricks_by_manufacturer(manufacturer.id)
        ManufacturerDB.delete(manufacturer)
        return True

    @staticmethod
    def get_next_manufacturer():
        return Manufacturer.query.order_by(Manufacturer.id).first()

    @staticmethod
    def _is_valid_email(email):
        # Simple regex for email validation
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return bool(email) and re.match(pattern, email) is not None

    @staticmethod
    def _is_valid_phone(phone):
        # Accepts numbers, spaces, dashes, parentheses, and plus sign, 7-20 chars
        if not phone:
            return False
        pattern = r"^[\d\s\-\(\)\+]{7,20}$"
        return re.match(pattern, phone) is not None

    @staticmethod
    def add_manufacturer_with_checks(form_data):
        name = form_data.get('name')
        address = form_data.get('address')
        phoneNo = form_data.get('phoneNo', '')
        email = form_data.get('email', '')
        if not name:
            return {'error': 'Name is required.'}
        if ManufacturerMediator.duplicate_name_exists(name):
            return {'error': 'A manufacturer with this name already exists.'}
        if not ManufacturerMediator._is_valid_email(email):
            return {'error': 'A valid email address is required.'}
        if not ManufacturerMediator._is_valid_phone(phoneNo):
            return {'error': 'A valid phone number is required (7-20 digits, may include spaces, dashes, parentheses, +).'}
        manufacturer_data = {
            'name': name,
            'address': address,
            'phoneNo': phoneNo,
            'email': email
        }
        manufacturer = ManufacturerMediator.__add_manufacturer(manufacturer_data)
        return {'manufacturer': manufacturer}

    @staticmethod
    def update_manufacturer_with_checks(manufacturer, form_data):
        name = form_data.get('name')
        address = form_data.get('address')
        phoneNo = form_data.get('phoneNo', '')
        email = form_data.get('email', '')
        if not name:
            return {'error': 'Name is required.'}
        if ManufacturerMediator.duplicate_name_exists(name, exclude_id=manufacturer.id):
            return {'error': 'A manufacturer with this name already exists.'}
        if not ManufacturerMediator._is_valid_email(email):
            return {'error': 'A valid email address is required.'}
        if not ManufacturerMediator._is_valid_phone(phoneNo):
            return {'error': 'A valid phone number is required (7-20 digits, may include spaces, dashes, parentheses, +).'}
        manufacturer_data = {
            'name': name,
            'address': address,
            'phoneNo': phoneNo,
            'email': email
        }
        updated = ManufacturerMediator.__update_manufacturer(manufacturer, manufacturer_data)
        return {'manufacturer': updated}

    @staticmethod
    def delete_manufacturer_with_checks(manufacturer_id, is_admin):
        result = ManufacturerMediator.__delete_manufacturer(manufacturer_id, is_admin)
        if result == 'admin_required':
            return {'error': 'Only admins can delete manufacturers with bricks.'}
        return {'success': True}

    @staticmethod
    def get_next_manufacturer_id():
        next_manufacturer = ManufacturerMediator.get_next_manufacturer()
        return next_manufacturer.id if next_manufacturer else None
