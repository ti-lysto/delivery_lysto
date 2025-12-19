"""
Conexión MySQL y creación de tabla de prueba – Español
-----------------------------------------------------
"""
import os
import logging
import pymysql
from typing import Optional
from ..configuracion import Configuracion

logger = logging.getLogger(__name__)

# Variables de entorno con defaults solicitados
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "LystoLocal")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")


def get_connection(db: Optional[str] = None) -> pymysql.connections.Connection:
    """Obtiene una conexión a MySQL.
    Si `db` es None, se conecta sin seleccionar base para poder crearla.
    """
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=db,
        autocommit=True,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    return conn

def probar_conexion() -> bool:

    """Prueba la conexión a la base de datos e imprime el estado."""
    try:
        conn = get_connection(db=DB_NAME)
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
        print(f"Conexión exitosa a la base de datos '{DB_NAME}' en {DB_HOST}:{DB_PORT} como usuario '{DB_USER}'.")
        if Configuracion.DEBUG:
            logger.info(f"Conexión exitosa a la base de datos '{DB_NAME}' en {DB_HOST}:{DB_PORT} como usuario '{DB_USER}'.")
        return True
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        if Configuracion.DEBUG:
            logger.error(f"Error al conectar a la base de datos: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def ejecutar_sp_bool(sp_name: str, *args) -> bool:
    """Ejecuta un procedimiento almacenado con resultado booleano."""
    try:
        conn = get_connection(db=DB_NAME)
        with conn.cursor() as cur:
            cur.callproc(sp_name, args)
        if Configuracion.DEBUG:
            logger.info(f"Procedimiento almacenado '{sp_name}' ejecutado con éxito.")
        return True
    except Exception as e:
        if Configuracion.DEBUG:
            logger.error(f"Error al ejecutar el procedimiento almacenado: {e} con SP '{sp_name}' y argumentos {args}.")
        print(f"Error al ejecutar el procedimiento almacenado: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def ejecutar_sp_void(sp_name: str, *args) -> None:
    """Ejecuta un procedimiento almacenado sin resultado."""
    try:
        conn = get_connection(db=DB_NAME)
        with conn.cursor() as cur:
            cur.callproc(sp_name, args)
        if Configuracion.DEBUG:
            logger.info(f"Procedimiento almacenado '{sp_name}' ejecutado con éxito.")
    except Exception as e:
        if Configuracion.DEBUG:
            logger.error(f"Error al ejecutar el procedimiento almacenado: {e} con SP '{sp_name}' y argumentos {args}.")
        print(f"Error al ejecutar el procedimiento almacenado: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def ejecutar_sp_resultados(sp_name: str, *args) -> list[dict]:
    """Ejecuta un procedimiento almacenado y devuelve los resultados."""
    resultados = []
    try:
        conn = get_connection(db=DB_NAME)
        with conn.cursor() as cur:
            cur.callproc(sp_name, args)
            resultados = cur.fetchall()
        if Configuracion.DEBUG:
            logger.info(f"Procedimiento almacenado '{sp_name}' ejecutado con éxito. Resultados obtenidos.")
        return resultados
    except Exception as e:
        if Configuracion.DEBUG:
            logger.error(f"Error al ejecutar el procedimiento almacenado: {e} con SP '{sp_name}' y argumentos {args}.")
        print(f"Error al ejecutar el procedimiento almacenado: {e}")
        return resultados
    finally:
        if 'conn' in locals():
            conn.close()

def ejecutar_vista(vista_name: str) -> list[dict]:
    """Ejecuta una vista y devuelve los resultados."""
    resultados = []
    try:
        conn = get_connection(db=DB_NAME)
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {vista_name};")
            resultados = cur.fetchall()
        if Configuracion.DEBUG:
            logger.info(f"Vista '{vista_name}' ejecutada con éxito. Resultados obtenidos.")
        return resultados
    except Exception as e:
        if Configuracion.DEBUG:
            logger.error(f"Error al ejecutar la vista: {e} con nombre '{vista_name}'.")
        print(f"Error al ejecutar la vista: {e}")
        return resultados
    finally:
        if 'conn' in locals():
            conn.close()

