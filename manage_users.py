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

def render_manage_user_form(user, error_fields=None):
    return render_template('manage_user_form.html', user=user, error_fields=error_fields)

@manage_users_bp.route('/users/add', methods=['GET', 'POST'])
@loginRequired
@adminRequired
def add_user():
    if request.method == 'POST':
        userName = request.form['userName']
        password = request.form['password']
        isAdmin = bool(request.form.get('isAdmin'))
        error_fields = []
        # Validation checks
        if len(userName) < 3:
            error_fields.append('userName')
            message = 'Username must be at least 3 characters long.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {"success": False, "message": message, "error_fields": error_fields}, 400
            flash(message, 'danger')
            return render_manage_user_form(None, error_fields=error_fields)
        if len(password) < 8:
            error_fields.append('password')
            message = 'Password must be at least 8 characters long.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {"success": False, "message": message, "error_fields": error_fields}, 400
            flash(message, 'danger')
            return render_manage_user_form(None, error_fields=error_fields)
        if UserMediator.duplicate_username_exists(userName):
            error_fields.append('userName')
            message = 'Username already exists.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {"success": False, "message": message, "error_fields": error_fields}, 400
            flash(message, 'danger')
            return render_manage_user_form(None, error_fields=error_fields)
        user_data = {
            'userName': userName,
            'password': password,
            'isAdmin': isAdmin
        }
        newUser = UserMediator.add_user(user_data)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from flask import url_for, flash
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
    return render_manage_user_form(None)

@manage_users_bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@loginRequired
@adminRequired
def edit_user(id):
    user = UserMediator.get_user_by_id(id)
    if request.method == 'POST':
        userName = request.form['userName']
        is_self = user.id == session.get('userId')
        isAdmin = True if is_self else bool(request.form.get('isAdmin'))
        attempted_user = User(id=user.id, userName=userName, isAdmin=isAdmin, password=user.password)
        error_fields = []
        # Validation checks
        if is_self and not request.form.get('isAdmin'):
            message = 'Admins cannot remove their own admin rights.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {"success": False, "message": message, "error_fields": ["isAdmin"]}, 400
            flash(message, 'warning')
            return render_manage_user_form(attempted_user, error_fields=["isAdmin"])
        if len(userName) < 3:
            error_fields.append('userName')
            message = 'Username must be at least 3 characters long.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {"success": False, "message": message, "error_fields": error_fields}, 400
            flash(message, 'danger')
            return render_manage_user_form(attempted_user, error_fields=error_fields)
        if user.userName != userName and UserMediator.duplicate_username_exists(userName):
            error_fields.append('userName')
            message = 'Username already exists.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {"success": False, "message": message, "error_fields": error_fields}, 400
            flash(message, 'danger')
            return render_manage_user_form(attempted_user, error_fields=error_fields)
        password = request.form.get('password')
        if password and len(password) < 8:
            error_fields.append('password')
            message = 'Password must be at least 8 characters long.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return {"success": False, "message": message, "error_fields": error_fields}, 400
            flash(message, 'danger')
            return render_manage_user_form(attempted_user, error_fields=error_fields)
        user_data = {
            'userName': userName,
            'isAdmin': isAdmin,
            'password': password if password else None
        }
        UserMediator.update_user(user, user_data)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from flask import url_for, flash
            flash('User updated successfully!', 'success')
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "userName": user.userName,
                    "isAdmin": user.isAdmin
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
