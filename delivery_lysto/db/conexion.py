
import os
import logging
import mysql.connector
from typing import Optional, List, Dict, Any
from ..configuracion import Configuracion
from mysql.connector import pooling, Error

logger = logging.getLogger(__name__)

# Variables de entorno con defaults solicitados
DB_HOST = os.getenv("ZOOM_DB_HOST")
DB_PORT = os.getenv("ZOOM_DB_PORT")
DB_NAME = os.getenv("ZOOM_DB_NAME")
DB_USER = os.getenv("ZOOM_DB_USER")
DB_PASSWORD = os.getenv("ZOOM_DB_PASSWORD")


def get_connection(db: Optional[str] = None) -> mysql.connector.connection.MySQLConnection:
    """Obtiene conexión usando mysql-connector-python."""
    try:
        config = {
            'host': DB_HOST,
            'port': DB_PORT,  # Asegurar que sea int
            'user': DB_USER,
            'password': DB_PASSWORD,
            'database': db,  # Puede ser None
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'use_unicode': True,
            'autocommit': True,  # Similar a pymysql
            'pool_name': 'delivery_pool',  # Opcional: pooling
            'pool_size': 5
        }
        
        # Remover database si es None (para conexión inicial)
        if db is None:
            config.pop('database', None)
        
        conn = mysql.connector.connect(**config)
        return conn 
        
    except Error as e:
        logger.error(f"Error conectando a MySQL: {e}")
        raise
