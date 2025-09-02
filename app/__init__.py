from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def set_login_message(app):
    login_manager.login_message = app.config.get('LOGIN_MESSAGE', 'Please log in to access this page.')

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    set_login_message(app)

    from app.routes.empresas import bp as empresas_bp
    app.register_blueprint(empresas_bp, url_prefix='/empresas')  # ← Nuevo

    from app.routes.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.routes.empleados import bp as empleados_bp
    app.register_blueprint(empleados_bp, url_prefix='/empleados')

    from app.routes.asignaciones import bp as asignaciones_bp
    app.register_blueprint(asignaciones_bp, url_prefix='/asignaciones')

    from app.routes.herramientas import bp as herramientas_bp
    app.register_blueprint(herramientas_bp, url_prefix='/herramientas')

    from app.routes.vehiculos import bp as vehiculos_bp
    app.register_blueprint(vehiculos_bp, url_prefix='/vehiculos')

    from app.routes.ubicaciones import bp as ubicaciones_bp
    app.register_blueprint(ubicaciones_bp, url_prefix='/ubicaciones')

    return app