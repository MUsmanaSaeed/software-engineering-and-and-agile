from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Manufacturer
from users import loginRequired
from bricks import delete_bricks_by_manufacturer

manufacturers_bp = Blueprint('manufacturers', __name__)

@manufacturers_bp.route('/manufacturers')
@manufacturers_bp.route('/manufacturers/<int:selected_id>')
def manufacturers(selected_id=None):
    allManufacturers = Manufacturer.query.all()
    # Convert to dicts for JSON serialization in template
    def manufacturer_to_dict(m):
        return {
            'id': m.id,
            'name': m.name,
            'address': m.address,
            'phoneNo': m.phoneNo,
            'email': m.email,
            'bricks': [{'id': b.id, 'name': b.name} for b in m.bricks]
        }
    manufacturer_dicts = [manufacturer_to_dict(m) for m in allManufacturers]
    # Explicitly set selected_manufacturer_id to None if not provided
    if selected_id is None:
        selected_manufacturer_id = None
    else:
        selected_manufacturer_id = selected_id
    return render_template('manufacturers.html', manufacturers=manufacturer_dicts, selected_manufacturer_id=selected_manufacturer_id)

@manufacturers_bp.route('/add_manufacturer', methods=['GET', 'POST'])
@loginRequired
def addManufacturer():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        phoneNo = request.form.get('phoneNo', '')
        email = request.form.get('email', '')
        if not name:
            flash('Name is required.', 'danger')
            return render_template('add_manufacturer.html')
        # Duplicate name check (case-insensitive)
        existing = Manufacturer.query.filter(db.func.lower(Manufacturer.name) == name.lower()).first()
        if existing:
            flash('A manufacturer with this name already exists.', 'danger')
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
        # Redirect to manufacturers page and select the edited manufacturer
        return redirect(url_for('manufacturers.manufacturers', selected_id=manufacturer.id))
    return render_template('edit_manufacturer.html', manufacturer=manufacturer)

@manufacturers_bp.route('/cancel_edit_manufacturer/<int:id>')
@loginRequired
def cancelEditManufacturer(id):
    # Redirect to manufacturers page and select the editing manufacturer
    return redirect(url_for('manufacturers.manufacturers', selected_id=id))

@manufacturers_bp.route('/delete_manufacturer/<int:id>')
@loginRequired
def deleteManufacturer(id):
    manufacturer = Manufacturer.query.get_or_404(id)
    has_bricks = len(manufacturer.bricks) > 0
    if has_bricks and not session.get('isAdmin'):
        flash('Only admins can delete manufacturers with bricks.', 'danger')
        # Stay on the same manufacturer detail after failed delete
        return redirect(url_for('manufacturers.manufacturers', selected_id=id))
    # Call the function from bricks.py to delete all bricks for this manufacturer
    delete_bricks_by_manufacturer(manufacturer.id)
    db.session.delete(manufacturer)
    db.session.commit()
    flash('Manufacturer deleted successfully!', 'success')
    # After delete, select the next manufacturer (by id) if any, else none
    next_manufacturer = Manufacturer.query.order_by(Manufacturer.id).first()
    next_id = next_manufacturer.id if next_manufacturer else None
    if next_id:
        return redirect(url_for('manufacturers.manufacturers', selected_id=next_id))
    else:
        return redirect(url_for('manufacturers.manufacturers'))
