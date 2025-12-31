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
DB_HOST = os.getenv("ZOOM_DB_HOST")
DB_PORT = int(os.getenv("ZOOM_DB_PORT"))
DB_NAME = os.getenv("ZOOM_DB_NAME")
DB_USER = os.getenv("ZOOM_DB_USER")
DB_PASSWORD = os.getenv("ZOOM_DB_PASSWORD")


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

def ejecutar_sp_resultados(sp_name: str, *args, arg_out: Optional[list[str]] = None) -> list[dict]:
    """Ejecuta un procedimiento almacenado y devuelve resultados y OUT params.

    Compatibilidad:
    - Si el SP retorna filas (SELECT dentro del SP), se agregan primero.
    - Los parámetros OUT se leen de forma genérica usando variables de sesión
      `@_sp_name_idx`. Si `arg_out` está definido, se asignan alias en ese orden
      a los últimos índices; si no, se intenta aliasar los dos últimos como
      `p_exito` y `p_mensaje`.
    - Se retorna una lista de dicts (filas + OUTs) para no romper consumidores.
    """
    resultados: list[dict] = []
    try:
        conn = get_connection(db=DB_NAME)
        with conn.cursor() as cur:
            # Ejecutar SP
            cur.callproc(sp_name, args)

            # Intentar obtener filas devueltas por el SP (si hay)
            try:
                filas = cur.fetchall()
                if filas:
                    resultados.extend(filas)
            except Exception:
                # Algunos SP no devuelven result set
                pass

            # Lectura genérica de OUT params vía variables de sesión
            total_params = len(args)
            if total_params > 0:
                if arg_out and len(arg_out) > 0:
                    # Mapear los últimos N índices a los alias proporcionados
                    start_idx = max(0, total_params - len(arg_out))
                    for offset, nombre in enumerate(arg_out):
                        idx = start_idx + offset
                        cur.execute(f"SELECT @_" + sp_name + f"_{idx} AS {nombre};")
                        out_row = cur.fetchone()
                        if out_row is not None:
                            resultados.append(out_row)
                else:
                    # Alias por defecto: últimos dos como p_exito y p_mensaje
                    if total_params >= 2:
                        # p_exito
                        cur.execute(f"SELECT @_" + sp_name + f"_{total_params-2} AS p_exito;")
                        exito_row = cur.fetchone()
                        if exito_row is not None:
                            resultados.append(exito_row)
                        # p_mensaje
                        cur.execute(f"SELECT @_" + sp_name + f"_{total_params-1} AS p_mensaje;")
                        mensaje_row = cur.fetchone()
                        if mensaje_row is not None:
                            resultados.append(mensaje_row)
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

