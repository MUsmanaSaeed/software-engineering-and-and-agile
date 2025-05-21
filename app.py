from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'brickManagementSystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bricks.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    isAdmin = db.Column(db.Boolean, default=False, nullable=False)

class Manufacturer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    address = db.Column(db.String(250), nullable=False)
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

@app.before_request
def createTablesAndRequireLogin():
    db.create_all()
    # Require login for all routes except login, register, and static files
    allowedRoutes = ['login', 'register', 'static']
    if request.endpoint not in allowedRoutes and not session.get('userId'):
        return redirect(url_for('login', next=request.url))

def loginRequired(f):
    @wraps(f)
    def decoratedFunction(*args, **kwargs):
        if not session.get('userId'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decoratedFunction

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    userName = ''
    isAdmin = False
    if request.method == 'POST':
        userName = request.form['userName']
        password = request.form['password']
        isAdmin = bool(request.form.get('isAdmin'))

        if len(userName) < 5:
            flash('Username must be at least 5 characters long.', 'danger')
            return render_template('register.html', userName=userName, isAdmin=isAdmin)
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('register.html', userName=userName, isAdmin=isAdmin)

        if User.query.filter_by(userName=userName).first():
            flash('Username already exists.', 'danger')
            return render_template('register.html', userName=userName, isAdmin=isAdmin)

        hashedPassword = generate_password_hash(password, method='pbkdf2:sha256')
        newUser = User(userName=userName, password=hashedPassword, isAdmin=isAdmin)
        db.session.add(newUser)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', userName=userName, isAdmin=isAdmin)

@app.route('/login', methods=['GET', 'POST'])
def login():
    userName = ''
    if request.method == 'POST':
        userName = request.form['userName']
        password = request.form['password']
        user = User.query.filter_by(userName=userName).first()
        if user and check_password_hash(user.password, password):
            session['userId'] = user.id
            session['userName'] = user.userName
            session['isAdmin'] = user.isAdmin
            flash('Login successful!', 'success')
            nextUrl = request.args.get('next')
            return redirect(nextUrl) if nextUrl else redirect(url_for('index'))
        else:
            flash('Invalid credentials!', 'danger')
            return render_template('login.html', userName=userName)
    return render_template('login.html', userName=userName)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

# Manufacturer CRUD
@app.route('/manufacturers')
def manufacturers():
    allManufacturers = Manufacturer.query.all()
    return render_template('manufacturers.html', manufacturers=allManufacturers)

@app.route('/add_manufacturer', methods=['GET', 'POST'])
@loginRequired
def addManufacturer():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        if not name or not address:
            flash('All fields are required.', 'danger')
            return render_template('add_manufacturer.html')
        newManufacturer = Manufacturer(name=name, address=address)
        db.session.add(newManufacturer)
        db.session.commit()
        flash('Manufacturer added successfully!', 'success')
        return redirect(url_for('manufacturers'))
    return render_template('add_manufacturer.html')

@app.route('/edit_manufacturer/<int:id>', methods=['GET', 'POST'])
@loginRequired
def editManufacturer(id):
    manufacturer = Manufacturer.query.get_or_404(id)
    if request.method == 'POST':
        manufacturer.name = request.form['name']
        manufacturer.address = request.form['address']
        db.session.commit()
        flash('Manufacturer updated successfully!', 'success')
        return redirect(url_for('manufacturers'))
    return render_template('edit_manufacturer.html', manufacturer=manufacturer)

@app.route('/delete_manufacturer/<int:id>')
@loginRequired
def deleteManufacturer(id):
    if not session.get('isAdmin'):
        flash('Only admins can delete manufacturers.', 'danger')
        return redirect(url_for('manufacturers'))
    manufacturer = Manufacturer.query.get_or_404(id)
    db.session.delete(manufacturer)
    db.session.commit()
    flash('Manufacturer deleted successfully!', 'success')
    return redirect(url_for('manufacturers'))

# Brick CRUD
@app.route('/bricks')
def bricks():
    allBricks = Brick.query.all()
    return render_template('bricks.html', bricks=allBricks)

@app.route('/add_brick', methods=['GET', 'POST'])
@loginRequired
def addBrick():
    manufacturers = Manufacturer.query.all()
    if request.method == 'POST':
        name = request.form['name']
        colour = request.form['colour']
        material = request.form['material']
        strength = request.form['strength']
        width = float(request.form['width'])
        depth = float(request.form['depth'])
        height = float(request.form['height'])
        type_ = request.form['type']
        voids = int(request.form['voids'])
        manufacturerId = int(request.form['manufacturer_id'])
        newBrick = Brick(
            name=name, colour=colour, material=material, strength=strength,
            width=width, depth=depth, height=height, type=type_,
            voids=voids, manufacturerId=manufacturerId
        )
        db.session.add(newBrick)
        db.session.commit()
        flash('Brick added successfully!', 'success')
        return redirect(url_for('bricks'))
    return render_template('add_brick.html', manufacturers=manufacturers)

@app.route('/edit_brick/<int:id>', methods=['GET', 'POST'])
@loginRequired
def editBrick(id):
    brick = Brick.query.get_or_404(id)
    manufacturers = Manufacturer.query.all()
    if request.method == 'POST':
        brick.name = request.form['name']
        brick.colour = request.form['colour']
        brick.material = request.form['material']
        brick.strength = request.form['strength']
        brick.width = float(request.form['width'])
        brick.depth = float(request.form['depth'])
        brick.height = float(request.form['height'])
        brick.type = request.form['type']
        brick.voids = int(request.form['voids'])
        brick.manufacturerId = int(request.form['manufacturer_id'])
        db.session.commit()
        flash('Brick updated successfully!', 'success')
        return redirect(url_for('bricks'))
    return render_template('edit_brick.html', brick=brick, manufacturers=manufacturers)

@app.route('/delete_brick/<int:id>')
@loginRequired
def deleteBrick(id):
    brick = Brick.query.get_or_404(id)
    db.session.delete(brick)
    db.session.commit()
    flash('Brick deleted successfully!', 'success')
    return redirect(url_for('bricks'))

if __name__ == '__main__':
    app.run(debug=True)