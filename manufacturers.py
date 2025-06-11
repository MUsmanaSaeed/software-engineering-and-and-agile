from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Manufacturer
from users import loginRequired
from bricks import delete_bricks_by_manufacturer
from mediators.manufacturer_mediator import ManufacturerMediator

manufacturers_bp = Blueprint('manufacturers', __name__)

@manufacturers_bp.route('/manufacturers')
@manufacturers_bp.route('/manufacturers/<int:selected_id>')
def manufacturers(selected_id=None):
    allManufacturers = ManufacturerMediator.get_all_manufacturers()
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
        result = ManufacturerMediator.add_manufacturer_with_checks(request.form)
        if 'error' in result:
            flash(result['error'], 'danger')
            return render_template('add_manufacturer.html')
        flash('Manufacturer added successfully!', 'success')
        return redirect(url_for('manufacturers.manufacturers'))
    return render_template('add_manufacturer.html')

@manufacturers_bp.route('/edit_manufacturer/<int:id>', methods=['GET', 'POST'])
@loginRequired
def editManufacturer(id):
    manufacturer = ManufacturerMediator.get_manufacturer_by_id(id)
    if request.method == 'POST':
        result = ManufacturerMediator.update_manufacturer_with_checks(manufacturer, request.form)
        if 'error' in result:
            flash(result['error'], 'danger')
            return render_template('edit_manufacturer.html', manufacturer=manufacturer)
        flash('Manufacturer updated successfully!', 'success')
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
    result = ManufacturerMediator.delete_manufacturer_with_checks(id, session.get('isAdmin'))
    if 'error' in result:
        flash(result['error'], 'danger')
        return redirect(url_for('manufacturers.manufacturers', selected_id=id))
    flash('Manufacturer deleted successfully!', 'success')
    next_id = ManufacturerMediator.get_next_manufacturer_id()
    if next_id:
        return redirect(url_for('manufacturers.manufacturers', selected_id=next_id))
    return redirect(url_for('manufacturers.manufacturers'))
