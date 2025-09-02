# Esta función simularía la consulta a la base de datos de CURPs
# En un caso real, se conectaría a un servicio oficial
def consultar_curp(curp):
    # Simulación de consulta a base de datos de CURP
    # En una implementación real, esto se conectaría a un API oficial
    
    # Diccionario de ejemplo con algunas CURPs predefinidas
    base_datos_curp = {
        "HEMM560427MDFRRN09": {
            "nombre": "MARIA",
            "apellido_paterno": "HERNANDEZ",
            "apellido_materno": "MARTINEZ",
            "fecha_nacimiento": "1960-04-27",
            "sexo": "MUJER",
            "entidad_nacimiento": "DISTRITO FEDERAL"
        },
        "ROGJ770912HDFMNS01": {
            "nombre": "JUAN",
            "apellido_paterno": "RODRIGUEZ",
            "apellido_materno": "GOMEZ",
            "fecha_nacimiento": "1977-09-12",
            "sexo": "HOMBRE",
            "entidad_nacimiento": "DISTRITO FEDERAL"
        }
        # Agregar más registros según sea necesario
    }
    
    return base_datos_curp.get(curp.upper())