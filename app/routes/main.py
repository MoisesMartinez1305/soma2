from flask import send_file, request, url_for
import io
from weasyprint import HTML

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Empleado, Asignacion
from datetime import date, timedelta, datetime
from sqlalchemy import func, extract

bp = Blueprint('main', __name__)


@bp.route('/exportar_asignaciones_pdf')
@login_required
def exportar_asignaciones_pdf():
    fecha_str = request.args.get('fecha')
    # Extraer fecha en formato dd/mm/yyyy
    try:
        dia, mes, anio = map(int, fecha_str.split()[1].split('/'))
        fecha = date(anio, mes, dia)
    except Exception:
        fecha = date.today()
    asignaciones_hoy = Asignacion.query.filter_by(fecha=fecha).all()
    # Renderizar HTML para PDF
    rendered = render_template('pdf/asignaciones.html', asignaciones_hoy=asignaciones_hoy, fecha=fecha, url_logo=url_for('static', filename='img/logo.png', _external=True))
    pdf_io = io.BytesIO()
    HTML(string=rendered, base_url=request.base_url).write_pdf(pdf_io)
    pdf_io.seek(0)
    return send_file(pdf_io, mimetype='application/pdf', as_attachment=True, download_name=f'Asignaciones_{fecha.strftime('%d-%m-%Y')}.pdf')


@bp.route('/cumpleanos')
@login_required
def cumpleanos():
    hoy = date.today()
    empleados_todos = Empleado.query.all()
    # Calcular días faltantes para cada empleado
    empleados_con_dias = []
    for e in empleados_todos:
        cumple_este_año = date(hoy.year, e.fecha_nacimiento.month, e.fecha_nacimiento.day)
        if cumple_este_año < hoy:
            cumple_este_año = date(hoy.year + 1, e.fecha_nacimiento.month, e.fecha_nacimiento.day)
        dias_faltantes = (cumple_este_año - hoy).days
        empleados_con_dias.append({
            'empleado': e,
            'dias_faltantes': dias_faltantes,
            'fecha_cumple': cumple_este_año
        })

    orden = request.args.get('orden', 'proximo')
    if orden == 'ultimo':
        empleados_ordenados = sorted(empleados_con_dias, key=lambda x: x['dias_faltantes'], reverse=True)
    else:
        empleados_ordenados = sorted(empleados_con_dias, key=lambda x: x['dias_faltantes'])

    return render_template('cumpleanos.html', empleados_cumple=empleados_ordenados, hoy=hoy)




@bp.route('/')
@bp.route('/index')
@login_required
def index():
    # Obtener cumpleaños próximos (próximos 30 días)
    hoy = date.today()
    
    # Obtener todos los empleados (para sección de cumpleaños en encabezado)
    empleados_todos = Empleado.query.all()
    empleados_ordenados_cumple = sorted(
        empleados_todos,
        key=lambda e: ((date(hoy.year, e.fecha_nacimiento.month, e.fecha_nacimiento.day) - hoy).days if date(hoy.year, e.fecha_nacimiento.month, e.fecha_nacimiento.day) >= hoy else (date(hoy.year + 1, e.fecha_nacimiento.month, e.fecha_nacimiento.day) - hoy).days)
    )
    
    # Calcular días hasta cumpleaños para cada empleado
    cumpleaños_proximos = []
    for empleado in empleados_todos:
        # Crear fecha de cumpleaños de este año
        cumple_este_año = date(hoy.year, empleado.fecha_nacimiento.month, empleado.fecha_nacimiento.day)
        
        # Si ya pasó este año, calcular para el próximo año
        if cumple_este_año < hoy:
            cumple_este_año = date(hoy.year + 1, empleado.fecha_nacimiento.month, empleado.fecha_nacimiento.day)
        
        # Calcular días faltantes
        dias_faltantes = (cumple_este_año - hoy).days
        
        # Solo incluir si es dentro de los próximos 30 días
        if dias_faltantes <= 30:
            cumpleaños_proximos.append({
                'empleado': empleado,
                'dias_faltantes': dias_faltantes,
                'fecha_cumple': cumple_este_año
            })
    
    # Ordenar por días faltantes (más próximo primero)
    cumpleaños_proximos.sort(key=lambda x: x['dias_faltantes'])
    
    # Obtener asignaciones del día actual
    asignaciones_hoy = Asignacion.query.filter_by(fecha=hoy).all()
    
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    nombre_dia = dias_semana[hoy.weekday()]
    fecha_actual = f"{nombre_dia} {hoy.strftime('%d/%m/%Y')}"
    return render_template('index.html', 
                          title='Inicio',
                          cumpleaños_proximos=cumpleaños_proximos,
                          empleados_cumple=empleados_ordenados_cumple,
                          asignaciones_hoy=asignaciones_hoy,
                          fecha_actual=fecha_actual,
                          hoy=hoy)