def probar_conexion() -> bool:
    """Prueba la conexión a la base de datos e imprime el estado."""
    conn = None  # Inicializar como None
    
    try:
        conn = get_connection(db=DB_NAME)
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            result = cur.fetchone()
            
        print(f"✅ Conexión exitosa a la base de datos '{DB_NAME}' en {DB_HOST}:{DB_PORT}")
        print(f"   Usuario: '{DB_USER}'")
        print(f"   Test query: {result}")
        
        if Configuracion.DEBUG:
            logger.info(f"Conexión exitosa a '{DB_NAME}' en {DB_HOST}:{DB_PORT}")
        
        return True
        
    except Exception as e:        
        print(f"❌ Error al conectar a la base de datos:")
        print(f"   Host: {DB_HOST}:{DB_PORT}")
        print(f"   Database: {DB_NAME}")
        print(f"   User: {DB_USER}")
        print(f"   Error: {e}")
        
        if Configuracion.DEBUG:
            logger.error(f"Error al conectar a la base de datos: {e}")
        
        return False
        
    finally:
        if conn:
            try:
                conn.close()
                if Configuracion.DEBUG:
                    logger.debug("Conexión cerrada")
            except Exception as e:
                if Configuracion.DEBUG:
                    logger.warning(f"Error cerrando conexión: {e}")

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
    # """Ejecuta un procedimiento almacenado y devuelve resultados y OUT params.

    # Compatibilidad:
    # - Si el SP retorna filas (SELECT dentro del SP), se agregan primero.
    # - Los parámetros OUT se leen de forma genérica usando variables de sesión
    #   `@_sp_name_idx`. Si `arg_out` está definido, se asignan alias en ese orden
    #   a los últimos índices; si no, se intenta aliasar los dos últimos como
    #   `p_exito` y `p_mensaje`.
    # - Se retorna una lista de dicts (filas + OUTs) para no romper consumidores.
    # """
    # resultados: list[dict] = []
    # try:
    #     conn = get_connection(db=DB_NAME)
    #     with conn.cursor() as cur:
    #         # Ejecutar SP
    #         cur.callproc(sp_name, args)

    #         # Intentar obtener filas devueltas por el SP (si hay)
    #         try:
    #             filas = cur.fetchall()
    #             if filas:
    #                 resultados.extend(filas)
    #         except Exception:
    #             # Algunos SP no devuelven result set
    #             pass

    #         # Lectura genérica de OUT params vía variables de sesión
    #         total_params = len(args)
    #         if total_params > 0:
    #             if arg_out and len(arg_out) > 0:
    #                 # Mapear los últimos N índices a los alias proporcionados
    #                 start_idx = max(0, total_params - len(arg_out))
    #                 for offset, nombre in enumerate(arg_out):
    #                     idx = start_idx + offset
    #                     cur.execute(f"SELECT @_" + sp_name + f"_{idx} AS {nombre};")
    #                     out_row = cur.fetchone()
    #                     if out_row is not None:
    #                         resultados.append(out_row)
    #             else:
    #                 # Alias por defecto: últimos dos como p_exito y p_mensaje
    #                 if total_params >= 2:
    #                     # p_exito
    #                     cur.execute(f"SELECT @_" + sp_name + f"_{total_params-2} AS p_exito;")
    #                     exito_row = cur.fetchone()
    #                     if exito_row is not None:
    #                         resultados.append(exito_row)
    #                     # p_mensaje
    #                     cur.execute(f"SELECT @_" + sp_name + f"_{total_params-1} AS p_mensaje;")
    #                     mensaje_row = cur.fetchone()
    #                     if mensaje_row is not None:
    #                         resultados.append(mensaje_row)
    #     if Configuracion.DEBUG:
    #         logger.info(f"Procedimiento almacenado '{sp_name}' ejecutado con éxito. Resultados obtenidos.")
    #     return resultados
    # except Exception as e:
    #     if Configuracion.DEBUG:
    #         logger.error(f"Error al ejecutar el procedimiento almacenado: {e} con SP '{sp_name}' y argumentos {args}.")
    #     print(f"Error al ejecutar el procedimiento almacenado: {e}")
    #     return resultados
    # finally:
    #     if 'conn' in locals():
    #         conn.close()
    """Versión optimizada para mysql-connector-python."""
    resultados: list[dict] = []
    conn = None
    
    try:
        conn = get_connection(db=DB_NAME)
        
        # cursor con dictionary=True para obtener dicts directamente
        with conn.cursor(dictionary=True) as cur:
            # Ejecutar SP - mysql-connector maneja mejor los OUT params
            cur.callproc(sp_name, args)
            
            # 1. Obtener todos los result sets usando stored_results()
            for result_set in cur.stored_results():
                try:
                    rows = result_set.fetchall()
                    if rows:
                        resultados.extend(rows)
                except Exception as e:
                    if Configuracion.DEBUG:
                        logger.debug(f"Fin de result sets: {e}")
                    continue
            
            # 2. Obtener parámetros OUT - mysql-connector los mantiene en cur
            # Podemos consultar variables de sesión o usar los valores en args
            
            total_params = len(args)
            if total_params > 0:
                out_params = {}
                
                # Consultar variables de sesión
                if arg_out and len(arg_out) > 0:
                    for i, nombre in enumerate(arg_out):
                        cur.execute(f"SELECT @_{sp_name}_{i} AS {nombre}")
                        row = cur.fetchone()
                        if row and nombre in row:
                            out_params[nombre] = row[nombre]
                else:
                    # Últimos 2 como p_exito y p_mensaje
                    if total_params >= 2:
                        cur.execute(f"SELECT @_{sp_name}_{total_params-2} AS p_exito")
                        row = cur.fetchone()
                        if row and 'p_exito' in row:
                            out_params['p_exito'] = row['p_exito']
                        
                        cur.execute(f"SELECT @_{sp_name}_{total_params-1} AS p_mensaje")
                        row = cur.fetchone()
                        if row and 'p_mensaje' in row:
                            out_params['p_mensaje'] = row['p_mensaje']
                
                if out_params:
                    resultados.append(out_params)
        
        if Configuracion.DEBUG:
            logger.info(f"SP '{sp_name}' ejecutado. {len(resultados)} resultados.")
        
        return resultados
        
    except Error as e:
        error_msg = f"Error MySQL ejecutando SP '{sp_name}': {e}"
        logger.error(error_msg)
        return [{"error": True, "mensaje": error_msg}]
    
    except Exception as e:
        error_msg = f"Error general ejecutando SP '{sp_name}': {e}"
        logger.error(error_msg)
        return [{"error": True, "mensaje": error_msg}]
    
    finally:
        if conn:
            try:
                conn.close()
            except:
                pass

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

