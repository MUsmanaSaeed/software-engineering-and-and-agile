from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'brick_management_system'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bricks.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Brick(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    username = ''
    role = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        # Username and password length validation
        if len(username) < 5:
            flash('Username must be at least 5 characters long.', 'danger')
            return render_template('register.html', username=username, role=role)
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('register.html', username=username, role=role)

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', username=username, role=role)

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
            session['role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials!', 'danger')
            return render_template('login.html', username=username)
    return render_template('login.html', username=username)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/bricks')
def bricks():
    all_bricks = Brick.query.all()
    return render_template('bricks.html', bricks=all_bricks)

@app.route('/add_brick', methods=['GET', 'POST'])
def add_brick():
    if request.method == 'POST':
        name = request.form['name']
        color = request.form['color']
        quantity = request.form['quantity']
        new_brick = Brick(name=name, color=color, quantity=quantity)
        db.session.add(new_brick)
        db.session.commit()
        flash('Brick added successfully!', 'success')
        return redirect(url_for('bricks'))
    return render_template('add_brick.html')

@app.route('/edit_brick/<int:id>', methods=['GET', 'POST'])
def edit_brick(id):
    brick = Brick.query.get_or_404(id)
    if request.method == 'POST':
        brick.name = request.form['name']
        brick.color = request.form['color']
        brick.quantity = request.form['quantity']
        db.session.commit()
        flash('Brick updated successfully!', 'success')
        return redirect(url_for('bricks'))
    return render_template('edit_brick.html', brick=brick)

@app.route('/delete_brick/<int:id>')
def delete_brick(id):
    brick = Brick.query.get_or_404(id)
    db.session.delete(brick)
    db.session.commit()
    flash('Brick deleted successfully!', 'success')
    return redirect(url_for('bricks'))

if __name__ == '__main__':
    app.run(debug=True)
