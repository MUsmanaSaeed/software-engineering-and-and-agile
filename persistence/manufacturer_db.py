from models import db, Manufacturer

class ManufacturerDB:
    @staticmethod
    def get_by_id(manufacturer_id):
        return db.session.get(Manufacturer, manufacturer_id)

    @staticmethod
    def get_by_name(name):
        return Manufacturer.query.filter_by(name=name).first()

    @staticmethod
    def get_all():
        return Manufacturer.query.all()

    @staticmethod
    def add(manufacturer):
        db.session.add(manufacturer)
        db.session.commit()

    @staticmethod
    def delete(manufacturer):
        db.session.delete(manufacturer)
        db.session.commit()

    @staticmethod
    def commit():
        db.session.commit()
