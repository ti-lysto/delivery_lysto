"""
Inicializa la base de datos creando la tabla de prueba.
Uso:
    python -m zoom_api.scripts.init_db
"""
from ..db.conexion import probar_conexion, DB_HOST, DB_PORT, DB_NAME, DB_USER


def main() -> None:
    if probar_conexion():
        print(f"Conexión exitosa a la base de datos en {DB_HOST}:{DB_PORT}/{DB_NAME} (usuario {DB_USER}).")
    else:
        print("No se pudo establecer conexión con la base de datos.")


if __name__ == "__main__":
    main()
