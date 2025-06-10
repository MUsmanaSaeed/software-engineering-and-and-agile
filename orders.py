from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from models import db, BrickOrder
from datetime import datetime

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders')
def orders():
    order_nos = db.session.query(BrickOrder.orderNo).distinct().all()
    return render_template('orders.html', order_nos=[o[0] for o in order_nos])

@orders_bp.route('/orders/<order_no>')
def order_detail(order_no):
    orders = BrickOrder.query.filter_by(orderNo=order_no).all()
    return render_template('order_detail.html', order_no=order_no, orders=orders)

@orders_bp.route('/orders/add', methods=['POST'])
def add_order():
    data = request.form
    new_order = BrickOrder(
        orderNo=data['orderNo'],
        brick=data['brick'],
        bricks_ordered=int(data['bricks_ordered']),
        bricks_received=int(data.get('bricks_received', 0)),
        ordered_date=datetime.strptime(data['ordered_date'], '%Y-%m-%d'),
        expected_date=datetime.strptime(data['expected_date'], '%Y-%m-%d')
    )
    db.session.add(new_order)
    db.session.commit()
    return redirect(url_for('orders.orders'))

@orders_bp.route('/orders/received/<int:order_id>', methods=['POST'])
def mark_received(order_id):
    order = BrickOrder.query.get(order_id)
    if order:
        order.bricks_received = order.bricks_ordered
        db.session.commit()
    return redirect(url_for('orders.order_detail', order_no=order.orderNo))
