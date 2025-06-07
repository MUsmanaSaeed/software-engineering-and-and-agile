from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Manufacturer
from users import loginRequired
from bricks import delete_bricks_by_manufacturer

manufacturers_bp = Blueprint('manufacturers', __name__)

@manufacturers_bp.route('/manufacturers')
def manufacturers():
    allManufacturers = Manufacturer.query.all()
    return render_template('manufacturers.html', manufacturers=allManufacturers)

@manufacturers_bp.route('/add_manufacturer', methods=['GET', 'POST'])
@loginRequired
def addManufacturer():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phoneNo = request.form.get('phoneNo', '')
        email = request.form.get('email', '')
        if not name or not address:
            flash('All fields are required.', 'danger')
            return render_template('add_manufacturer.html')
        newManufacturer = Manufacturer(name=name, address=address, phoneNo=phoneNo, email=email)
        db.session.add(newManufacturer)
        db.session.commit()
        flash('Manufacturer added successfully!', 'success')
        return redirect(url_for('manufacturers.manufacturers'))
    return render_template('add_manufacturer.html')

@manufacturers_bp.route('/edit_manufacturer/<int:id>', methods=['GET', 'POST'])
@loginRequired
def editManufacturer(id):
    manufacturer = Manufacturer.query.get_or_404(id)
    if request.method == 'POST':
        manufacturer.name = request.form['name']
        manufacturer.address = request.form['address']
        manufacturer.phoneNo = request.form.get('phoneNo', '')
        manufacturer.email = request.form.get('email', '')
        db.session.commit()
        flash('Manufacturer updated successfully!', 'success')
        return redirect(url_for('manufacturers.manufacturers'))
    return render_template('edit_manufacturer.html', manufacturer=manufacturer)

@manufacturers_bp.route('/delete_manufacturer/<int:id>')
@loginRequired
def deleteManufacturer(id):
    if not session.get('isAdmin'):
        flash('Only admins can delete manufacturers.', 'danger')
        return redirect(url_for('manufacturers.manufacturers'))
    manufacturer = Manufacturer.query.get_or_404(id)
    # Call the function from bricks.py to delete all bricks for this manufacturer
    delete_bricks_by_manufacturer(manufacturer.id)
    db.session.delete(manufacturer)
    db.session.commit()
    flash('Manufacturer deleted successfully!', 'success')
    return redirect(url_for('manufacturers.manufacturers'))
