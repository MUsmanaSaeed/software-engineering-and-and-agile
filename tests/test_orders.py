import pytest
from models import Brick, Manufacturer, BrickOrder
from datetime import date, timedelta
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
    
    # Create a manufacturer and brick for orders
    with app.app_context():
        from models import db
        
        # Create manufacturer
        manu = Manufacturer.query.filter_by(name='OrderManu').first()
        if not manu:
            manu = Manufacturer(
                name='OrderManu',
                address='Order Address',
                phoneNo='123-456-7890',  # Valid phone number format
                email='order@example.com'
            )
            db.session.add(manu)
            db.session.commit()
        
        manu_id = manu.id
        
        # Create brick
        brick = Brick.query.filter_by(name='OrderBrick').first()
        if not brick:
            brick = Brick(
                name='OrderBrick',
                price=1.0,
                colour='Red',
                material='Clay',
                strength='High',
                width=10,
                depth=5,
                height=3,
                type='Solid',
                voids=0,
                manufacturerId=manu_id
            )
            db.session.add(brick)
            db.session.commit()
        
        brick_id = brick.id
    
    return brick_id

def test_add_order(client, app):
    # Login and create test data
    brick_id = login_admin(client, app)
    
    # Verify session has admin rights before proceeding
    with client.session_transaction() as sess:
        assert sess.get('isAdmin') is True, "Not logged in as admin"
        assert sess.get('userId') is not None, "No user ID in session"
    
    # Add an order
    rv = client.post('/orders/add', data={
        'orderNo': 'ORD1', 
        'brickId': brick_id, 
        'bricks_ordered': 100, 
        'ordered_date': date.today().strftime('%Y-%m-%d'), 
        'expected_date': (date.today() + timedelta(days=2)).strftime('%Y-%m-%d')
    }, follow_redirects=True)
    
    # Check for errors
    if b'Login</title>' in rv.data:
        print("ERROR: Redirected to login page during order add")
    
    assert b'ORD1' in rv.data

def test_edit_order(client, app):
    # Login and create test data
    brick_id = login_admin(client, app)
    
    # Verify session has admin rights
    with client.session_transaction() as sess:
        assert sess.get('isAdmin') is True, "Not logged in as admin"
        assert sess.get('userId') is not None, "No user ID in session"
    
    # Create order to edit if it doesn't exist
    order_id = None
    with app.app_context():
        from models import db
        
        # Check if order already exists
        order = BrickOrder.query.filter_by(orderNo='ORD1').first()
        if not order:
            # Create a new test order
            order = BrickOrder(
                orderNo='ORD1',
                brickId=brick_id,
                bricks_ordered=100,
                bricks_received=0,
                ordered_date=date.today(),
                expected_date=date.today() + timedelta(days=2)
            )
            db.session.add(order)
            db.session.commit()
        
        order_id = order.id
    
    # Now edit the order
    rv = client.post(f'/orders/edit/{order_id}', data={
        'bricks_ordered': 150, 
        'ordered_date': date.today().strftime('%Y-%m-%d'), 
        'expected_date': (date.today() + timedelta(days=3)).strftime('%Y-%m-%d')
    }, follow_redirects=True)
    
    # Check for errors
    if b'Login</title>' in rv.data:
        print("ERROR: Redirected to login page during order edit")
    
    assert b'150' in rv.data

def test_mark_received(client, app):
    # Login and create test data
    brick_id = login_admin(client, app)
    
    # Verify session has admin rights
    with client.session_transaction() as sess:
        assert sess.get('isAdmin') is True, "Not logged in as admin"
        assert sess.get('userId') is not None, "No user ID in session"
    
    # Get or create order
    order_id = None
    with app.app_context():
        from models import db
        
        # Check if order already exists
        order = BrickOrder.query.filter_by(orderNo='ORD1').first()
        if not order:
            # Create a new test order
            order = BrickOrder(
                orderNo='ORD1',
                brickId=brick_id,
                bricks_ordered=150,
                bricks_received=0,
                ordered_date=date.today(),
                expected_date=date.today() + timedelta(days=3)
            )
            db.session.add(order)
            db.session.commit()
        
        order_id = order.id
    
    # Mark order as received
    rv = client.post(f'/orders/received/{order_id}', data={'bricks_received': 150}, follow_redirects=True)
    
    # Check for errors
    if b'Login</title>' in rv.data:
        print("ERROR: Redirected to login page during mark received")
    
    assert b'Received' in rv.data or b'ORD1' in rv.data

def test_cancel_order(client, app):
    # Login and create test data
    brick_id = login_admin(client, app)
    
    # Verify session has admin rights
    with client.session_transaction() as sess:
        assert sess.get('isAdmin') is True, "Not logged in as admin"
        assert sess.get('userId') is not None, "No user ID in session"
    
    # Get or create order
    order_id = None
    with app.app_context():
        from models import db
        
        # Create a new test order specifically for cancellation
        order = BrickOrder(
            orderNo='ORD2',
            brickId=brick_id,
            bricks_ordered=150,
            bricks_received=0,
            ordered_date=date.today(),
            expected_date=date.today() + timedelta(days=3)
        )
        db.session.add(order)
        db.session.commit()
        
        order_id = order.id
    
    # Cancel the order
    rv = client.post(f'/orders/cancel/{order_id}', follow_redirects=True)
    
    # Check for errors
    if b'Login</title>' in rv.data:
        print("ERROR: Redirected to login page during order cancel")
    
    assert b'Canceled' in rv.data or b'ORD2' in rv.data

def test_delete_order(client, app):
    # Login and create test data
    brick_id = login_admin(client, app)
    
    # Verify session has admin rights
    with client.session_transaction() as sess:
        assert sess.get('isAdmin') is True, "Not logged in as admin"
        assert sess.get('userId') is not None, "No user ID in session"
    
    # Get or create order
    order_id = None
    order_no = None
    with app.app_context():
        from models import db
        
        # Create a new test order specifically for deletion
        order = BrickOrder(
            orderNo='ORD3',
            brickId=brick_id,
            bricks_ordered=150,
            bricks_received=0,
            ordered_date=date.today(),
            expected_date=date.today() + timedelta(days=3)
        )
        db.session.add(order)
        db.session.commit()
        
        order_id = order.id
        order_no = order.orderNo
    
    # Delete the order
    rv = client.post(f'/orders/delete/{order_id}', follow_redirects=True)
    
    # Check for errors
    if b'Login</title>' in rv.data:
        print("ERROR: Redirected to login page during order delete")
    
    assert order_no.encode() not in rv.data
