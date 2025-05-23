from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
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
