import pytest
from flask import session
from models import User
from werkzeug.security import generate_password_hash

def register(client, username, password):
    return client.post('/register', data={
        'userName': username,
        'password': password
    }, follow_redirects=True)

def login(client, username, password):
    return client.post('/login', data={
        'userName': username,
        'password': password
    }, follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_register_login_logout(client, app):
    # Register
    rv = register(client, 'testuser', 'testpassword')
    assert b'Register' in rv.data or b'Login' in rv.data
    # Login
    rv = login(client, 'testuser', 'testpassword')
    assert b'Welcome' in rv.data or b'Bricks' in rv.data
    # Logout
    rv = logout(client)
    assert b'Login' in rv.data

def test_login_invalid(client, app):
    rv = login(client, 'nouser', 'badpass')
    assert b'Invalid' in rv.data or b'Login' in rv.data

def test_register_duplicate(client, app):
    register(client, 'dupuser', 'password123')
    rv = register(client, 'dupuser', 'password123')
    assert b'already exists' in rv.data or b'Register' in rv.data
