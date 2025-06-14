from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash, session
from models import db, BrickOrder, Brick
from datetime import datetime, timedelta
from mediators.brick_order_mediator import BrickOrderMediator
from mediators.brick_mediator import BrickMediator

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders')
def orders():
    order_nos = BrickOrderMediator.get_all_order_nos()
    bricks = BrickMediator.get_all_bricks()
    def brick_to_dict(brick):
        return {
            'id': brick.id,
            'name': brick.name,
            'manufacturer': {
                'id': brick.manufacturer.id if brick.manufacturer else None,
                'name': brick.manufacturer.name if brick.manufacturer else ''
            }
        }
    brick_dicts = [brick_to_dict(b) for b in bricks]
    current_date = datetime.today().date()
    return render_template('orders.html', order_nos=order_nos, bricks=brick_dicts, current_date=current_date, timedelta=timedelta)

@orders_bp.route('/orders/<order_no>')
def order_detail(order_no):
    orders = BrickOrderMediator.get_orders_by_order_no(order_no)
    order_nos = BrickOrderMediator.get_all_order_nos()
    bricks = BrickMediator.get_all_bricks()
    current_date = datetime.today().date()
    def brick_to_dict(brick):
        return {
            'id': brick.id,
            'name': brick.name,
            'manufacturer': {
                'id': brick.manufacturer.id if brick.manufacturer else None,
                'name': brick.manufacturer.name if brick.manufacturer else ''
            }
        }
    brick_dicts = [brick_to_dict(b) for b in bricks]
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not orders:
            return render_template('order_detail_panel.html', selected_order_no=None, order_details=None)
        return render_template('order_detail_panel.html', selected_order_no=order_no, order_details=orders, current_date=current_date, bricks=brick_dicts)
    if not orders:
        return render_template('orders.html', order_nos=order_nos, selected_order_no=None, order_details=None, bricks=brick_dicts)
    return render_template('orders.html', order_nos=order_nos, selected_order_no=order_no, order_details=orders, current_date=current_date, bricks=brick_dicts, timedelta=timedelta)

@orders_bp.route('/orders/add', methods=['POST'])
def add_order():
    data = request.form
    try:
        order_data = {
            'orderNo': data['orderNo'],
            'brickId': int(data['brickId']) if data.get('brickId') else None,
            'bricks_ordered': int(data['bricks_ordered']),
            'bricks_received': int(data.get('bricks_received', 0)),
            'ordered_date': datetime.strptime(data['ordered_date'], '%Y-%m-%d'),
            'expected_date': datetime.strptime(data['expected_date'], '%Y-%m-%d')
        }
        new_order = BrickOrderMediator.add_order(order_data)
    except ValueError as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)})
        flash(str(e), 'danger')
        return redirect(url_for('orders.orders'))
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'orderNo': new_order.orderNo})
    return redirect(url_for('orders.order_detail', order_no=new_order.orderNo))

@orders_bp.route('/orders/received/<int:order_id>', methods=['POST'])
def mark_received(order_id):
    bricks_received = request.form.get('bricks_received', type=int)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    try:
        BrickOrderMediator.mark_received(order_id, bricks_received)
    except ValueError as e:
        if is_ajax:
            return jsonify({'success': False, 'error': str(e)})
        flash(str(e), 'danger')
        order = BrickOrderMediator.get_order_by_id(order_id)
        return redirect(url_for('orders.order_detail', order_no=order.orderNo))
    if is_ajax:
        return jsonify({'success': True})
    order = BrickOrderMediator.get_order_by_id(order_id)
    return redirect(url_for('orders.order_detail', order_no=order.orderNo))

@orders_bp.route('/orders/cancel/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    BrickOrderMediator.cancel_order(order_id)
    order = BrickOrderMediator.get_order_by_id(order_id)
    return redirect(url_for('orders.order_detail', order_no=order.orderNo))

@orders_bp.route('/orders/edit/<int:order_id>', methods=['POST'])
def edit_order(order_id):
    order = BrickOrderMediator.get_order_by_id(order_id)
    from flask import session
    is_admin = session.get('isAdmin', False)
    if not order:
        return jsonify({'success': False, 'error': 'Order not found.'}), 404 if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else (flash('Order not found.', 'danger'), redirect(url_for('orders.orders')))
    if order.canceled_date:
        return jsonify({'success': False, 'error': 'Cannot edit an order that has been canceled.'}), 400 if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else (flash('Cannot edit an order that has been canceled.', 'warning'), redirect(url_for('orders.order_detail', order_no=order.orderNo)))
    try:
        order.bricks_ordered = int(request.form['bricks_ordered'])
        order.expected_date = datetime.strptime(request.form['expected_date'], '%Y-%m-%d')
        # Admins can edit received status
        if is_admin:
            if 'set_unreceived' in request.form and request.form['set_unreceived'] == '1':
                order.received_date = None
                order.bricks_received = 0
            elif 'received_date' in request.form and request.form['received_date']:
                order.received_date = datetime.strptime(request.form['received_date'], '%Y-%m-%d')
                order.bricks_received = int(request.form.get('bricks_received', order.bricks_received or 0))
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True})
        flash('Order updated successfully!', 'success')
        return redirect(url_for('orders.order_detail', order_no=order.orderNo))
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': str(e)}), 400
        flash(f'Error updating order: {e}', 'danger')
        return redirect(url_for('orders.order_detail', order_no=order.orderNo))

@orders_bp.route('/orders/delete/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    success = BrickOrderMediator.delete_order(order_id)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': success})
    if success:
        flash('Order deleted!', 'success')
    else:
        flash('Order not found or could not be deleted.', 'danger')
    return redirect(url_for('orders.orders'))
