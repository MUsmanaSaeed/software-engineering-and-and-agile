from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from functools import wraps

users_bp = Blueprint('users', __name__)

def loginRequired(f):
    @wraps(f)
    def decoratedFunction(*args, **kwargs):
        if not session.get('userId'):
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('users.login', next=request.url))
        return f(*args, **kwargs)
    return decoratedFunction

@users_bp.route('/register', methods=['GET', 'POST'])
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
        return redirect(url_for('users.login'))
    return render_template('register.html', userName=userName, isAdmin=isAdmin)

@users_bp.route('/login', methods=['GET', 'POST'])
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

@users_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('users.login'))
