

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Ubicacion, Empleado
from datetime import datetime
import pytz


bp = Blueprint('ubicaciones', __name__)



# Ruta para borrar todas las ubicaciones (solo admin)
@bp.route('/borrar_todas', methods=['POST'])
@login_required
def borrar_todas_ubicaciones():
    if not current_user.es_administrador:
        return 'No autorizado', 403
    Ubicacion.query.delete()
    db.session.commit()
    from sqlalchemy import func
    fecha = datetime.utcnow().date()
    return render_template('ubicaciones/list.html', entradas=[], salidas=[], fecha=fecha)


# Nueva ruta para ver ubicaciones con filtros y separación de entrada/salida
@bp.route('/list', methods=['GET'])
@login_required
def list_ubicaciones():
    from sqlalchemy import func
    fecha_str = request.args.get('fecha')
    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except Exception:
            tz = pytz.timezone('America/Mexico_City')
            fecha = datetime.now(tz).date()
    else:
        tz = pytz.timezone('America/Mexico_City')
        fecha = datetime.now(tz).date()

    if current_user.es_administrador:
        empleados = Empleado.query.filter(Empleado.estatus == 'Activo').all()
        entradas = Ubicacion.query.filter(
            Ubicacion.tipo == 'entrada',
            func.date(Ubicacion.fecha_hora) == fecha
        ).order_by(Ubicacion.fecha_hora.desc()).all()
        salidas = Ubicacion.query.filter(
            Ubicacion.tipo == 'salida',
            func.date(Ubicacion.fecha_hora) == fecha
        ).order_by(Ubicacion.fecha_hora.desc()).all()

        empleados_con_entrada = set(u.empleado_id for u in entradas)
        empleados_con_salida = set(u.empleado_id for u in salidas)
        empleados_faltan_entrada = [e for e in empleados if e.id not in empleados_con_entrada]
        empleados_faltan_salida = [e for e in empleados if e.id not in empleados_con_salida]

        return render_template('ubicaciones/list.html', entradas=entradas, salidas=salidas, fecha=fecha,
                               empleados_faltan_entrada=empleados_faltan_entrada,
                               empleados_faltan_salida=empleados_faltan_salida,
                               total_empleados=len(empleados))
    else:
        entradas = Ubicacion.query.filter(
            Ubicacion.empleado_id == current_user.id,
            Ubicacion.tipo == 'entrada',
            func.date(Ubicacion.fecha_hora) == fecha
        ).order_by(Ubicacion.fecha_hora.desc()).all()
        salidas = Ubicacion.query.filter(
            Ubicacion.empleado_id == current_user.id,
            Ubicacion.tipo == 'salida',
            func.date(Ubicacion.fecha_hora) == fecha
        ).order_by(Ubicacion.fecha_hora.desc()).all()
        return render_template('ubicaciones/list.html', entradas=entradas, salidas=salidas, fecha=fecha)


@bp.route('/registrar', methods=['GET', 'POST'])
@login_required
def registrar_ubicacion():
    from sqlalchemy import and_, func
    if request.method == 'POST':
        data = request.get_json()

        latitud = data.get('latitud')
        longitud = data.get('longitud')
        tipo = data.get('tipo')  # 'entrada' o 'salida'
        fecha_hora_local = data.get('fecha_hora_local')

        if not latitud or not longitud or not tipo or not fecha_hora_local:
            return jsonify({'error': 'Datos incompletos'}), 400


        try:
            fecha_hora = datetime.fromisoformat(fecha_hora_local.replace('Z', '+00:00'))
        except Exception:
            fecha_hora = datetime.utcnow()

        # Convertir a zona de México para la comparación
        tz = pytz.timezone('America/Mexico_City')
        fecha_hora_mx = fecha_hora.astimezone(tz)
        hoy_mx = fecha_hora_mx.date()
        existe = Ubicacion.query.filter(
            Ubicacion.empleado_id == current_user.id,
            Ubicacion.tipo == tipo,
            func.date(Ubicacion.fecha_hora) == hoy_mx
        ).first()
        if existe:
            return jsonify({'error': f'Ya registraste {tipo} hoy.'}), 400

        ubicacion = Ubicacion(
            empleado_id=current_user.id,
            latitud=latitud,
            longitud=longitud,
            tipo=tipo,
            fecha_hora=fecha_hora
        )
        db.session.add(ubicacion)
        db.session.commit()
        return jsonify({'message': 'Ubicación registrada exitosamente'})

    # Usar zona horaria de México para la consulta del día actual
    tz = pytz.timezone('America/Mexico_City')
    ahora_mx = datetime.now(tz)
    hoy_mx = ahora_mx.date()
    entrada_hoy = Ubicacion.query.filter(
        Ubicacion.empleado_id == current_user.id,
        Ubicacion.tipo == 'entrada',
        func.date(Ubicacion.fecha_hora) == hoy_mx
    ).first()
    salida_hoy = Ubicacion.query.filter(
        Ubicacion.empleado_id == current_user.id,
        Ubicacion.tipo == 'salida',
        func.date(Ubicacion.fecha_hora) == hoy_mx
    ).first()
    return render_template('ubicaciones/registrar.html', 
                          title='Registrar Ubicación',
                          entrada_registrada=entrada_hoy is not None,
                          salida_registrada=salida_hoy is not None)