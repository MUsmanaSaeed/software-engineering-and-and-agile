from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'brick_management_system'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bricks.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

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
    manufacturer_id = db.Column(db.Integer, db.ForeignKey('manufacturer.id'), nullable=False)

@app.before_request
def create_tables_and_require_login():
    db.create_all()
    # Require login for all routes except login, register, and static files
    allowed_routes = ['login', 'register', 'static']
    if request.endpoint not in allowed_routes and not session.get('user_id'):
        return redirect(url_for('login', next=request.url))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    username = ''
    is_admin = False
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = bool(request.form.get('is_admin'))

        if len(username) < 5:
            flash('Username must be at least 5 characters long.', 'danger')
            return render_template('register.html', username=username, is_admin=is_admin)
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('register.html', username=username, is_admin=is_admin)

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('register.html', username=username, is_admin=is_admin)

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', username=username, is_admin=is_admin)

@app.route('/login', methods=['GET', 'POST'])
def login():
    username = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('Login successful!', 'success')
            next_url = request.args.get('next')
            return redirect(next_url) if next_url else redirect(url_for('index'))
        else:
            flash('Invalid credentials!', 'danger')
            return render_template('login.html', username=username)
    return render_template('login.html', username=username)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

# Manufacturer CRUD
@app.route('/manufacturers')
def manufacturers():
    all_manufacturers = Manufacturer.query.all()
    return render_template('manufacturers.html', manufacturers=all_manufacturers)

@app.route('/add_manufacturer', methods=['GET', 'POST'])
@login_required
def add_manufacturer():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        if not name or not address:
            flash('All fields are required.', 'danger')
            return render_template('add_manufacturer.html')
        new_manufacturer = Manufacturer(name=name, address=address)
        db.session.add(new_manufacturer)
        db.session.commit()
        flash('Manufacturer added successfully!', 'success')
        return redirect(url_for('manufacturers'))
    return render_template('add_manufacturer.html')

@app.route('/edit_manufacturer/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_manufacturer(id):
    manufacturer = Manufacturer.query.get_or_404(id)
    if request.method == 'POST':
        manufacturer.name = request.form['name']
        manufacturer.address = request.form['address']
        db.session.commit()
        flash('Manufacturer updated successfully!', 'success')
        return redirect(url_for('manufacturers'))
    return render_template('edit_manufacturer.html', manufacturer=manufacturer)

@app.route('/delete_manufacturer/<int:id>')
@login_required
def delete_manufacturer(id):
    if not session.get('is_admin'):
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
    all_bricks = Brick.query.all()
    return render_template('bricks.html', bricks=all_bricks)

@app.route('/add_brick', methods=['GET', 'POST'])
@login_required
def add_brick():
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
        manufacturer_id = int(request.form['manufacturer_id'])
        new_brick = Brick(
            name=name, colour=colour, material=material, strength=strength,
            width=width, depth=depth, height=height, type=type_,
            voids=voids, manufacturer_id=manufacturer_id
        )
        db.session.add(new_brick)
        db.session.commit()
        flash('Brick added successfully!', 'success')
        return redirect(url_for('bricks'))
    return render_template('add_brick.html', manufacturers=manufacturers)

@app.route('/edit_brick/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_brick(id):
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
        brick.manufacturer_id = int(request.form['manufacturer_id'])
        db.session.commit()
        flash('Brick updated successfully!', 'success')
        return redirect(url_for('bricks'))
    return render_template('edit_brick.html', brick=brick, manufacturers=manufacturers)

@app.route('/delete_brick/<int:id>')
@login_required
def delete_brick(id):
    brick = Brick.query.get_or_404(id)
    db.session.delete(brick)
    db.session.commit()
    flash('Brick deleted successfully!', 'success')
    return redirect(url_for('bricks'))

if __name__ == '__main__':
    app.run(debug=True)