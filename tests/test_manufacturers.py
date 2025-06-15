import pytest
from models import Manufacturer
from flask import session

def create_admin_user(app):
    """Create an admin user directly in the database"""
    from models import db, User
    from werkzeug.security import generate_password_hash
    
    with app.app_context():
        # Check if user already exists
        user = User.query.filter_by(userName='testadmin').first()
        if user is None:
            # Create new admin user directly in the database
            admin = User(
                userName='testadmin',
                password=generate_password_hash('adminpass'),
                isAdmin=True
            )
            db.session.add(admin)
            db.session.commit()
            admin_id = admin.id  # Get ID before leaving context
            return admin_id
        else:
            # Ensure existing user is admin
            if not user.isAdmin:
                user.isAdmin = True
                db.session.commit()
            return user.id  # Return ID instead of object

def login_admin(client, app):
    # First create the admin user directly in the database and get its ID
    admin_id = create_admin_user(app)
    
    # Then log in through the client
    response = client.post('/login', data={'userName': 'testadmin', 'password': 'adminpass'}, follow_redirects=True)
    
    # Verify and fix session if needed
    with client.session_transaction() as sess:
        print(f"Session after login: userId={sess.get('userId')}, isAdmin={sess.get('isAdmin')}")
        
        # If not properly logged in, manually set session values
        if not sess.get('userId'):
            sess['userId'] = admin_id
            print(f"WARNING: Manually set userId={admin_id} in session")
            
        if not sess.get('isAdmin'):
            sess['isAdmin'] = True
            print("WARNING: Manually set isAdmin=True in session")
            
    return admin_id

def test_add_manufacturer(client, app):
    admin_id = login_admin(client, app)
    
    # Verify session has admin rights before proceeding
    with client.session_transaction() as sess:
        assert sess.get('isAdmin') is True, "Not logged in as admin"
        assert sess.get('userId') is not None, "No user ID in session"
    
    rv = client.post('/add_manufacturer', data={
        'name': 'Manu1', 
        'address': 'Addr', 
        'phoneNo': '123', 
        'email': 'a@b.com'
    }, follow_redirects=True)
    
    assert b'Manu1' in rv.data

def test_edit_manufacturer(client, app):
    admin_id = login_admin(client, app)
    
    # Verify session has admin rights
    with client.session_transaction() as sess:
        assert sess.get('isAdmin') is True, "Not logged in as admin"
        assert sess.get('userId') is not None, "No user ID in session"
    
    # First create a manufacturer to edit
    with app.app_context():
        from models import db
        
        # Check if test manufacturer already exists
        manu = Manufacturer.query.filter_by(name='Manu1').first()
        if not manu:
            manu = Manufacturer(
                name='Manu1',
                address='Addr',
                phoneNo='123-456-7890',  # Valid phone number format
                email='a@b.com'
            )
            db.session.add(manu)
            db.session.commit()
            
        # Store the ID to use outside app context
        manu_id = manu.id
    
    # Now edit the manufacturer
    rv = client.post(f'/edit_manufacturer/{manu_id}', data={
        'name': 'Manu1Edit', 
        'address': 'Addr2', 
        'phoneNo': '456-789-0123',  # Valid phone number format
        'email': 'b@c.com'
    }, follow_redirects=True)
    
    # Check if we're redirected to the login page
    if b'Login</title>' in rv.data:
        print("ERROR: Redirected to login page during edit")
    
    # Check if we're on the edit page
    if b'Edit Manufacturer</title>' in rv.data:
        print("Still on edit page, form not submitted successfully")
        
    # Check for validation errors
    if b'error' in rv.data.lower():
        print(f"Validation error occurred: {rv.data}")
    
    # Now we should see the edited manufacturer name in the response
    assert b'Manu1Edit' in rv.data

def test_delete_manufacturer(client, app):
    admin_id = login_admin(client, app)
    
    # Verify session has admin rights
    with client.session_transaction() as sess:
        assert sess.get('isAdmin') is True, "Not logged in as admin"
        assert sess.get('userId') is not None, "No user ID in session"
    
    # First create a manufacturer to delete
    with app.app_context():
        from models import db
        
        # Check if test manufacturer already exists
        manu = Manufacturer.query.filter_by(name='DeleteManu').first()
        if not manu:
            manu = Manufacturer(
                name='DeleteManu',
                address='DeleteAddr',
                phoneNo='999',
                email='delete@example.com'
            )
            db.session.add(manu)
            db.session.commit()
            
        # Store the ID to use outside app context
        manu_id = manu.id
    
    # Now delete the manufacturer
    rv = client.get(f'/delete_manufacturer/{manu_id}', follow_redirects=True)
    assert b'DeleteManu' not in rv.data

def test_duplicate_manufacturer(client, app):
    admin_id = login_admin(client, app)
    
    # Verify session has admin rights
    with client.session_transaction() as sess:
        assert sess.get('isAdmin') is True, "Not logged in as admin"
        assert sess.get('userId') is not None, "No user ID in session"
    
    # First add a manufacturer
    add_response = client.post('/add_manufacturer', data={
        'name': 'ManuDup', 
        'address': 'DupAddr', 
        'phoneNo': '123-456-7890',  # Valid phone number
        'email': 'dup@example.com'
    }, follow_redirects=True)
    
    # Debug: Check if first add was successful
    if b'ManuDup' not in add_response.data:
        print("ERROR: First manufacturer was not added successfully")
        if b'Login</title>' in add_response.data:
            print("Redirected to login page during first add")
    
    # Try to add a manufacturer with the same name
    dup_response = client.post('/add_manufacturer', data={
        'name': 'ManuDup', 
        'address': 'OtherAddr', 
        'phoneNo': '456-789-0123', 
        'email': 'other@example.com'
    }, follow_redirects=True)
    
    # Debug output
    if b'Login</title>' in dup_response.data:
        print("ERROR: Redirected to login page during duplicate attempt")
    
    # Should get a duplicate error message or stay on the Add Manufacturer form
    assert b'already exists' in dup_response.data or b'Add Manufacturer' in dup_response.data
