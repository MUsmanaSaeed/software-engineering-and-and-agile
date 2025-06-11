from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User
from users import loginRequired
from werkzeug.security import generate_password_hash
from functools import wraps
from mediators.user_mediator import UserMediator

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
    all_users = UserMediator.get_all_users()
    return render_template('manage_users.html', users=all_users, current_user_id=session.get('userId'))

def render_manage_user_form(user, error_fields=None, error_messages=None):
    return render_template('manage_user_form.html', user=user, error_fields=error_fields, error_messages=error_messages)

@manage_users_bp.route('/users/add', methods=['GET', 'POST'])
@loginRequired
@adminRequired
def add_user():
    if request.method == 'POST':
        user_data = {
            'userName': request.form['userName'],
            'password': request.form['password'],
            'isAdmin': bool(request.form.get('isAdmin'))
        }
        success, newUser, error_messages, error_fields = UserMediator.add_user(user_data)
        if not success:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {"success": False, "message": error_messages[0] if error_messages else '', "error_fields": error_fields}, 400
            return render_manage_user_form(None, error_fields=error_fields, error_messages=error_messages)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            flash('User added successfully!', 'success')
            return {
                "success": True,
                "user": {
                    "id": newUser.id,
                    "userName": newUser.userName,
                    "isAdmin": newUser.isAdmin
                },
                "message": "User added successfully!",
                "redirect": url_for('manage_users.users')
            }
        flash('User added successfully!', 'success')
        return redirect(url_for('manage_users.users'))
    return render_manage_user_form(None, error_fields=None, error_messages=None)

@manage_users_bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@loginRequired
@adminRequired
def edit_user(id):
    user = UserMediator.get_user_by_id(id)
    if request.method == 'POST':
        user_data = {
            'userName': request.form['userName'],
            'isAdmin': True if user.id == session.get('userId') else bool(request.form.get('isAdmin')),
            'password': request.form.get('password') if request.form.get('password') else None
        }
        success, updated_user, error_messages, error_fields = UserMediator.update_user(user, user_data, session_user_id=session.get('userId'))
        attempted_user = User(id=user.id, userName=user_data['userName'], isAdmin=user_data['isAdmin'], password=user.password)
        if not success:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {"success": False, "message": error_messages[0] if error_messages else '', "error_fields": error_fields}, 400
            flash(error_messages, 'danger' if 'password' in error_fields or 'userName' in error_fields else 'warning')
            return render_manage_user_form(attempted_user, error_fields=error_fields, error_messages=error_messages)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            flash('User updated successfully!', 'success')
            return {
                "success": True,
                "user": {
                    "id": updated_user.id,
                    "userName": updated_user.userName,
                    "isAdmin": updated_user.isAdmin
                },
                "message": "User updated successfully!",
                "redirect": url_for('manage_users.users')
            }
        flash('User updated successfully!', 'success')
        return redirect(url_for('manage_users.users'))
    return render_manage_user_form(user)

@manage_users_bp.route('/users/delete/<int:id>', methods=['POST'])
@loginRequired
@adminRequired
def delete_user(id):
    if id == session.get('userId'):
        flash('You cannot delete your own account while logged in.', 'danger')
        return redirect(url_for('manage_users.users'))
    UserMediator.delete_user(id)
    flash('User deleted successfully!', 'success')
    return redirect(url_for('manage_users.users'))
