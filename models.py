from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    isAdmin = db.Column(db.Boolean, default=False, nullable=False)

class Manufacturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    address = db.Column(db.String(250), nullable=False)
    phoneNo = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    bricks = db.relationship('Brick', backref='manufacturer', lazy=True)

class Brick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    colour = db.Column(db.String(50), nullable=False)
    material = db.Column(db.String(100), nullable=False)
    strength = db.Column(db.String(50), nullable=False)
    width = db.Column(db.Float, nullable=False)
    depth = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(100), nullable=False)
    voids = db.Column(db.Integer, nullable=False)
    manufacturerId = db.Column(db.Integer, db.ForeignKey('manufacturer.id'), nullable=False)
