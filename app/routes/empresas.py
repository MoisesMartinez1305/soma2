from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Empresa
from app.forms import EmpresaForm

bp = Blueprint('empresas', __name__)

def requiere_gerente(func):
    def wrapper(*args, **kwargs):
        if not current_user.es_administrador:
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@bp.route('/')
@login_required
@requiere_gerente
def list_empresas():
    empresas = Empresa.query.all()
    return render_template('empresas/list.html', title='Empresas', empresas=empresas)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
@requiere_gerente
def create_empresa():
    form = EmpresaForm()
    if form.validate_on_submit():
        empresa = Empresa(
            nombre=form.nombre.data,
            direccion=form.direccion.data,
            contacto=form.contacto.data,
            telefono=form.telefono.data
        )
        db.session.add(empresa)
        db.session.commit()
        flash('Empresa creada exitosamente', 'success')
        return redirect(url_for('empresas.list_empresas'))
    
    return render_template('empresas/create.html', title='Crear Empresa', form=form)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@requiere_gerente
def edit_empresa(id):
    empresa = Empresa.query.get_or_404(id)
    form = EmpresaForm(obj=empresa)
    
    if form.validate_on_submit():
        empresa.nombre = form.nombre.data
        empresa.direccion = form.direccion.data
        empresa.contacto = form.contacto.data
        empresa.telefono = form.telefono.data
        
        db.session.commit()
        flash('Empresa actualizada exitosamente', 'success')
        return redirect(url_for('empresas.list_empresas'))
    
    return render_template('empresas/edit.html', title='Editar Empresa', form=form, empresa=empresa)


@bp.route('/delete/<int:id>')
@login_required
@requiere_gerente
def delete_empresa(id):
    empresa = Empresa.query.get_or_404(id)
    
    # Primero eliminar todas las asignaciones relacionadas
    from app.models import Asignacion
    asignaciones = Asignacion.query.filter_by(empresa_id=id).all()
    
    for asignacion in asignaciones:
        db.session.delete(asignacion)
    
    # Ahora eliminar la empresa
    db.session.delete(empresa)
    db.session.commit()
    
    flash('Empresa y sus asignaciones eliminadas exitosamente', 'success')
    return redirect(url_for('empresas.list_empresas'))