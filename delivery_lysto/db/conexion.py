
import os
import logging
import json
import mysql.connector
from typing import Optional, Any
from ..configuracion import Configuracion
from mysql.connector import pooling, Error
from mysql.connector.abstracts import MySQLConnectionAbstract

ConnectionType = MySQLConnectionAbstract | pooling.PooledMySQLConnection

logger = logging.getLogger(__name__)

# Variables de entorno con defaults solicitados
DB_HOST = os.getenv("ZOOM_DB_HOST")
DB_PORT = os.getenv("ZOOM_DB_PORT")
DB_NAME = os.getenv("ZOOM_DB_NAME")
DB_USER = os.getenv("ZOOM_DB_USER")
DB_PASSWORD = os.getenv("ZOOM_DB_PASSWORD")


def get_connection(db: Optional[str] = None) -> ConnectionType:
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

        logger.info(
            "[DB][CONNECT][REQUEST] host=%s port=%s db=%s user=%s",
            DB_HOST,
            DB_PORT,
            db,
            DB_USER,
        )
        
        conn = mysql.connector.connect(**config)
        logger.info(
            "[DB][CONNECT][SUCCESS] host=%s port=%s db=%s user=%s",
            DB_HOST,
            DB_PORT,
            db,
            DB_USER,
        )
        return conn 
        
    except Error as e:
        logger.error(
            "[DB][CONNECT][ERROR] host=%s port=%s db=%s user=%s error=%s",
            DB_HOST,
            DB_PORT,
            db,
            DB_USER,
            str(e),
        )
        raise
def probar_conexion() -> bool:
    """Prueba la conexión a la base de datos y registra el estado."""
    conn = None  # Inicializar como None
    
    try:
        conn = get_connection(db=DB_NAME)
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            result = cur.fetchone()
        
        logger.info(
            "[DB][HEALTH][SUCCESS] host=%s port=%s db=%s user=%s test_query=%s",
            DB_HOST,
            DB_PORT,
            DB_NAME,
            DB_USER,
            result,
        )
        
        if Configuracion.DEBUG:
            logger.info(f"Conexión exitosa a '{DB_NAME}' en {DB_HOST}:{DB_PORT}")
        
        return True
        
    except Exception as e:        
        logger.error(
            "[DB][HEALTH][ERROR] host=%s port=%s db=%s user=%s error=%s",
            DB_HOST,
            DB_PORT,
            DB_NAME,
            DB_USER,
            str(e),
        )
        
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
    conn: Optional[ConnectionType] = None
    try:
        logger.info(
            "[DB][SP_BOOL][REQUEST] sp=%s args=%s",
            sp_name,
            json.dumps(args, ensure_ascii=False, default=str),
        )
        conn = get_connection(db=DB_NAME)
        with conn.cursor() as cur:
            cur.callproc(sp_name, args)
        logger.info("[DB][SP_BOOL][SUCCESS] sp=%s", sp_name)
        if Configuracion.DEBUG:
            logger.info(f"Procedimiento almacenado '{sp_name}' ejecutado con éxito.")
        return True
    except Exception as e:
        logger.error(
            "[DB][SP_BOOL][ERROR] sp=%s args=%s error=%s",
            sp_name,
            json.dumps(args, ensure_ascii=False, default=str),
            str(e),
        )
        return False
    finally:
        if conn is not None:
            conn.close()

def ejecutar_sp_void(sp_name: str, *args) -> None:
    """Ejecuta un procedimiento almacenado sin resultado."""
    conn: Optional[ConnectionType] = None
    try:
        logger.info(
            "[DB][SP_VOID][REQUEST] sp=%s args=%s",
            sp_name,
            json.dumps(args, ensure_ascii=False, default=str),
        )
        conn = get_connection(db=DB_NAME)
        with conn.cursor() as cur:
            cur.callproc(sp_name, args)
        logger.info("[DB][SP_VOID][SUCCESS] sp=%s", sp_name)
        if Configuracion.DEBUG:
            logger.info(f"Procedimiento almacenado '{sp_name}' ejecutado con éxito.")
    except Exception as e:
        logger.error(
            "[DB][SP_VOID][ERROR] sp=%s args=%s error=%s",
            sp_name,
            json.dumps(args, ensure_ascii=False, default=str),
            str(e),
        )
    finally:
        if conn is not None:
            conn.close()

def ejecutar_sp_resultados(sp_name: str, *args, arg_out: Optional[list[str]] = None) -> list[dict[str, Any]]:
    """Versión optimizada para mysql-connector-python."""
    resultados: list[dict[str, Any]] = []
    conn: Optional[ConnectionType] = None
    
    try:
        logger.info(
            "[DB][SP_RESULTS][REQUEST] sp=%s args=%s arg_out=%s",
            sp_name,
            json.dumps(args, ensure_ascii=False, default=str),
            json.dumps(arg_out, ensure_ascii=False, default=str),
        )
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
                        for row in rows:
                            if isinstance(row, dict):
                                resultados.append(row)
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
                    start_idx = max(0, total_params - len(arg_out))
                    for offset, nombre in enumerate(arg_out):
                        idx = start_idx + offset
                        cur.execute(f"SELECT @_{sp_name}_{idx} AS {nombre}")
                        row = cur.fetchone()
                        if isinstance(row, dict) and nombre in row:
                            out_params[nombre] = row[nombre]
                else:
                    # Últimos 2 como p_exito y p_mensaje
                    if total_params >= 2:
                        cur.execute(f"SELECT @_{sp_name}_{total_params-2} AS p_exito")
                        row = cur.fetchone()
                        if isinstance(row, dict) and 'p_exito' in row:
                            out_params['p_exito'] = row['p_exito']
                        
                        cur.execute(f"SELECT @_{sp_name}_{total_params-1} AS p_mensaje")
                        row = cur.fetchone()
                        if isinstance(row, dict) and 'p_mensaje' in row:
                            out_params['p_mensaje'] = row['p_mensaje']
                
                if out_params:
                    resultados.append(out_params)
                    logger.info(
                        "[DB][SP_RESULTS][OUT_PARAMS] sp=%s out_params=%s",
                        sp_name,
                        json.dumps(out_params, ensure_ascii=False, default=str),
                    )
        
        if Configuracion.DEBUG:
            logger.info(f"SP '{sp_name}' ejecutado. {len(resultados)} resultados.")
        logger.info(
            "[DB][SP_RESULTS][SUCCESS] sp=%s total_resultados=%s",
            sp_name,
            len(resultados),
        )
        
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

def ejecutar_vista(vista_name: str) -> list[dict[str, Any]]:
    """Ejecuta una vista y devuelve los resultados."""
    resultados: list[dict[str, Any]] = []
    conn: Optional[ConnectionType] = None
    try:
        logger.info("[DB][VIEW][REQUEST] vista=%s", vista_name)
        conn = get_connection(db=DB_NAME)
        with conn.cursor(dictionary=True) as cur:
            cur.execute(f"SELECT * FROM {vista_name};")
            rows = cur.fetchall()
            resultados = [row for row in rows if isinstance(row, dict)]
        logger.info(
            "[DB][VIEW][SUCCESS] vista=%s total_filas=%s",
            vista_name,
            len(resultados),
        )
        if Configuracion.DEBUG:
            logger.info(f"Vista '{vista_name}' ejecutada con éxito. Resultados obtenidos.")
        return resultados
    except Exception as e:
        logger.error(
            "[DB][VIEW][ERROR] vista=%s error=%s",
            vista_name,
            str(e),
        )
        return resultados
    finally:
        if conn is not None:
            conn.close()

