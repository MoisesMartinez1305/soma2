from app import create_app, db
from app.models import Empleado

app = create_app()

@app.cli.command("init-db")
def init_db():
    """Inicializa la base de datos y crea un usuario administrador"""
    
    with app.app_context():  # ¡TODO debe estar dentro del contexto!
        # Crear todas las tablas
        db.create_all()

        # Crear usuario administrador por defecto
        admin = Empleado(
            telefono="5551234567",
            nombre="Administrador",
            apellido_paterno="Sistema",
            apellido_materno="SOMA",
            fecha_nacimiento="1990-01-01",
            fecha_ingreso="2023-01-01",
            puesto="Administrador",
            es_supervisor=True,
            es_administrador=True,
            username="admin",
            sexo='M'  # Asignar un valor por defecto para sexo
        )
        admin.set_password("admin123")
        
        db.session.add(admin)
        db.session.commit()
        print("Base de datos inicializada y usuario administrador creado")

if __name__ == '__main__':
    app.run(debug=True)