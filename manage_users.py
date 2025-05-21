from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User
from users import loginRequired
from werkzeug.security import generate_password_hash
from functools import wraps

manage_users_bp = Blueprint('manage_users', __name__)

def adminRequired(f):
    @wraps(f)
    def decoratedFunction(*args, **kwargs):
        if not session.get('isAdmin'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decoratedFunction

@manage_users_bp.route('/users/manage')
@loginRequired
@adminRequired
def users():
    all_users = User.query.all()
    return render_template('manage_users.html', users=all_users, current_user_id=session.get('userId'))

@manage_users_bp.route('/users/add', methods=['GET', 'POST'])
@loginRequired
@adminRequired
def add_user():
    if request.method == 'POST':
        userName = request.form['userName']
        password = request.form['password']
        isAdmin = bool(request.form.get('isAdmin'))
        if len(userName) < 5:
            flash('Username must be at least 5 characters long.', 'danger')
            return render_template('manage_user_form.html', user=None)
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('manage_user_form.html', user=None)
        if User.query.filter_by(userName=userName).first():
            flash('Username already exists.', 'danger')
            return render_template('manage_user_form.html', user=None)
        hashedPassword = generate_password_hash(password, method='pbkdf2:sha256')
        newUser = User(userName=userName, password=hashedPassword, isAdmin=isAdmin)
        db.session.add(newUser)
        db.session.commit()
        flash('User added successfully!', 'success')
        return redirect(url_for('manage_users.users'))
    return render_template('manage_user_form.html', user=None)

@manage_users_bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@loginRequired
@adminRequired
def edit_user(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        userName = request.form['userName']
        isAdmin = bool(request.form.get('isAdmin'))
        if len(userName) < 5:
            flash('Username must be at least 5 characters long.', 'danger')
            return render_template('manage_user_form.html', user=user)
        if user.userName != userName and User.query.filter_by(userName=userName).first():
            flash('Username already exists.', 'danger')
            return render_template('manage_user_form.html', user=user)
        user.userName = userName
        user.isAdmin = isAdmin
        password = request.form.get('password')
        if password:
            if len(password) < 8:
                flash('Password must be at least 8 characters long.', 'danger')
                return render_template('manage_user_form.html', user=user)
            user.password = generate_password_hash(password, method='pbkdf2:sha256')
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('manage_users.users'))
    return render_template('manage_user_form.html', user=user)

@manage_users_bp.route('/users/delete/<int:id>', methods=['POST'])
@loginRequired
@adminRequired
def delete_user(id):
    if id == session.get('userId'):
        flash('You cannot delete your own account while logged in.', 'danger')
        return redirect(url_for('manage_users.users'))
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_users.users'))
