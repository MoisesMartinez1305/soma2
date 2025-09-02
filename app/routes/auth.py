from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Empleado
from app.forms import LoginForm, RegistrationForm
from sqlalchemy.exc import IntegrityError

bp = Blueprint('auth', __name__)
# ¡FALTA ESTA FUNCIÓN!
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        empleado = Empleado.query.filter_by(username=form.username.data).first()
        if empleado is None or not empleado.check_password(form.password.data):
            flash('Usuario o contraseña inválidos', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(empleado, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Iniciar Sesión', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión exitosamente', 'success')
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if not current_user.es_administrador:
        flash('No tienes permisos para acceder a esta página', 'danger')
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            # Verificar si ya existe un empleado con ese teléfono
            empleado_existente = Empleado.query.filter_by(telefono=form.telefono.data).first()
            if empleado_existente:
                flash('Ya existe un empleado con este teléfono', 'danger')
                return render_template('auth/register.html', title='Registrar Empleado', form=form)

            # Verificar si ya existe un usuario con ese username
            usuario_existente = Empleado.query.filter_by(username=form.username.data).first()
            if usuario_existente:
                flash('Ya existe un empleado con este nombre de empleado', 'danger')
                return render_template('auth/register.html', title='Registrar Empleado', form=form)
            
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
            flash('Empleado registrado exitosamente', 'success')
            return redirect(url_for('empleados.list_empleados'))
            
        except IntegrityError:
            db.session.rollback()
            flash('Error: Ya existe un empleado con el mismo teléfono o nombre de empleado', 'danger')
            return render_template('auth/register.html', title='Registrar Empleado', form=form)
    
    return render_template('auth/register.html', title='Registrar Empleado', form=form)


