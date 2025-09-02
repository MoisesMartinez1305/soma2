from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, DateField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, Regexp
from app.models import Empleado, Empresa

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class RegistrationForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    apellido_paterno = StringField('Apellido Paterno', validators=[DataRequired()])
    apellido_materno = StringField('Apellido Materno')
    telefono = StringField('Teléfono', validators=[
        DataRequired(),
        Length(min=10, max=10, message='El teléfono debe tener 10 dígitos'),
        Regexp(r'^[0-9]+$', message='Solo se permiten números')
    ])
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[DataRequired()])
    fecha_ingreso = DateField('Fecha de Ingreso', validators=[DataRequired()])
    sexo = SelectField('Sexo', choices=[('M', 'Masculino'), ('F', 'Femenino'), ('I', 'Indefinido')], validators=[DataRequired()])
    puesto = SelectField('Puesto', choices=[
        ('Ayudante general', 'Ayudante general'),
        ('Chofer', 'Chofer')
    ], validators=[DataRequired()])
    es_supervisor = BooleanField('Es Supervisor')
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    password2 = PasswordField('Repetir Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')


class EmpleadoEditForm(RegistrationForm):
    sexo = SelectField('Sexo', choices=[('M', 'Masculino'), ('F', 'Femenino'), ('I', 'Indefinido')], validators=[DataRequired()])
    estatus = SelectField('Estatus', choices=[
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
        ('Vacaciones', 'Vacaciones'),
        ('Incapacitado', 'Incapacitado')
    ])
    supervisor_id = SelectField('Supervisor', coerce=int)
    reset_password = BooleanField('Resetear contraseña')
    submit = SubmitField('Actualizar')
    
    def __init__(self, *args, **kwargs):
        # Guardar la instancia del empleado si se está editando
        self.empleado_actual = kwargs.get('obj')
        super(EmpleadoEditForm, self).__init__(*args, **kwargs)
        
        # Hacer los campos de contraseña opcionales por defecto
        self.password.validators = [Optional()]
        self.password2.validators = [Optional(), EqualTo('password')]
        
        self.supervisor_id.choices = [(0, 'Ninguno')] + [
            (e.id, f"{e.nombre} {e.apellido_paterno}") 
            for e in Empleado.query.filter_by(es_supervisor=True, estatus='Activo').all()
        ]
    
    def validate(self, extra_validators=None):
        # Validación personalizada
        if not super().validate(extra_validators):
            return False
        
        # Solo validar contraseñas si se marca reset_password
        if self.reset_password.data:
            if not self.password.data:
                self.password.errors.append('La contraseña es requerida')
                return False
            if self.password.data != self.password2.data:
                self.password2.errors.append('Las contraseñas no coinciden')
                return False
        
        return True
    
    
    def validate_username(self, username):
        # Solo validar si es un nuevo empleado o si el username cambió
        if self.empleado_actual is None or username.data != self.empleado_actual.username:
            empleado = Empleado.query.filter_by(username=username.data).first()
            if empleado:
                raise ValidationError('Este nombre de usuario ya está en uso')           

class AsignacionForm(FlaskForm):
    fecha = DateField('Fecha', validators=[DataRequired()])
    empleado_id = SelectField('Empleado', coerce=int, validators=[DataRequired()])
    empresa_id = SelectField('Empresa', coerce=int, validators=[DataRequired()])
    supervisor_id = SelectField('Supervisor', coerce=int, validators=[DataRequired()])
    detalles = TextAreaField('Detalles')
    submit = SubmitField('Guardar')
    
    def __init__(self, *args, **kwargs):
        super(AsignacionForm, self).__init__(*args, **kwargs)
        self.empleado_id.choices = [
            (e.id, f"{e.nombre} {e.apellido_paterno}") 
            for e in Empleado.query.filter_by(estatus='Activo').all()
        ]
        self.empresa_id.choices = [
            (e.id, e.nombre) for e in Empresa.query.all()
        ]
        self.supervisor_id.choices = [
            (e.id, f"{e.nombre} {e.apellido_paterno}") 
            for e in Empleado.query.filter_by(es_supervisor=True, estatus='Activo').all()
        ]

class HerramientaForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired()])
    categoria = SelectField('Categoría', choices=[
        ('Jardinería', 'Jardinería'),
        ('Limpieza', 'Limpieza'),
        ('Mantenimiento', 'Mantenimiento'),
        ('Construcción', 'Construcción'),
        ('Electricidad', 'Electricidad'),
        ('Fontanería', 'Fontanería'),
        ('Otros', 'Otros')
    ])
    cantidad = StringField('Cantidad', validators=[DataRequired()])
    estatus = SelectField('Estatus', choices=[
        ('Disponible', 'Disponible'),
        ('En uso', 'En uso'),
        ('Mantenimiento', 'Mantenimiento'),
        ('Dañado', 'Dañado')
    ])
    descripcion = TextAreaField('Descripción')
    responsable_id = SelectField('Responsable', coerce=int)
    submit = SubmitField('Guardar')
    
    def __init__(self, *args, **kwargs):
        super(HerramientaForm, self).__init__(*args, **kwargs)
        self.responsable_id.choices = [(0, 'Bodega')] + [
            (e.id, f"{e.nombre} {e.apellido_paterno}") 
            for e in Empleado.query.filter_by(es_supervisor=True, estatus='Activo').all()
        ]

class EmpresaForm(FlaskForm):
    nombre = StringField('Nombre de la Empresa', validators=[DataRequired()], 
                        render_kw={"placeholder": "Ej: Empresa ABC, S.A. de C.V."})
    contacto = StringField('Persona de Contacto', 
                          render_kw={"placeholder": "Nombre del contacto principal"})
    telefono = StringField('Teléfono', 
                          render_kw={"placeholder": "Ej: 555-123-4567"})
    direccion = TextAreaField('Dirección', 
                             render_kw={"placeholder": "Dirección completa de la empresa", "rows": 3})
    submit = SubmitField('Guardar Empresa', render_kw={"class": "btn btn-primary"})

class VehiculoForm(FlaskForm):
    marca = StringField('Marca', validators=[DataRequired()])
    modelo = StringField('Modelo', validators=[DataRequired()])
    año = StringField('Año', validators=[DataRequired()])
    placas = StringField('Placas', validators=[DataRequired()])
    kilometraje = StringField('Kilometraje', validators=[DataRequired()])
    estatus = SelectField('Estatus', choices=[
        ('Disponible', 'Disponible'),
        ('En uso', 'En uso'),
        ('Mantenimiento', 'Mantenimiento'),
        ('Dañado', 'Dañado')
    ])
    asignado_id = SelectField('Asignado a', coerce=int)
    submit = SubmitField('Guardar')
    
    def __init__(self, *args, **kwargs):
        super(VehiculoForm, self).__init__(*args, **kwargs)
        self.asignado_id.choices = [(0, 'No asignado')] + [
            (e.id, f"{e.nombre} {e.apellido_paterno}") 
            for e in Empleado.query.filter_by(es_supervisor=True, estatus='Activo').all()
        ]