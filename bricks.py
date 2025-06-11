from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Brick, Manufacturer
from users import loginRequired
from mediators.brick_mediator import BrickMediator
from mediators.manufacturer_mediator import ManufacturerMediator

bricks_bp = Blueprint('bricks', __name__)

@bricks_bp.route('/bricks')
@bricks_bp.route('/bricks/<int:brick_id>')
def bricks(brick_id=None):
    allBricks = BrickMediator.get_all_bricks()
    # Convert to list of dicts for JSON serialization in template
    def brick_to_dict(brick):
        return {
            'id': brick.id,
            'name': brick.name,
            'colour': brick.colour,
            'material': brick.material,
            'strength': brick.strength,
            'width': brick.width,
            'depth': brick.depth,
            'height': brick.height,
            'type': brick.type,
            'voids': brick.voids,
            'manufacturer': {
                'id': brick.manufacturer.id if brick.manufacturer else None,
                'name': brick.manufacturer.name if brick.manufacturer else ''
            }
        }
    brick_dicts = [brick_to_dict(b) for b in allBricks]
    selected_brick_id = None
    if brick_id is not None and any(b['id'] == brick_id for b in brick_dicts):
        selected_brick_id = brick_id
    return render_template('bricks.html', bricks=brick_dicts, selected_brick_id=selected_brick_id)

@bricks_bp.route('/add_brick', methods=['GET', 'POST'])
@loginRequired
def addBrick():
    manufacturers = ManufacturerMediator.get_all_manufacturers()
    selected_brick_id = request.args.get('selected_brick_id', type=int)
    if request.method == 'POST':
        name = request.form['name']
        colour = request.form['colour']
        material = request.form['material']
        strength = request.form['strength']
        width = float(request.form['width'])
        depth = float(request.form['depth'])
        height = float(request.form['height'])
        type_ = request.form['type']
        voids = int(request.form['voids'])
        manufacturerId = int(request.form['manufacturer_id'])
        # Use mediator for business logic and creation
        brick_data = {
            'name': name,
            'colour': colour,
            'material': material,
            'strength': strength,
            'width': width,
            'depth': depth,
            'height': height,
            'type': type_,
            'voids': voids,
            'manufacturerId': manufacturerId
        }
        # Duplicate name check via mediator
        if BrickMediator.duplicate_name_exists(name):
            flash('A brick with this name already exists.', 'danger')
            form_data = dict(request.form)
            form_data['manufacturerId'] = manufacturerId
            return render_template('add_brick.html', manufacturers=manufacturers, selected_brick_id=selected_brick_id, brick=form_data)
        newBrick = BrickMediator.add_brick(brick_data)
        flash('Brick added successfully!', 'success')
        return redirect(url_for('bricks.bricks', brick_id=newBrick.id))
    return render_template('add_brick.html', manufacturers=manufacturers, selected_brick_id=selected_brick_id)

@bricks_bp.route('/edit_brick/<int:id>', methods=['GET', 'POST'])
@loginRequired
def editBrick(id):
    brick = BrickMediator.get_brick_by_id(id)
    manufacturers = ManufacturerMediator.get_all_manufacturers()
    if request.method == 'POST':
        name = request.form['name']
        # Duplicate name check via mediator (exclude self)
        if BrickMediator.duplicate_name_exists(name, exclude_id=brick.id):
            flash('A brick with this name already exists.', 'danger')
            return render_template('edit_brick.html', brick=brick, manufacturers=manufacturers)
        brick_data = {
            'name': name,
            'colour': request.form['colour'],
            'material': request.form['material'],
            'strength': request.form['strength'],
            'width': float(request.form['width']),
            'depth': float(request.form['depth']),
            'height': float(request.form['height']),
            'type': request.form['type'],
            'voids': int(request.form['voids']),
            'manufacturerId': int(request.form['manufacturer_id'])
        }
        BrickMediator.update_brick(brick, brick_data)
        flash('Brick updated successfully!', 'success')
        return redirect(url_for('bricks.bricks', brick_id=brick.id))
    return render_template('edit_brick.html', brick=brick, manufacturers=manufacturers)

@bricks_bp.route('/delete_brick/<int:id>')
@loginRequired
def deleteBrick(id):
    BrickMediator.delete_brick(id)
    flash('Brick deleted successfully!', 'success')
    return redirect(url_for('bricks.bricks'))

@bricks_bp.route('/delete_bricks_by_manufacturer/<int:manufacturer_id>')
@loginRequired
def deleteBricksByManufacturer(manufacturer_id):
    BrickMediator.delete_bricks_by_manufacturer(manufacturer_id)
    flash('All bricks for the manufacturer have been deleted.', 'success')
    return redirect(url_for('manufacturers.manufacturers'))

# Utility function for internal use (not a route)
def delete_bricks_by_manufacturer(manufacturer_id):
    BrickMediator.delete_bricks_by_manufacturer(manufacturer_id)
