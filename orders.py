from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from models import db, BrickOrder, Brick
from datetime import datetime
from mediators.brick_order_mediator import BrickOrderMediator
from mediators.brick_mediator import BrickMediator

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders')
def orders():
    order_nos = BrickOrderMediator.get_all_order_nos()
    bricks = BrickMediator.get_all_bricks()
    return render_template('orders.html', order_nos=order_nos, bricks=bricks)

@orders_bp.route('/orders/<order_no>')
def order_detail(order_no):
    orders = BrickOrderMediator.get_orders_by_order_no(order_no)
    order_nos = BrickOrderMediator.get_all_order_nos()
    bricks = BrickMediator.get_all_bricks()
    current_date = datetime.today().date()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not orders:
            return render_template('order_detail_panel.html', selected_order_no=None, order_details=None)
        return render_template('order_detail_panel.html', selected_order_no=order_no, order_details=orders, current_date=current_date, bricks=bricks)
    if not orders:
        return render_template('orders.html', order_nos=order_nos, selected_order_no=None, order_details=None, bricks=bricks)
    return render_template('orders.html', order_nos=order_nos, selected_order_no=order_no, order_details=orders, current_date=current_date, bricks=bricks)

@orders_bp.route('/orders/add', methods=['POST'])
def add_order():
    data = request.form
    order_data = {
        'orderNo': data['orderNo'],
        'brickId': int(data['brickId']),
        'bricks_ordered': int(data['bricks_ordered']),
        'bricks_received': int(data.get('bricks_received', 0)),
        'ordered_date': datetime.strptime(data['ordered_date'], '%Y-%m-%d'),
        'expected_date': datetime.strptime(data['expected_date'], '%Y-%m-%d')
    }
    new_order = BrickOrderMediator.add_order(order_data)
    return redirect(url_for('orders.order_detail', order_no=new_order.orderNo))

@orders_bp.route('/orders/received/<int:order_id>', methods=['POST'])
def mark_received(order_id):
    BrickOrderMediator.mark_received(order_id)
    order = BrickOrderMediator.get_order_by_id(order_id)
    return redirect(url_for('orders.order_detail', order_no=order.orderNo))

@orders_bp.route('/orders/cancel/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    BrickOrderMediator.cancel_order(order_id)
    order = BrickOrderMediator.get_order_by_id(order_id)
    return redirect(url_for('orders.order_detail', order_no=order.orderNo))
