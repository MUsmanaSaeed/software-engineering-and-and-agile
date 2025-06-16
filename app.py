from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db
from users import users_bp
from manufacturers import manufacturers_bp
from bricks import bricks_bp
from manage_users import manage_users_bp
from orders import orders_bp
from mediators.user_mediator import UserMediator

app = Flask(__name__)
app.config['SECRET_KEY'] = 'brickManagementSystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bricks.db'
db.init_app(app)

@app.before_request
def require_login():
    # Require login for all routes except login, register, and static files
    allowedRoutes = ['users.login', 'users.register']
    endpoint = request.endpoint
    if endpoint is None:
        return  # Let Flask handle it
    if endpoint in allowedRoutes or endpoint.startswith('static'):
        return  # Allow access
    if not session.get('userId'):
        return redirect(url_for('users.login', next=request.url))

@app.route('/')
def index():
    return render_template('index.html')

app.register_blueprint(users_bp)
app.register_blueprint(manufacturers_bp)
app.register_blueprint(bricks_bp)
app.register_blueprint(manage_users_bp)
app.register_blueprint(orders_bp)

if __name__ == 'app':
    with app.app_context():
        db.create_all()
        if not UserMediator.duplicate_username_exists('admin'):
            admin_user_data = {
                'userName': 'admin',
                'password': 'p4$$w0rd',
                'isAdmin': True
            }
            UserMediator.add_admin_user(admin_user_data)
    app.run(debug=True)