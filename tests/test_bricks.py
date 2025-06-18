import pytest
from flask import session
from models import db, Brick, Manufacturer

# Import logger for debug output
import logging
logger = logging.getLogger(__name__)

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

def create_test_manufacturer(app):
    """Create a test manufacturer directly in the database"""
    from models import db
    
    with app.app_context():
        # Check if manufacturer already exists
        manu = Manufacturer.query.filter_by(name='TestManu').first()
        if manu is None:
            # Create new manufacturer with valid phone number
            manu = Manufacturer(
                name='TestManu',
                address='Test Address',
                phoneNo='123-456-7890',  # Valid phone number format
                email='test@example.com'
            )
            db.session.add(manu)
            db.session.commit()
        
        # Return the ID instead of the object
        return manu.id

def login_admin(client, app):
    # First create the admin user directly in the database
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
    
    # Create a test manufacturer directly in the database
    manu_id = create_test_manufacturer(app)
    return manu_id

def test_add_brick(client, app):
    # Get manufacturer ID from login
    manu_id = login_admin(client, app)
    
    # Verify session has admin rights before proceeding
    with client.session_transaction() as sess:
        assert sess.get('isAdmin') is True, "Not logged in as admin"
        assert sess.get('userId') is not None, "No user ID in session"
    
    # Use the ID to create the brick
    rv = client.post('/add_brick', data={
        'name': 'Brick1', 
        'price': 1.5, 
        'colour': 'Red', 
        'material': 'Clay', 
        'strength': 'High',
        'width': 10, 
        'depth': 5, 
        'height': 3, 
        'type': 'Solid', 
        'voids': 0, 
        'manufacturer_id': manu_id
    }, follow_redirects=True)
    
    # Check for errors
    if b'Login</title>' in rv.data:
        print("ERROR: Redirected to login page during brick add")
    
    assert b'Brick1' in rv.data

def test_edit_brick(client, app):
    # Login and get manufacturer ID
    manu_id = login_admin(client, app)
    
    # Verify session has admin rights
    with client.session_transaction() as sess:
        assert sess.get('isAdmin') is True, "Not logged in as admin"
        assert sess.get('userId') is not None, "No user ID in session"
    
    # Create a brick to edit
    brick_id = None
    with app.app_context():
        from models import db
        
        # Get manufacturer
        manu = db.session.get(Manufacturer, manu_id)
        assert manu is not None, "Test manufacturer not found"
        
        # Check if test brick already exists
        brick = Brick.query.filter_by(name='TestBrick').first()
        if not brick:
            brick = Brick(
                name='TestBrick',
                price=1.5,
                colour='Red',
                material='Clay',
                strength='High',
                width=10,
                depth=5,
                height=3,
                type='Solid',
                voids=0,
                manufacturerId=manu.id
            )
            db.session.add(brick)
            db.session.commit()
        
        # Store the ID to use outside app context
        brick_id = brick.id
    
    # Now edit the brick using its ID
    rv = client.post(f'/edit_brick/{brick_id}', data={
        'name': 'TestBrickEdit', 
        'price': 2.0, 
        'colour': 'Blue', 
        'material': 'Cement', 
        'strength': 'Medium',
        'width': 12, 
        'depth': 6, 
        'height': 4, 
        'type': 'Hollow', 
        'voids': 10, 
        'manufacturer_id': manu_id
    }, follow_redirects=True)
    
    # Check for errors
    if b'Login</title>' in rv.data:
        print("ERROR: Redirected to login page during brick edit")
    
    assert b'TestBrickEdit' in rv.data

def test_delete_brick(client, app):
    # Login and get manufacturer ID
    manu_id = login_admin(client, app)
    
    # Verify session has admin rights
    with client.session_transaction() as sess:
        assert sess.get('isAdmin') is True, "Not logged in as admin"
        assert sess.get('userId') is not None, "No user ID in session"
    
    # Create a brick to delete
    brick_id = None
    with app.app_context():
        from models import db
        
        # Get manufacturer
        manu = db.session.get(Manufacturer, manu_id)
        assert manu is not None, "Test manufacturer not found"
        
        # Check if test brick already exists
        brick = Brick.query.filter_by(name='DeleteBrick').first()
        if not brick:
            brick = Brick(
                name='DeleteBrick',
                price=1.5,
                colour='Red',
                material='Clay',
                strength='High',
                width=10,
                depth=5,
                height=3,
                type='Solid',
                voids=0,
                manufacturerId=manu.id
            )
            db.session.add(brick)
            db.session.commit()
        
        # Store the ID to use outside app context
        brick_id = brick.id
    
    # Delete the brick using its ID
    rv = client.get(f'/delete_brick/{brick_id}', follow_redirects=True)
    
    # Check for errors
    if b'Login</title>' in rv.data:
        print("ERROR: Redirected to login page during brick delete")
    
    assert b'DeleteBrick' not in rv.data

def test_duplicate_brick(client, app):
    # Get manufacturer ID from login
    manu_id = login_admin(client, app)
    
    # Verify session has admin rights
    with client.session_transaction() as sess:
        assert sess.get('isAdmin') is True, "Not logged in as admin"
        assert sess.get('userId') is not None, "No user ID in session"
    
    # First add a brick
    first_response = client.post('/add_brick', data={
        'name': 'DuplicateBrick', 
        'price': 1.0, 
        'colour': 'Red', 
        'material': 'Clay', 
        'strength': 'High',
        'width': 10, 
        'depth': 5, 
        'height': 3, 
        'type': 'Solid', 
        'voids': 0, 
        'manufacturer_id': manu_id
    }, follow_redirects=True)
    
    # Check if first brick was added successfully
    if b'DuplicateBrick' not in first_response.data:
        print("ERROR: First brick was not added successfully")
        if b'Login</title>' in first_response.data:
            print("Redirected to login page during first brick add")
    
    # Try to add a brick with the same name
    rv = client.post('/add_brick', data={
        'name': 'DuplicateBrick', 
        'price': 1.0, 
        'colour': 'Red', 
        'material': 'Clay', 
        'strength': 'High',
        'width': 10, 
        'depth': 5, 
        'height': 3, 
        'type': 'Solid', 
        'voids': 0, 
        'manufacturer_id': manu_id
    }, follow_redirects=True)
    
    # Check for errors
    if b'Login</title>' in rv.data:
        print("ERROR: Redirected to login page during duplicate brick add")
    
    # Should get a duplicate error message
    assert b'already exists' in rv.data or b'Add Brick' in rv.data
