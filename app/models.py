from datetime import datetime, date
from zoneinfo import ZoneInfo

def mexico_now():
    return datetime.now(ZoneInfo('America/Mexico_City'))
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class Empleado(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telefono = db.Column(db.String(10), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido_paterno = db.Column(db.String(100), nullable=False)
    apellido_materno = db.Column(db.String(100))
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    sexo = db.Column(db.String(1), nullable=False)  # 'M' o 'F'
    fecha_ingreso = db.Column(db.Date, nullable=False)
    puesto = db.Column(db.String(100), nullable=False)
    es_supervisor = db.Column(db.Boolean, default=False)
    es_administrador = db.Column(db.Boolean, default=False)
    estatus = db.Column(db.String(20), default='Activo')
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(512))
    asignaciones = db.relationship('Asignacion', 
                                  foreign_keys='Asignacion.empleado_id',
                                  backref='empleado_rel', 
                                  lazy='dynamic')
    
    # Relaciones
    supervisor_id = db.Column(db.Integer, db.ForeignKey('empleado.id'))
    supervisor = db.relationship('Empleado', remote_side=[id], backref='supervisados')
    
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculo.id'))
    vehiculo = db.relationship('Vehiculo', backref='asignado_a')
    
    # Relaciones sin backref para evitar conflictos
    herramientas = db.relationship('Herramienta', backref='herramienta_responsable', lazy='dynamic')
    ubicaciones = db.relationship('Ubicacion', backref='ubicacion_empleado', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def dias_trabajando(self):
        dias = (date.today() - self.fecha_ingreso).days
        if dias < 0:
            return "-"
        años = dias // 365
        dias_restantes = dias % 365
        partes = []
        if años > 0:
            partes.append(f"{años} año{'s' if años > 1 else ''}")
        if dias_restantes > 0 or años == 0:
            partes.append(f"{dias_restantes} día{'s' if dias_restantes != 1 else ''}")
        return ", ".join(partes) + " trabajando"
    
    def edad(self):
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
    
    def __repr__(self):
        return f'<Empleado {self.nombre} {self.apellido_paterno}>'

class Empresa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    direccion = db.Column(db.Text)
    contacto = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    
    def __repr__(self):
        return f'<Empresa {self.nombre}>'

class Vehiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    año = db.Column(db.Integer, nullable=False)
    placas = db.Column(db.String(10), unique=True, nullable=False)
    kilometraje = db.Column(db.Integer, default=0)
    estatus = db.Column(db.String(20), default='Disponible')
    
    def __repr__(self):
        return f'<Vehiculo {self.marca} {self.modelo} {self.placas}>'

class Herramienta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    categoria = db.Column(db.String(50))
    cantidad = db.Column(db.Integer, default=1)
    estatus = db.Column(db.String(20), default='Disponible')
    
    # Relación con el supervisor responsable
    responsable_id = db.Column(db.Integer, db.ForeignKey('empleado.id'))
    
    def __repr__(self):
        return f'<Herramienta {self.nombre}>'

class Asignacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False, default=date.today)
    detalles = db.Column(db.Text)
    
    # Relaciones
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleado.id'), nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    supervisor_id = db.Column(db.Integer, db.ForeignKey('empleado.id'), nullable=False)
    
    # Definir las relaciones sin backref para evitar conflictos
    empleado = db.relationship('Empleado', foreign_keys=[empleado_id], backref='asignaciones_empleado')
    empresa = db.relationship('Empresa', foreign_keys=[empresa_id], backref='asignaciones_empresa')
    supervisor = db.relationship('Empleado', foreign_keys=[supervisor_id], backref='asignaciones_supervisor')
    
    def __repr__(self):
        return f'<Asignacion {self.id} - {self.fecha}>'

class Ubicacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, nullable=False, default=mexico_now)
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # 'entrada' o 'salida'
    
    # Relación con el empleado
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleado.id'), nullable=False)
    
    def __repr__(self):
        return f'<Ubicacion {self.id} - {self.tipo} - {self.fecha_hora}>'

@login_manager.user_loader
def load_user(id):
    return Empleado.query.get(int(id))