
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Empleado, Asignacion
from app.forms import EmpleadoEditForm
from app.utils.curp_utils import consultar_curp

bp = Blueprint('empleados', __name__)

@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_empleado(id):
    if not current_user.es_administrador:
        flash('No tienes permisos para realizar esta acción', 'danger')
        return redirect(url_for('empleados.list_empleados'))
    empleado = Empleado.query.get_or_404(id)
    db.session.delete(empleado)
    db.session.commit()
    flash('Empleado eliminado exitosamente', 'success')
    return redirect(url_for('empleados.list_empleados'))

@bp.route('/')
@login_required
def list_empleados():
    empleados = Empleado.query.all()
    return render_template('empleados/list.html', title='Empleados', empleados=empleados)

@bp.route('/<int:id>')
@login_required
def detail_empleado(id):
    empleado = Empleado.query.get_or_404(id)
    return render_template('empleados/detail.html', title='Detalle Empleado', empleado=empleado, Asignacion=Asignacion)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_empleado():
    if not current_user.es_administrador:
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.index'))
    
    form = EmpleadoEditForm()
    if form.validate_on_submit():
        empleado = Empleado(
            telefono=form.telefono.data,
            nombre=form.nombre.data,
            apellido_paterno=form.apellido_paterno.data,
            apellido_materno=form.apellido_materno.data,
            fecha_nacimiento=form.fecha_nacimiento.data,
            fecha_ingreso=form.fecha_ingreso.data,
            puesto=form.puesto.data,
            es_supervisor=form.es_supervisor.data,
            username=form.username.data,
            sexo=form.sexo.data
        )
        empleado.set_password(form.password.data)
        db.session.add(empleado)
        db.session.commit()
        flash('Empleado creado exitosamente', 'success')
        return redirect(url_for('empleados.list_empleados'))
    
    return render_template('empleados/create.html', title='Crear Empleado', form=form)

    
@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_empleado(id):
    if not current_user.es_administrador:
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.index'))
    
    empleado = Empleado.query.get_or_404(id)
    
    # Pasar la instancia del empleado al formulario para las validaciones
    form = EmpleadoEditForm(obj=empleado)
    
    if form.validate_on_submit():
        # Verificar si los campos únicos cambiaron
        if form.telefono.data != empleado.telefono:
            empleado_existente = Empleado.query.filter_by(telefono=form.telefono.data).first()
            if empleado_existente and empleado_existente.id != empleado.id:
                flash('Ya existe un empleado con este teléfono', 'danger')
                return render_template('empleados/edit.html', title='Editar Empleado', form=form, empleado=empleado)

        if form.username.data != empleado.username:
            usuario_existente = Empleado.query.filter_by(username=form.username.data).first()
            if usuario_existente and usuario_existente.id != empleado.id:
                flash('Ya existe un usuario con este nombre de usuario', 'danger')
                return render_template('empleados/edit.html', title='Editar Empleado', form=form, empleado=empleado)
        
        # Actualizar los campos
        empleado.nombre = form.nombre.data
        empleado.apellido_paterno = form.apellido_paterno.data
        empleado.apellido_materno = form.apellido_materno.data
        empleado.fecha_nacimiento = form.fecha_nacimiento.data
        empleado.fecha_ingreso = form.fecha_ingreso.data
        empleado.puesto = form.puesto.data
        empleado.es_supervisor = form.es_supervisor.data
        empleado.estatus = form.estatus.data
        empleado.username = form.username.data
        empleado.sexo = form.sexo.data

        if form.supervisor_id.data != 0:
            empleado.supervisor_id = form.supervisor_id.data
        else:
            empleado.supervisor_id = None

        if form.reset_password.data:
            empleado.set_password(form.password.data)

        db.session.commit()
        flash('Empleado actualizado exitosamente', 'success')
        return redirect(url_for('empleados.detail_empleado', id=empleado.id))
    
    # Establecer valores iniciales
    if empleado.supervisor_id:
        form.supervisor_id.data = empleado.supervisor_id
    else:
        form.supervisor_id.data = 0
    
    return render_template('empleados/edit.html', title='Editar Empleado', form=form, empleado=empleado)