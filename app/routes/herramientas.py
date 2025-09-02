from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Herramienta, Empleado
from app.forms import HerramientaForm

bp = Blueprint('herramientas', __name__)

@bp.route('/')
@login_required
def list_herramientas():
    herramientas = Herramienta.query.all()
    return render_template('herramientas/list.html', title='Herramientas', herramientas=herramientas)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_herramienta():
    if not current_user.es_administrador:
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.index'))
    
    form = HerramientaForm()
    if form.validate_on_submit():
        herramienta = Herramienta(
            nombre=form.nombre.data,
            categoria=form.categoria.data,
            cantidad=form.cantidad.data,
            estatus=form.estatus.data,
            descripcion=form.descripcion.data,
            responsable_id=form.responsable_id.data if form.responsable_id.data != 0 else None
        )
        db.session.add(herramienta)
        db.session.commit()
        flash('Herramienta creada exitosamente', 'success')
        return redirect(url_for('herramientas.list_herramientas'))
    
    return render_template('herramientas/create.html', title='Crear Herramienta', form=form)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_herramienta(id):
    if not current_user.es_administrador:
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.index'))
    
    herramienta = Herramienta.query.get_or_404(id)
    form = HerramientaForm(obj=herramienta)
    
    if form.validate_on_submit():
        herramienta.nombre = form.nombre.data
        herramienta.categoria = form.categoria.data
        herramienta.cantidad = form.cantidad.data
        herramienta.estatus = form.estatus.data
        herramienta.descripcion = form.descripcion.data
        herramienta.responsable_id = form.responsable_id.data if form.responsable_id.data != 0 else None
        
        db.session.commit()
        flash('Herramienta actualizada exitosamente', 'success')
        return redirect(url_for('herramientas.list_herramientas'))
    
    # Establecer valor inicial para el responsable
    if herramienta.responsable_id:
        form.responsable_id.data = herramienta.responsable_id
    else:
        form.responsable_id.data = 0
    
    return render_template('herramientas/edit.html', title='Editar Herramienta', form=form, herramienta=herramienta)

# Ruta para eliminar herramienta
@bp.route('/delete/<int:id>', methods=['POST', 'GET'])
@login_required
def delete_herramienta(id):
    if not current_user.es_administrador:
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.index'))
    herramienta = Herramienta.query.get_or_404(id)
    db.session.delete(herramienta)
    db.session.commit()
    flash('Herramienta eliminada exitosamente', 'success')
    return redirect(url_for('herramientas.list_herramientas'))