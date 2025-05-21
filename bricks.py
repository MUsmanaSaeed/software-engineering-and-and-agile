from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Brick, Manufacturer
from users import loginRequired

bricks_bp = Blueprint('bricks', __name__)

@bricks_bp.route('/bricks')
def bricks():
    allBricks = Brick.query.all()
    return render_template('bricks.html', bricks=allBricks)

@bricks_bp.route('/add_brick', methods=['GET', 'POST'])
@loginRequired
def addBrick():
    manufacturers = Manufacturer.query.all()
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
        newBrick = Brick(
            name=name, colour=colour, material=material, strength=strength,
            width=width, depth=depth, height=height, type=type_,
            voids=voids, manufacturerId=manufacturerId
        )
        db.session.add(newBrick)
        db.session.commit()
        flash('Brick added successfully!', 'success')
        return redirect(url_for('bricks.bricks'))
    return render_template('add_brick.html', manufacturers=manufacturers)

@bricks_bp.route('/edit_brick/<int:id>', methods=['GET', 'POST'])
@loginRequired
def editBrick(id):
    brick = Brick.query.get_or_404(id)
    manufacturers = Manufacturer.query.all()
    if request.method == 'POST':
        brick.name = request.form['name']
        brick.colour = request.form['colour']
        brick.material = request.form['material']
        brick.strength = request.form['strength']
        brick.width = float(request.form['width'])
        brick.depth = float(request.form['depth'])
        brick.height = float(request.form['height'])
        brick.type = request.form['type']
        brick.voids = int(request.form['voids'])
        brick.manufacturerId = int(request.form['manufacturer_id'])
        db.session.commit()
        flash('Brick updated successfully!', 'success')
        return redirect(url_for('bricks.bricks'))
    return render_template('edit_brick.html', brick=brick, manufacturers=manufacturers)

@bricks_bp.route('/delete_brick/<int:id>')
@loginRequired
def deleteBrick(id):
    brick = Brick.query.get_or_404(id)
    db.session.delete(brick)
    db.session.commit()
    flash('Brick deleted successfully!', 'success')
    return redirect(url_for('bricks.bricks'))
