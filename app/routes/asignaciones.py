from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Asignacion, Empleado, Empresa
from app.forms import AsignacionForm

# Crear el Blueprint
bp = Blueprint('asignaciones', __name__)

from datetime import date, timedelta, datetime

@bp.route('/')
@login_required
def list_asignaciones():
    filtro = request.args.get('filtro')
    fecha_actual = date.today()
    asignaciones = Asignacion.query
    if filtro == 'hoy':
        asignaciones = asignaciones.filter(Asignacion.fecha == fecha_actual)
    elif filtro == 'semana':
        inicio_semana = fecha_actual - timedelta(days=fecha_actual.weekday())
        fin_semana = inicio_semana + timedelta(days=6)
        asignaciones = asignaciones.filter(Asignacion.fecha >= inicio_semana, Asignacion.fecha <= fin_semana)
    elif filtro == 'mes':
        inicio_mes = fecha_actual.replace(day=1)
        if fecha_actual.month == 12:
            fin_mes = fecha_actual.replace(year=fecha_actual.year+1, month=1, day=1) - timedelta(days=1)
        else:
            fin_mes = fecha_actual.replace(month=fecha_actual.month+1, day=1) - timedelta(days=1)
        asignaciones = asignaciones.filter(Asignacion.fecha >= inicio_mes, Asignacion.fecha <= fin_mes)
    elif filtro == 'fecha' and request.args.get('fecha_especifica'):
        try:
            fecha_esp = datetime.strptime(request.args.get('fecha_especifica'), '%Y-%m-%d').date()
            asignaciones = asignaciones.filter(Asignacion.fecha == fecha_esp)
        except Exception:
            pass
    asignaciones = asignaciones.order_by(Asignacion.fecha.desc()).all()
    return render_template('asignaciones/list.html', title='Asignaciones', asignaciones=asignaciones, fecha_actual=fecha_actual)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_asignacion():
    if not current_user.es_administrador:
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.index'))
    
    form = AsignacionForm()
    if form.validate_on_submit():
        asignacion = Asignacion(
            fecha=form.fecha.data,
            empleado_id=form.empleado_id.data,
            empresa_id=form.empresa_id.data,
            supervisor_id=form.supervisor_id.data,
            detalles=form.detalles.data
        )
        db.session.add(asignacion)
        db.session.commit()
        flash('Asignación creada exitosamente', 'success')
        return redirect(url_for('asignaciones.list_asignaciones'))
    
    return render_template('asignaciones/create.html', title='Crear Asignación', form=form)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_asignacion(id):
    if not current_user.es_administrador:
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.index'))
    
    asignacion = Asignacion.query.get_or_404(id)
    form = AsignacionForm(obj=asignacion)
    
    if form.validate_on_submit():
        asignacion.fecha = form.fecha.data
        asignacion.empleado_id = form.empleado_id.data
        asignacion.empresa_id = form.empresa_id.data
        asignacion.supervisor_id = form.supervisor_id.data
        asignacion.detalles = form.detalles.data
        
        db.session.commit()
        flash('Asignación actualizada exitosamente', 'success')
        return redirect(url_for('asignaciones.list_asignaciones'))
    
    return render_template('asignaciones/edit.html', title='Editar Asignación', form=form, asignacion=asignacion)

@bp.route('/delete/<int:id>')
@login_required
def delete_asignacion(id):
    if not current_user.es_administrador:
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.index'))
    
    asignacion = Asignacion.query.get_or_404(id)
    db.session.delete(asignacion)
    db.session.commit()
    flash('Asignación eliminada exitosamente', 'success')
    return redirect(url_for('asignaciones.list_asignaciones'))