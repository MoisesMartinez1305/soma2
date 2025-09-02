from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Vehiculo, Empleado
from app.forms import VehiculoForm

bp = Blueprint('vehiculos', __name__)

@bp.route('/')
@login_required
def list_vehiculos():
    vehiculos = Vehiculo.query.all()
    return render_template('vehiculos/list.html', title='Vehículos', vehiculos=vehiculos)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_vehiculo():
    if not current_user.es_administrador:
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.index'))
    
    form = VehiculoForm()
    if form.validate_on_submit():
        vehiculo = Vehiculo(
            marca=form.marca.data,
            modelo=form.modelo.data,
            año=form.año.data,
            placas=form.placas.data,
            kilometraje=form.kilometraje.data,
            estatus=form.estatus.data
        )
        
        if form.asignado_id.data != 0:
            vehiculo.asignado_id = form.asignado_id.data
        
        db.session.add(vehiculo)
        db.session.commit()
        flash('Vehículo creado exitosamente', 'success')
        return redirect(url_for('vehiculos.list_vehiculos'))
    
    return render_template('vehiculos/create.html', title='Crear Vehículo', form=form)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_vehiculo(id):
    if not current_user.es_administrador:
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.index'))
    
    vehiculo = Vehiculo.query.get_or_404(id)
    form = VehiculoForm(obj=vehiculo)
    
    if form.validate_on_submit():
        vehiculo.marca = form.marca.data
        vehiculo.modelo = form.modelo.data
        vehiculo.año = form.año.data
        vehiculo.placas = form.placas.data
        vehiculo.kilometraje = form.kilometraje.data
        vehiculo.estatus = form.estatus.data
        vehiculo.asignado_id = form.asignado_id.data if form.asignado_id.data != 0 else None
        
        db.session.commit()
        flash('Vehículo actualizado exitosamente', 'success')
        return redirect(url_for('vehiculos.list_vehiculos'))
    
    # Establecer valor inicial para el asignado
    if vehiculo.asignado_id:
        form.asignado_id.data = vehiculo.asignado_id
    else:
        form.asignado_id.data = 0
    
    return render_template('vehiculos/edit.html', title='Editar Vehículo', form=form, vehiculo=vehiculo)

# Ruta para eliminar vehículo
@bp.route('/delete/<int:id>', methods=['POST', 'GET'])
@login_required
def delete_vehiculo(id):
    if not current_user.es_administrador:
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.index'))
    vehiculo = Vehiculo.query.get_or_404(id)
    db.session.delete(vehiculo)
    db.session.commit()
    flash('Vehículo eliminado exitosamente', 'success')
    return redirect(url_for('vehiculos.list_vehiculos'))