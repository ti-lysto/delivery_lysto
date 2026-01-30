"""
Rutas privadas unificadas (clientes y envíos) ZOOM y ARMI
------------------------------------------------------
"""
import json
import logging
import base64, os
from datetime import datetime
from typing import Optional, Dict, Any, List

from flask import Blueprint, request, jsonify, current_app
from ..core.autenticacion import requerir_api_key
from ..servicios.cliente_zoom import ClienteZoom
from ..servicios.cliente_armi import ClienteArmi
from ..configuracion import Configuracion
from ..db.conexion import ejecutar_sp_resultados


bp_privadas = Blueprint("privadas", __name__)
bp_callbacks = Blueprint("callbacks", __name__)
logger = logging.getLogger(__name__)
debug = Configuracion.DEBUG
catalogo_dict = {
    0: {"ID": 0, "NAME": "RECIBIDA", "DESCRIPTION": "ORDEN PARA LA LOGICA DE LAS COLAS DE ORACLE"},
    1: {"ID": 1, "NAME": "EMITIDA", "DESCRIPTION": "PEDIDO EMITIDO EN EL SISTEMA"},
    2: {"ID": 2, "NAME": "ENVIADA", "DESCRIPTION": "PEDIDO ENVIADO AL PROVEEDOR LOGISTICO"},
    3: {"ID": 3, "NAME": "ASIGNADA", "DESCRIPTION": "PEDIDO ES ASIGNADO A UN DOMICILIARIO"},
    4: {"ID": 4, "NAME": "PICKING", "DESCRIPTION": "DOMICILIARIO ESTA PREPARANDO EL PEDIDO"},
    5: {"ID": 5, "NAME": "FACTURADA", "DESCRIPTION": "PEDIDO HA SIDO FACTURADO EN CAJA DE UNA TIENDA"},
    6: {"ID": 6, "NAME": "ENTREGADA", "DESCRIPTION": "PEDIDO ENTREGADO AL CLIENTE"},
    7: {"ID": 7, "NAME": "FINALIZADA", "DESCRIPTION": "PEDIDO FINALIZADO"},
    8: {"ID": 8, "NAME": "OCULTA", "DESCRIPTION": "ESTATUS PARA OCULTAR UNA ORDEN EN EL MONITOR"},
    9: {"ID": 9, "NAME": "PREPROCESADO", "DESCRIPTION": "PEDIDO FUE ENVIADO DESDE EL CALLCENTER DIRECTAMENTE A LOS MENSAJEROS"},
    10: {"ID": 10, "NAME": "MODIFICADA", "DESCRIPTION": "ORDEN MODIFICADA POR EL CLIENTE"},
    11: {"ID": 11, "NAME": "ENVIADA CON ERROR", "DESCRIPTION": "PEDIDO ENVIADO A LOS MENSAJEROS PERO CON ERROR AL ENVIAR A LAS TIENDAS"},
    12: {"ID": 12, "NAME": "PAGADA", "DESCRIPTION": "ORDEN PAGADA POR EL CLIENTE"},
    13: {"ID": 13, "NAME": "EN COLA POR PAGAR", "DESCRIPTION": "ORDEN ENVIADA A LA COLA DE PAGOS PENDIENTES POR PAGAR"},
    14: {"ID": 14, "NAME": "CANCELADA", "DESCRIPTION": "ORDEN CANCELADA"},
    15: {"ID": 15, "NAME": "ASIGNADO ENVIO NACIONAL", "DESCRIPTION": "ORDEN ENVIO NACIONAL"},
    16: {"ID": 16, "NAME": "FINALIZADO ENVIO NACIONAL", "DESCRIPTION": "ORDEN FINALIZADO ENVIO NACIONAL"},
    17: {"ID": 17, "NAME": "PEDIDO TIEMPO EXCEDIDO", "DESCRIPTION": "SE EXCEDIO EL TIEMPO LIMITE ESTABLECIDO EN EL PROCESO DE RUTA OPTIMA"},
    18: {"ID": 18, "NAME": "TOKEN VERIFICADO", "DESCRIPTION": "TOKEN VERIFICADO POR PARTE DEL PICKER"},
    19: {"ID": 19, "NAME": "ENTREGADA TIENDA", "DESCRIPTION": "INDICA QUE LA ORDEN YA SE ENCUENTRA EN LA TIENDA XSTORE"},
    20: {"ID": 20, "NAME": "ACEPTADA TIENDA", "DESCRIPTION": "ORDEN ACEPTADA POR TIENDA XSTORE"},
    21: {"ID": 21, "NAME": "RECHAZADA TIENDA", "DESCRIPTION": "ORDEN RECHAZADA POR TIENDA XSTORE"},
    22: {"ID": 22, "NAME": "RESERVADA TIENDA", "DESCRIPTION": "ORDEN CREADA DESDE TIENDA XSTORE"},
    23: {"ID": 23, "NAME": "REASIGNADA MANUAL", "DESCRIPTION": "ORDEN REASIGNADA POR EL CALL CENTER MANUALMENTE"},
    24: {"ID": 24, "NAME": "PEDIDO ALISTADO", "DESCRIPTION": "PEDIDO ALISTADO EN EL CENDIS"},
    25: {"ID": 25, "NAME": "PEDIDO ENVIADO", "DESCRIPTION": "PEDIDO ENVIADO AL CLIENTE DESDE EL CENDIS"},
    26: {"ID": 26, "NAME": "PENDIENTE DEVOLUCION TIENDA", "DESCRIPTION": "ORDEN QUE SE DEBE ENVIAR NUEVAMENTE A XSTORE PARA REALIZAR LOS AJUSTES NECESARIOS"},
    27: {"ID": 27, "NAME": "SIN PAGAR", "DESCRIPTION": "PEDIDO NACIONAL O MARKETPLACE CREADO PENDIENTE DE PAGO EFECTIVO O DATAFONO"},
    28: {"ID": 28, "NAME": "PEDIDO INCOMPLETO", "DESCRIPTION": "PEDIDO QUE NO SE HA PODIDO COMPLETAR POR FALTA DE ARTICULOS"},
    29: {"ID": 29, "NAME": "ENVIAR INCOMPLETO", "DESCRIPTION": "PEDIDO ENVIADO SIN COMPLETAR POR FALTA DE ARTICULOS"},
    30: {"ID": 30, "NAME": "CLIENTE ESPERA", "DESCRIPTION": "PREVIO ACUERDO CON EL CLIENTE A QUE SE COMPLETEN EL PEDIDO CON LOS ARTICULOS FALTANTES"},
    31: {"ID": 31, "NAME": "PAGO_PENDIENTE", "DESCRIPTION": "ORDEN QUE NO PUDO SER COBRADA AL MOMENTO DE LA CREACIÓN"},
    32: {"ID": 32, "NAME": "EN CAMINO", "DESCRIPTION": "ORDEN EN CAMINO A DOMICILIO"},
    33: {"ID": 33, "NAME": "EN PUNTO DE ENTREGA", "DESCRIPTION": "MENSAJERO EN DOMICILIO PARA ENTREGA"},
    34: {"ID": 34, "NAME": "RECOGIENDO EN PUNTOS DE TRANSFERENCIA", "DESCRIPTION": "MENSAJERO ESTA RECOGIENDO EN TIENDAS DE TRANSFERENCIA"},
    35: {"ID": 35, "NAME": "PICKING TRANSFERENCIA", "DESCRIPTION": "DOMICILIARIO RECOGIENDO PRODUCTOS EN TIENDA DE TRANSFERENCIA"},
    36: {"ID": 36, "NAME": "PICKING EN TRANSFERENCIA TERMINADO", "DESCRIPTION": "MENSAJERO FINALIZA EL PICKING EN TIENDA DE TRANSFERENCIA"},
    37: {"ID": 37, "NAME": "PICKING TERMINADO", "DESCRIPTION": "MENSAJERO FINALIZA EL PICKING EN TIENDA"},
    38: {"ID": 38, "NAME": "ESCANEANDO DATAFONO", "DESCRIPTION": "MENSAJERO ESCANEA CODIGO DE BARRAS DEL DATAFONO"},
    39: {"ID": 39, "NAME": "CAPTURA BOUCHER", "DESCRIPTION": "MENSAJERO CAPTURA FOTO DEL BOUCHER DE PAGO"},
    40: {"ID": 40, "NAME": "COBRANDO EN LINEA", "DESCRIPTION": "MENSAJERO ESTA COBRANDO EN LINEA"},
    41: {"ID": 41, "NAME": "CAMBIO METODO PAGO DATAFONO A EFECTIVO", "DESCRIPTION": "METODO DE PAGO CAMBIADO DE DATAFONO A EFECTIVO"},
    42: {"ID": 42, "NAME": "CAMBIO METODO PAGO EN LINEA A EFECTIVO", "DESCRIPTION": "METODO DE PAGO CAMBIADO DE EN LINEA A EFECTIVO"},
    43: {"ID": 43, "NAME": "CAMBIO METODO PAGO EN LINEA A DATAFONO", "DESCRIPTION": "METODO DE PAGO CAMBIADO DE EN LINEA A DATAFONO"},
    44: {"ID": 44, "NAME": "PAGADO EN LINEA", "DESCRIPTION": "PEDIDO PAGADO EN LINEA"},
    45: {"ID": 45, "NAME": "PAGADO EN EFECTIVO", "DESCRIPTION": "PEDIDO PAGADO EN EFECTIVO"},
    46: {"ID": 46, "NAME": "PAGADO CON DATAFONO", "DESCRIPTION": "PEDIDO PAGADO CON DATAFONO"},
    47: {"ID": 47, "NAME": "VALIDACION EFECTIVO RECIBIDO", "DESCRIPTION": "TOMA DE FOTO DEL DINERO RECIBIDO EN EFECTIVO"},
    48: {"ID": 48, "NAME": "DEVOLUCIÓN", "DESCRIPTION": "ORDEN CANCELADA DESPUÉS DE HABER SIDO FACTURADA"},
    49: {"ID": 49, "NAME": "DEVOLUCIÓN EXITOSA", "DESCRIPTION": "DEVOLUCIÓN DE LOS PRODUCTOS A LA TIENDA"},
}
def _cliente_Zoom() -> ClienteZoom:
    cfg = current_app.config
    return ClienteZoom(
        base_url=cfg["ZOOM_BASE_URL"],
        api_key=cfg.get("ZOOM_API_KEY", ""),
        frase_secreta=cfg.get("ZOOM_FRASE_SECRETA", ""),
        timeout=cfg.get("ZOOM_TIMEOUT", 10.0),
        reintentos=cfg.get("ZOOM_REINTENTOS", 3),
    )
def _cliente_Armi() -> ClienteArmi:
    cfg = current_app.config
    return ClienteArmi(
        base_url=cfg["ARMI_BASE_URL"],
        api_key=cfg.get("ARMI_API_KEY", ""),
        timeout=cfg.get("ZOOM_TIMEOUT", 10.0),
        reintentos=cfg.get("ZOOM_REINTENTOS", 3),
        country=cfg.get("ARMI_COUNTRY")
    )


def _pick(d: dict, *keys, default=None):
    for k in keys:
        if isinstance(d, dict) and k in d and d[k] not in (None, ""):
            return d[k]
    return default


def _to_bool(val, default=False) -> bool:
    if val is None:
        return default
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val != 0
    if isinstance(val, str):
        return val.strip().lower() in ("1", "true", "t", "yes", "y", "si", "sí")
    return default


def _to_int(val, default=None):
    try:
        return int(val)
    except Exception:
        return default


def _to_float(val, default=None):
    try:
        return float(val)
    except Exception:
        return default

# ------ procediminetos ZOOM ----------------
def _guardar_cliente_zoom(payload: dict) -> int:
    """Upsert de cliente local con sp_guarda_cliente_zoom usando la estructura del payload orquestado."""
    
    try:
        # Extraer datos del payload estructurado
        autenticacion = payload.get("autenticacion_zoom", {})
        remitente = payload.get("remitente", {})
        datos_personales = remitente.get("datos_personales", {})
        direccion = remitente.get("direccion", {})
        
        # Determinar tipo de cliente
        # Por defecto CLIENTE_FINAL, si tiene remitente_id podría ser INTEGRADOR
        tipo_cliente = "CLIENTE_FINAL"
        if remitente.get("remitente_id"):
            tipo_cliente = "INTEGRADOR"
        
        # Limpiar y ajustar tipo de documento (CHAR(1) en BD)
        tipo_documento = datos_personales.get("tipo_documento")
        # Si es "V-", tomar solo "V"
        if tipo_documento and len(tipo_documento) > 1:
            tipo_documento = tipo_documento[0]  # Solo primer caracter
        
        # Obtener número de documento (VARCHAR(10) en BD)
        num_documento = datos_personales.get("numero_documento") or ""
        if len(num_documento) > 10:
            num_documento = num_documento[:10]  # Truncar si es muy largo
        
        # Obtener teléfono (VARCHAR(14) en BD)
        telefono = (datos_personales.get("telefono_movil") or datos_personales.get("telefono_fijo") or "")
        if len(telefono) > 14:
            telefono = telefono[:14]
        
        # Obtener email (VARCHAR(50) en BD)
        mail = datos_personales.get("email") or ""
        if len(mail) > 50:
            mail = mail[:50]
        
        # Obtener dirección (VARCHAR(200) en BD)
        direccion_completa = direccion.get("direccion_completa") or ""
        if len(direccion_completa) > 200:
            direccion_completa = direccion_completa[:200]
        
        # Obtener código cliente Zoom
        cod_cliente_zoom = _to_int(autenticacion.get("codigo_cliente"), 407940)
        
        # Preparar argumentos para el stored procedure
        args_cliente = (
            tipo_cliente,              # p_tipo_cliente VARCHAR(20)
            tipo_documento,            # p_tipo_documento CHAR(1)
            num_documento,             # p_num_documento VARCHAR(10)
            telefono,                  # p_telefono VARCHAR(14)
            mail,                      # p_mail VARCHAR(50)
            direccion_completa,        # p_direccion VARCHAR(200)
            cod_cliente_zoom,          # p_cod_cliente_zoom INT
        )
        
        logger.debug(f"Ejecutando sp_guarda_cliente_zoom con args: {args_cliente}")
        
        # Ejecutar stored procedure
        print (f"Args para sp_guarda_cliente_zoom: {args_cliente}")
        res = ejecutar_sp_resultados("sp_guarda_cliente_zoom", *args_cliente)
        #print (f"Respuesta sp_guarda_cliente_zoom: {res}")
        if not res:
            logger.error("No se obtuvo respuesta de sp_guarda_cliente_zoom")
            raise Exception("No se pudo guardar/obtener id_cliente")
        
        # Extraer el ID del cliente de la respuesta
        resultado = res[0]
        
        # Buscar id_cliente en diferentes formatos de clave
        id_cliente = None
        for key in ["id_cliente", "ID_CLIENTE", "Id_Cliente", "ID"]:
            if key in resultado:
                id_cliente = resultado[key]
                break
        
        if not id_cliente:
            logger.error(f"Respuesta inesperada de sp_guarda_cliente_zoom: {resultado}")
            raise Exception("No se pudo obtener id_cliente de la respuesta")
        
        id_cliente_int = int(id_cliente)
        logger.info(f"Cliente guardado/actualizado con ID: {id_cliente_int} - Tipo: {tipo_cliente}")
        
        return id_cliente_int
        
    except Exception as e:
        logger.exception(f"Error en _guardar_cliente_zoom: {str(e)}")
        raise Exception(f"Error guardando cliente en BD: {str(e)}")


def _persistir_envio_zoom(payload: dict, extras: dict, id_cliente_db: int):
    """Persiste el envío con el payload original y extras mínimos (guia/token/certificado/etiqueta), usando el id_cliente real de BD."""
    
    try:
        # Extraer datos del payload (sin depender de mutaciones)
        
        # Datos básicos
        metadata = payload.get("metadata", {})
        autenticacion = payload.get("autenticacion_zoom", {})
        configuracion = payload.get("configuracion_envio", {})
        servicio = payload.get("servicio", {})
        ubicacion_origen = payload.get("ubicacion_origen", {})
        ubicacion_destino = payload.get("ubicacion_destino", {})
        remitente = payload.get("remitente", {})
        destinatario = payload.get("destinatario", {})
        paquete = payload.get("paquete", {})
        
        # Usar guía proveniente de extras
        id_guia_zoom = extras.get("guia_zoom")
        
        # Obtener datos del destinatario guardado
        destinatario_guardado = {}
        remitente_id = None
        
        # Preparar argumentos para el stored procedure
        args = (
            # Cliente y empresa (asumimos valores por defecto si no están)
            _to_int(id_cliente_db),  # p_id_cliente (ID real en tb_delivery_cliente)
            _to_int(3),  # p_id_empresa_envio (ZOOM=3 por defecto)
            
            # Referencias
            metadata.get("solicitud_id"),  # p_referencia_interna
            extras.get("token"),  # p_token_zoom
            extras.get("certificado"),  # p_certificado_zoom
            _to_int(autenticacion.get("codigo_cliente")),  # p_codigo_cliente_zoom
            
            # Remitente
            remitente.get("datos_personales", {}).get("nombre_completo"),
            remitente.get("direccion", {}).get("direccion_completa"),
            _to_int(ubicacion_origen.get("ciudad", {}).get("codciudad"), 0),
            remitente.get("datos_personales", {}).get("contacto",
                remitente.get("datos_personales", {}).get("nombre_completo")),
            remitente.get("datos_personales", {}).get("telefono_movil",
                remitente.get("datos_personales", {}).get("telefono_fijo")),
            
            # Destinatario
            destinatario.get("datos_personales", {}).get("nombre_completo"),
            destinatario.get("direccion", {}).get("direccion_completa"),
            _to_int(ubicacion_destino.get("ciudad", {}).get("codciudad"), 0),
            destinatario.get("datos_personales", {}).get("contacto",
                destinatario.get("datos_personales", {}).get("nombre_completo")),
            destinatario.get("datos_personales", {}).get("telefono_movil",
                destinatario.get("datos_personales", {}).get("telefono_fijo")),
            
            # Entrega
            _to_bool(destinatario.get("configuracion", {}).get("retira_oficina")),
            _to_int(ubicacion_destino.get("oficina", {}).get("codoficina")),
            
            # Servicio
            _to_int(servicio.get("codservicio")),
            _to_int(servicio.get("tipo_tarifa")),
            _to_int(servicio.get("modalidad_tarifa")),
            _to_int(servicio.get("modalidad_cod")),
            
            # Paquete
            _to_int(paquete.get("numero_piezas")),
            _to_float(paquete.get("peso_total"), 0.0),
            _to_float(paquete.get("dimensiones", {}).get("alto")),
            _to_float(paquete.get("dimensiones", {}).get("ancho")),
            _to_float(paquete.get("dimensiones", {}).get("largo")),
            paquete.get("tipo_paquete"),
            _to_float(paquete.get("valores", {}).get("valor_mercancia"), 0.0),
            _to_float(paquete.get("valores", {}).get("valor_declarado"), 0.0),
            _to_bool(servicio.get("seguro")),
            paquete.get("descripcion", ""),
            
            # Sistema
            1,  # p_cod_estatus_envio (CREADO por defecto)
            payload.get("informacion_adicional", {}).get("observaciones"),
            metadata.get("solicitud_id"),  # p_referencia_zoom
            str(id_guia_zoom or ""),  # p_id_guia_zoom
            
            # Backups (payload completo)
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")),  # p_payload_cab
            
            # Out params
            None,  # p_exito (OUT)
            None   # p_mensaje (OUT)
        )
        
        # Ejecutar stored procedure
        #print (f"Args para sp_crear_envio_zoom: {args}")
        resultados = ejecutar_sp_resultados("sp_crear_envio_zoom", *args, arg_out=["p_exito", "p_mensaje"])        
        #print (f"Respuesta sp_crear_envio_zoom: {resultados}")
        
        # Si el stored procedure devuelve los out params, procesarlos
        if resultados and len(resultados) > 0:
            resultado_dict = resultados[0]
            p_exito = resultado_dict.get("p_exito", resultado_dict.get("P_EXITO"))
            p_mensaje = resultado_dict.get("p_mensaje", resultado_dict.get("P_MENSAJE"))
            if debug: logger.info(f"Sp ejecutado OK en BD con resultado: {resultados}")
            return {
                "p_exito": p_exito if p_exito is not None else True,
                "p_mensaje": p_mensaje or "Envío guardado exitosamente",
                "resultado": resultados,
                #"id_envio_cab": resultado_dict.get("id_envio_cab", resultado_dict.get("ID_ENVIO_CAB")),
                "id_guia_zoom": id_guia_zoom
            }            
        else:
            logger.error("No se obtuvo respuesta del procedimiento almacenado sp_crear_envio_zoom")
            return {
                "p_exito": False,
                "p_mensaje": "Error: No se obtuvo respuesta del procedimiento almacenado",
                "resultado": [],
                "id_guia_zoom": id_guia_zoom
            }
            
    except Exception as e:
        logger.exception(f"Error en _persistir_envio_zoom: {str(e)}")
        return {
            "p_exito": False,
            "p_mensaje": f"Error guardando envío en BD: {str(e)}",
            "error": str(e)
        }

def reimprimir_guia(_cliente: ClienteZoom, guia: str) -> dict:
    """Reimprime usando la etiqueta ya guardada en BD (sin solicitar nueva)."""
    try:
        if not guia:
            logger.error("No se proporcionó número de guía para reimpresión")
            return {"error": "No se proporcionó número de guía"}
        
        # Ejecutar SP de búsqueda por guía
        resultados = ejecutar_sp_resultados("sp_busqueda_zoom", guia, None, None)
        #print(f"Resultados sp_busqueda_zoom para guía {guia}: {resultados}")
        
        if not resultados:
            return {"error": "No se encontró la guía en BD"}

        # Tomar el primer resultado (debería ser solo uno)
        fila = resultados[0]
        
        # Buscar etiqueta en payload_solicitud -> datos_devueltos -> etiqueta_pdf
        etiqueta_pdf = None
        
        # 1. Buscar directamente en payload_solicitud
        payload_solicitud = fila.get('payload_solicitud')
        if payload_solicitud:
            try:
                # Convertir string JSON a dict si es necesario
                if isinstance(payload_solicitud, str):
                    payload_data = json.loads(payload_solicitud)
                else:
                    payload_data = payload_solicitud
                
                # Buscar en datos_devueltos -> etiqueta_pdf
                datos_devueltos = payload_data.get('datos_devueltos', {})
                if isinstance(datos_devueltos, str):
                    try:
                        datos_devueltos = json.loads(datos_devueltos)
                    except:
                        datos_devueltos = {}
                
                etiqueta_pdf = datos_devueltos.get('etiqueta_pdf')
                
            except Exception as e:
                logger.error(f"Error procesando payload_solicitud: {str(e)}")
                
        if not etiqueta_pdf:
            logger.error("No se encontró etiqueta en ningún campo")
            return {"error": "La guía existe pero no tiene etiqueta almacenada"}
        
        # Verificar que la etiqueta sea base64 válido
        if not etiqueta_pdf or len(etiqueta_pdf.strip()) < 100:
            logger.error(f"Etiqueta encontrada pero parece inválida (longitud: {len(etiqueta_pdf) if etiqueta_pdf else 0})")
            return {"error": "Etiqueta almacenada en formato inválido"}
        
        # Generar el PDF
        respuesta = crear_pdf_etiqueta_zoom(_cliente, etiqueta_pdf, guia)
        if respuesta.get("error"):
            logger.error(f"Error generando PDF: {respuesta.get('error')}")
            return {"error": respuesta.get("error")}
        
        return {
            "ok": True,
            "guia": guia,
            "etiqueta_pdf_encontrada": True,
            "fuente": "bd",
            "ruta_pdf": respuesta.get("ruta")
        }
        
    except Exception as e:
        logger.exception(f"Error en reimprimir_guia: {str(e)}")
        return {"error": str(e)}

# --------- Procedimientos ARMI ----------------
# ===== FUNCIONES DE TRANSFORMACIÓN INSTALEAP-ARMI =====
def transformar_payload_instaleap_a_armi(payload_instaleap: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforma el payload de Instaleap al formato requerido por ARMI para crear órdenes.
    """
    try:
        logger.info(f"Transformando payload Instaleap a ARMI. Task ID: {payload_instaleap.get('task_id')}")
        
        # Extraer datos básicos
        task_id = payload_instaleap.get("task_id", "")
        job_number = payload_instaleap.get("job_number", "")
        client_id = payload_instaleap.get("client_id", "")
        print ("cliente_id:", client_id)
        
        # Información de pago
        payment_info = payload_instaleap.get("payment_info", {})
        prices = payment_info.get("prices", {})
        
        # Información de destino/cliente
        destination = payload_instaleap.get("destination", {})
        recipient = payload_instaleap.get("recipient", {})
        
        # Productos
        job_items = payload_instaleap.get("job_items", [])
        #calcular peso de los items instaleap
        peso_total = 0.0
        for item in job_items:
            peso = float(item.get("weight", 0))
            cantidad = float(item.get("quantity", 1))
            peso_total += peso * cantidad        
        peso_total = round(peso_total, 2) if peso_total > 0 else len(job_items) * 0.5
        
        #obtener nombre y apellido
        nombre_completo = recipient.get("name", "")
        if not nombre_completo:
            nombre = "Cliente"
            apellido= "Instaleap"
        else:    
            partes = nombre_completo.strip().split()
            nombre = partes[0] if partes else "Cliente"
            apellido = partes[-1] if len(partes) > 1 else "Instaleap"
        
        import re
        numeros = re.findall(r'\d+', nombre_completo)
        dni= numeros[0] if numeros else ""
        

        # Determinar el método de pago
        match payment_info.get("payment", {}).get("method", "PREPAID"):
            case "CASH":
                metodo_pago = 1
            case "CARD" | "TERMINAL" | "DATAFONO":
                metodo_pago = 2
            case "PREPAID"|"ONLINE" | "DIGITAL":
                metodo_pago = 3
            case _:
                metodo_pago = 1


        # Construir payload ARMI
        payload_armi = {
            "business_id": client_id, #None,  # Se determinará luego mediante mapeo
            "total_value": float(prices.get("order_value", 0)) / 100,  # Convertir centavos
            "user_tip": 0.0,
            "incentive_value": 0.0,
            "delivery_value": float(prices.get("shipping_fee", 0)) / 100,
            "vehicle_type": 2,  # Moto por defecto
            #"payment_method": _determinar_metodo_pago_instaleap(payment_info.get("payment", {}).get("method", "PREPAID")),
            "payment_method": metodo_pago,
            #"weight": _calcular_peso_total_instaleap(job_items),
            "weight": peso_total,
            "city": _normalizar_nombre_ciudad(destination.get("city", "")),
            "instructions": payload_instaleap.get("job_comment", "") or "",
            "orderInvoice": job_number,
            "products": _transformar_productos_instaleap(job_items),
            "client_info": {
                # "first_name": _extraer_nombre(recipient.get("name", "")),
                # "last_name": _extraer_apellido(recipient.get("name", "")),
                "first_name": nombre,
                "last_name": apellido,
                "phone": recipient.get("phone_number", ""),
                "email": recipient.get("email", ""),
                "address": destination.get("address", ""),
                "lat": destination.get("latitude", 0.0),
                "lng": destination.get("longitude", 0.0),
                "dni": dni
                #"dni": _extraer_dni_de_nombre(recipient.get("name", ""))
            },
            "country": _normalizar_codigo_pais_instaleap(destination.get("country", "")),
            "token": task_id
            # "metadata": {
            #     "task_id": task_id,
            #     "job_number": job_number,
            #     "created_at": payload_instaleap.get("created_at", "")
            # }
        }
        
        logger.info(f"Payload ARMI transformado exitosamente")
        return payload_armi
        
    except Exception as e:
        logger.exception(f"Error transformando payload Instaleap a ARMI: {str(e)}")
        raise


# def _determinar_metodo_pago_instaleap(metodo_instaleap: str) -> int:
#     """Convierte método de pago de Instaleap a código ARMI."""
#     metodo = (metodo_instaleap or "").upper()
    
#     if metodo == "CASH":
#         return 1  # efectivo
#     elif metodo in ["CARD", "TERMINAL", "DATAFONO"]:
#         return 2  # Datafono
#     elif metodo in ["PREPAID", "ONLINE", "DIGITAL"]:
#         return 3  # en línea
#     else:
#         logger.warning(f"Método de pago no reconocido: {metodo}. Usando efectivo por defecto.")
#         return 1


# def _calcular_peso_total_instaleap(job_items: List[Dict]) -> float:
#     """Calcula el peso total de los items de Instaleap."""
#     if not job_items:
#         return 1.0  # Peso por defecto
    
#     peso_total = 0.0
#     for item in job_items:
#         peso = float(item.get("weight", 0))
#         cantidad = float(item.get("quantity", 1))
#         peso_total += peso * cantidad
    
#     return round(peso_total, 2) if peso_total > 0 else len(job_items) * 0.5


def _transformar_productos_instaleap(job_items: List[Dict]) -> List[Dict]:
    """Transforma productos de Instaleap a formato ARMI."""
    productos = []
    
    for idx, item in enumerate(job_items):
        producto = {
            "product_id": item.get("id") or f"INSTALEAP_{idx + 1}",
            "name": item.get("name", f"Producto {idx + 1}"),
            "description": item.get("comment", "") or item.get("name", ""),
            "quantity": int(item.get("quantity", 1)),
            "image_url": item.get("image_url", ""),
            "unit_price": float(item.get("price", 0)) / 100,  # Convertir centavos
            "store_id": None  # Se llenará después con el mapeo
        }
        productos.append(producto)
    
    return productos


def _normalizar_nombre_ciudad(ciudad: str) -> str:
    """Normaliza nombre de ciudad para ARMI."""
    if not ciudad:
        return ""    
    # Convertir a minúsculas y simplificar
    ciudad = ciudad.lower().strip()    
    # Reemplazar caracteres especiales
    import unicodedata
    ciudad = ''.join(
        c for c in unicodedata.normalize('NFD', ciudad)
        if unicodedata.category(c) != 'Mn'
    )    
    return ciudad


def _normalizar_codigo_pais_instaleap(pais: str) -> str:
    """Normaliza código de país para ARMI."""
    if not pais:
        return "VEN"    
    pais = pais.upper()    
    # Mapeo simple
    mapeo = {
        "COLOMBIA": "COL",
        "COL": "COL",
        "VEN": "VEN",
        "VENZUELA": "VEN"
    }    
    # Buscar coincidencia exacta o parcial
    for key, value in mapeo.items():
        if key in pais or pais in key:
            return value    
    # Si no encuentra, usar primeras 3 letras
    return pais[:3] if len(pais) >= 3 else "VEN"


# def _extraer_nombre(nombre_completo: str) -> str:
#     """Extrae primer nombre."""
#     if not nombre_completo:
#         return "Cliente"
    
#     partes = nombre_completo.strip().split()
#     return partes[0] if partes else "Cliente"


# def _extraer_apellido(nombre_completo: str) -> str:
#     """Extrae apellido."""
#     if not nombre_completo:
#         return "Instaleap"
    
#     partes = nombre_completo.strip().split()
#     return partes[-1] if len(partes) > 1 else "Instaleap"


# def _extraer_dni_de_nombre(nombre_completo: str) -> str:
#     """Intenta extraer DNI del nombre."""
#     if not nombre_completo:
#         return ""
    
#     import re
#     numeros = re.findall(r'\d+', nombre_completo)
#     return numeros[0] if numeros else ""


# def buscar_mapa_tienda_instaleap(store_ref: str, client_id: str) -> tuple:
#     """
#     Busca mapeo entre store_ref de Instaleap y IDs de ARMI.
#     IMPORTANTE: Debes implementar esta función según tu base de datos.
#     """
#     try:
#         # EJEMPLO - Debes adaptar esto a tu BD real
        
#         # Opción 1: Buscar en tabla de mapeo
#         resultados = ejecutar_sp_resultados(
#             "sp_buscar_mapa_tienda_instaleap",
#             store_ref,
#             client_id
#         )
        
#         # Opción 2: Si no tienes SP, buscar directamente
#         # from ..db.conexion import get_db_connection
#         # with get_db_connection() as conn:
#         #     cursor = conn.cursor()
#         #     cursor.execute("""
#         #         SELECT business_id, branch_office_id 
#         #         FROM third_party_store_mapping 
#         #         WHERE external_store_ref = %s AND client_id = %s
#         #     """, (store_ref, client_id))
#         #     row = cursor.fetchone()
#         #     if row:
#         #         return (row[0], row[1])
        
#         if resultados and len(resultados) > 0:
#             fila = resultados[0]
#             return (
#                 fila.get("business_id") or fila.get("BUSINESS_ID"),
#                 fila.get("branch_office_id") or fila.get("BRANCH_OFFICE_ID")
#             )
        
#         logger.warning(f"No se encontró mapeo para store_ref: {store_ref}, client_id: {client_id}")
#         return (None, None)
        
#     except Exception as e:
#         logger.error(f"Error buscando mapeo de tienda: {str(e)}")
#         return (None, None)


# def guardar_relacion_instaleap_armi(**kwargs):
#     """
#     Guarda relación entre orden de Instaleap y ARMI.
#     """
#     try:
#         # EJEMPLO - Debes adaptar esto a tu BD real
#         args = (
#             kwargs.get("task_id"),
#             kwargs.get("job_number"),
#             kwargs.get("client_id"),
#             kwargs.get("order_id_armi"),
#             kwargs.get("business_id"),
#             kwargs.get("branch_office_id"),
#             json.dumps(kwargs.get("payload_original"), ensure_ascii=False),
#             json.dumps(kwargs.get("payload_armi"), ensure_ascii=False),
#             datetime.now().isoformat()
#         )
        
#         # Ejecutar SP o insert directo
#         ejecutar_sp_resultados("sp_guardar_relacion_instaleap_armi", *args)
        
#         logger.info(f"Relación guardada: task_id={kwargs.get('task_id')}")
        
#     except Exception as e:
#         logger.error(f"Error guardando relación: {str(e)}")

# guardar instaleap-armi en base de datos
def guardar_envio_instaleap_armi(**kwargs) -> tuple[bool, str]:    
    #Guarda el envío de Instaleap y ARMI en la base de datos.        
    try:        
        json_instaleap = kwargs.get("payload_instaleap")
        json_armi = kwargs.get("payload_armi")
        
        if not json_instaleap or not json_armi:
            return (False, "Los payloads de Instaleap y ARMI son requeridos")
        
        # ============================================
        # 1. PREPARAR PRODUCTOS JSON
        # ============================================
        productos = json_armi.get("products", [])
        if not productos:
            return (False, "La lista de productos no puede estar vacía")
        
        # Preparar productos en formato JSON string
        productos_json_str = json.dumps(productos, ensure_ascii=False)
        
        # ============================================
        # 2. VALIDACIONES Y TRANSFORMACIONES
        # ============================================
        client_info = json_armi.get("client_info", {})
        
        # business_id - debe ser > 0
        business_id = json_armi.get("business_id")        
        if business_id is None or not business_id :
            logger.error(f"No se pudo procesar el ID del negocio: {business_id}")
            return (False, f"No se pudo procesar el ID del negocio: {business_id}")
       
        # vehicle_type - debe ser 1, 2 o 3
        vehicle_type = json_armi.get("vehicle_type", 0)
        if vehicle_type not in [1, 2, 3]:
            vehicle_type = 2  # Valor por defecto: moto
        
        # payment_method - debe ser 1, 2 o 3
        payment_method = json_armi.get("payment_method", 0)
        if payment_method not in [1, 2, 3]:
            payment_method = 1  # Valor por defecto: efectivo
        
        # ============================================
        # 3. PREPARAR ARGUMENTOS PARA EL SP
        # ============================================
        # NOTA: El SP tiene 24 parámetros: 22 IN + 2 OUT
        # El orden es importante:
        # 1-22: Parámetros IN
        # 23-24: Parámetros OUT (estos se llenarán después)

        args = [
            # Parámetros IN (1-22)
            business_id,  # p_business_id BIGINT
            float(json_armi.get("total_value", 0.0)),  # p_total_value DOUBLE
            float(json_armi.get("user_tip", 0.0)),  # p_user_tip DOUBLE
            float(json_armi.get("incentive_value", 0.0)),  # p_incentive_value DOUBLE
            float(json_armi.get("delivery_value", 0.0)),  # p_delivery_value DOUBLE
            vehicle_type,  # p_vehicle_type INT
            payment_method,  # p_payment_method INT
            float(json_armi.get("weight", 0.0)),  # p_weight DOUBLE
            str(json_armi.get("city", "")),  # p_city VARCHAR(100)
            str(json_armi.get("instructions", "")),  # p_instructions TEXT
            str(json_armi.get("orderInvoice", "")),  # p_orderInvoice VARCHAR(100)
            str(json_armi.get("token", "")),  # p_token VARCHAR(255)
            str(client_info.get("first_name", "")),  # p_first_name VARCHAR(100)
            str(client_info.get("last_name", "")),  # p_last_name VARCHAR(100)
            str(client_info.get("phone", "")),  # p_phone VARCHAR(50)
            str(client_info.get("email", "")),  # p_email VARCHAR(150)
            str(client_info.get("address", "")),  # p_address TEXT
            float(client_info.get("lat", 0.0)),  # p_lat DOUBLE
            float(client_info.get("lng", 0.0)),  # p_lng DOUBLE
            str(client_info.get("dni", "")),  # p_dni VARCHAR(50)
            str(kwargs.get("nota_interna", "")),  # p_nota_interna TEXT
            json.dumps(json_instaleap, ensure_ascii=False),  # p_instaleap_payload JSON
            json.dumps(json_armi, ensure_ascii=False),  # p_armi_payload JSON
            productos_json_str,  # p_productos_json JSON (¡NUEVO PARÁMETRO!)
            
            # Parámetros OUT (estos se llenarán)
            0,    # p_exito BOOLEAN (OUT) - valor inicial
            ''    # p_mensaje VARCHAR(500) (OUT) - valor inicial
        ]        
        # ============================================
        # 4. EJECUTAR PROCEDIMIENTO ALMACENADO
        # ============================================
        # NOTA: Asegúrate de que ejecutar_sp_resultados maneje correctamente
        # los parámetros OUT. Debe retornar una tupla o diccionario con los resultados.
        print (f"Args para sp_guardar_envio_ARMI: {args}")
        respuesta_bd = ejecutar_sp_resultados(
            "sp_guardar_envio_ARMI",  # Nombre correcto del SP
            *args
        )
        
        print(f"Respuesta sp_guardar_envio_ARMI: {respuesta_bd}")
        
        # ============================================
        # 5. PROCESAR RESULTADOS
        # ============================================
        # Dependiendo de cómo implementes ejecutar_sp_resultados,
        # aquí hay algunas opciones:
        
        # Opción A: Si ejecutar_sp_resultados retorna los valores OUT directamente
        if isinstance(respuesta_bd, tuple) and len(respuesta_bd) >= 2:
            p_exito, p_mensaje = respuesta_bd[0], respuesta_bd[1]
            exito = bool(p_exito)
            mensaje = str(p_mensaje)
        
        # Opción B: Si los valores OUT están en args después de ejecutar
        elif len(args) >= 24:
            # Los últimos 2 elementos de args fueron actualizados
            exito = bool(args[-2])
            mensaje = str(args[-1])
        
        # Opción C: Si ejecutar_sp_resultados retorna un diccionario
        elif isinstance(respuesta_bd, dict):
            exito = respuesta_bd.get('exito', False)
            mensaje = respuesta_bd.get('mensaje', '')
        
        else:
            # No se pudo determinar el resultado
            logger.error(f"No se pudo procesar respuesta del SP: {respuesta_bd}")
            return (False, "Error procesando respuesta de la base de datos")
        
        if exito:
            logger.info(f"Envío guardado exitosamente: task_id={kwargs.get('task_id')}, mensaje={mensaje}")
            return (True, mensaje)
        else:
            logger.error(f"Error guardando envío: {mensaje}")
            return (False, mensaje)
            
    except Exception as e:
        error_msg = f"Error guardando envío: {str(e)}"
        logger.error(error_msg)
        return (False, error_msg)


# --- Clientes ---
@bp_privadas.post("/informeCliente")
@requerir_api_key(Delivery_Empresa="ZOOM")
def crear_informecliente():
    payload = request.get_json(silent=True) or {}
    cliente = _cliente_Zoom()
    data = cliente.informe_cliente(payload)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data}), 201


# --- SOLO ENDPOINTS PRIVADOS DOCUMENTADOS ---
@bp_privadas.post("/zoomCert")
@requerir_api_key(Delivery_Empresa="ZOOM")
def zoom_cert():
    payload = request.get_json(silent=True) or {}
    cliente = _cliente_Zoom()
    data = cliente.zoom_cert(payload)
    return jsonify({"ok": True, "data": data})

@bp_privadas.post("/serviciosClientes")
@requerir_api_key(Delivery_Empresa="ZOOM")
def servicios_clientes():
    payload = request.get_json(silent=True) or {}
    cliente = _cliente_Zoom()
    data = cliente.servicios_clientes(payload)
    return jsonify({"ok": True, "data": data})

@bp_privadas.post("/createShipment")
@requerir_api_key(Delivery_Empresa="ZOOM")
def create_shipment():
    payload = request.get_json(silent=True) or {}
    cliente = _cliente_Zoom()
    data = cliente.create_shipment(payload)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    

    # try:
    #     resultado_db = _persistir_envio_zoom(payload, data)
    # except Exception as exc:
    #     logger.exception("Error guardando createShipment en BD")
    #     return jsonify({
    #         "ok": False,
    #         "error": "Error al guardar en base de datos",
    #         "detalle": str(exc),
    #         "data_zoom": data,
    #     }), 500
    # return jsonify({"ok": True, "data": data, "db": resultado_db}), 201
    
    return jsonify({"ok": True, "data": data}), 201
#--------------------------------------------------------endpoint orquestador propio-----------------------------------------------
@bp_privadas.post("/delivery/zoom/envio")
@requerir_api_key(Delivery_Empresa="ZOOM")
def crear_envio_zoom_orquestado():    
    payload = request.get_json(silent=True) or {}
    if not payload:
        logger.error("No se recibió payload en el envío orquestado")
        return jsonify({"ok": False, "error": "No se recibió payload"}), 400
    elif debug: logger.info(f"Creando envío orquestado: {payload.get('metadata', {}).get('solicitud_id', 'N/A')}")
    
    # Resultado acumulado de todo el proceso
    resultado = {
        "metadata": payload.get("metadata", {}),
        "pasos_completados": [],
        "errores": [],
        "datos_intermedios": {},
        "respuesta_final": {}
    }
    
    cliente_zoom = _cliente_Zoom()
    
    try:
        resultado["ok"] = True
            #===== PASO 1: VALIDACIÓN INICIAL =====
        validaciones_ok, error = validar_payload_estructura(payload)        
        if not validaciones_ok:
            logger.error(f"Validación de estructura fallida: {error}")
            resultado["errores"].append(f"Error en la estructura: {error}")
            resultado["ok"] = False
            #return jsonify({"ok": False, "error": error}), 400
        elif debug: logger.info(f"Validación de estructura exitosa: {validaciones_ok}, error: {error}")
        
        resultado["pasos_completados"].append("validacion_estructura")
        
        # ===== PASO 2: OBTENER TOKEN Y CERTIFICADO =====
        token_data = obtener_autenticacion_zoom(cliente_zoom, payload)
        if "error" in token_data:
            logger.error(f"Error obteniendo token: {token_data['error']}")
            resultado["errores"].append(f"Error al obtener token: {token_data['error']}")
            resultado["ok"] = False
            #return jsonify({"ok": False, "error": token_data["error"]}), 401
        elif debug: logger.info("Token y certificado obtenidos correctamente")
        
        # Guardar token/certificado solo en variables locales (no mutar payload)
        token = token_data.get("token")
        certificado = token_data.get("certificado")
        
        resultado["datos_intermedios"]["autenticacion"] = {
            "token_obtenido": bool(token),
            "certificado_obtenido": bool(certificado)
        }
        resultado["pasos_completados"].append("autenticacion")
        
        # # ===== PASO 3: VALIDAR SERVICIOS DEL CLIENTE =====
        # # Solo si el cliente quiere validar sus servicios disponibles
        if payload.get("configuracion_envio", {}).get("validar_servicios", True):
            try:
                servicios = cliente_zoom.servicios_clientes({
                    "login": payload["autenticacion_zoom"]["login"]
                })                
                # Verificar que el servicio solicitado esté disponible
                codservicio = payload["servicio"]["codservicio"]
                servicios_disponibles = [s["codserviciofin"] for s in servicios.get("entidadRespuesta", [])]   
                if codservicio not in servicios_disponibles:
                    logger.warning(f"Servicio {codservicio} no disponible para cliente")
                    resultado["errores"].append("Servicio no disponible para el cliente")
                    resultado["datos_intermedios"]["servicios_validados"] = False
                    resultado["ok"] = False
                    #raise ValueError(f"Servicio {codservicio} no disponible para cliente")
                else: 
                    resultado["datos_intermedios"]["servicios_validados"] = True                    
                    if debug: logger.info(f"Servicio {codservicio} valido para el cliente")
                
            except Exception as e:
                logger.error(f"Error validando servicios del cliente: {str(e)}")
                resultado["ok"] = False
                resultado["errores"].append(f"Error validando servicios del cliente: {str(e)}")                
                # Continuamos aunque falle la validación de servicios
        
        resultado["pasos_completados"].append("validacion_servicios")
        
        # # ===== PASO 4: CALCULAR TARIFA =====
        tarifa_calculada = calcular_tarifa_envio(cliente_zoom, payload)
        if "error" in tarifa_calculada:
            resultado["ok"] = False
            if payload.get("configuracion_envio", {}).get("requerir_tarifa_valida", True):
                logger.error(f"Error calculando tarifa: {tarifa_calculada['error']}")
                resultado["errores"].append(f"Error al calcular tarifa: {tarifa_calculada['error']}")
        else:
            if debug: 
                logger.info("Tarifa calculada correctamente")
                resultado["pasos_completados"].append("calculo_tarifa")


        
        # # # ===== PASO 5: REGISTRAR/ACTUALIZAR REMITENTE =====
        # #if payload.get("remitente", {}).get("configuracion", {}).get("guardar_remitente", True):
        remitente_id = guardar_remitente_zoom(cliente_zoom, payload)
        
        if remitente_id:
            resultado["datos_intermedios"]["remitente_id"] = remitente_id
            resultado["pasos_completados"].append("registro_remitente")
            if debug: logger.info(f"Remitente guardado con ID: {remitente_id}")
        else:
            resultado["errores"].append("No se pudo guardar remitente")
            logger.warning("No se pudo guardar remitente, continuando...")
            resultado["ok"] = False
            
        
        # # # ===== PASO 6: REGISTRAR/ACTUALIZAR DESTINATARIO =====
        # # if payload.get("destinatario", {}).get("configuracion", {}).get("guardar_destinatario", True):
        destinatario = guardar_destinatario_zoom(cliente_zoom, payload)
        if destinatario.get("codrespuesta") == "COD_001":
            # resultado["datos_intermedios"]["destinatario_id"] = destinatario_id
            if debug: logger.info(f"Destinatario guardado con exito: {destinatario}")
            resultado["pasos_completados"].append("registro_destinatario")
        else:
            resultado["errores"].append("No se pudo guardar destinatario")            
            logger.warning("No se pudo guardar destinatario")
            resultado["ok"] = False
        
        # # # ===== PASO 7: CREAR EL ENVÍO =====
        
        tipo_envio = payload["configuracion_envio"]["tipo_envio"]   
        if tipo_envio in ["nacional", "internacional", "casillero_aereo", "casillero_maritimo"]:
            envio_creado = crear_envio_segun_tipo(cliente_zoom, payload, tipo_envio, token, certificado)
            guia_zoom = envio_creado.get("entidadRespuesta", [{}])[0].get("numguia")
            if not guia_zoom and (envio_creado.get("codrespuesta") != "CODE_001"):
                logger.error(f"Error creando envío: {envio_creado.get('error', 'Respuesta inesperada')}")   
                resultado["errores"].append(f"Error creando envío: {envio_creado['error']}")
                resultado["respuesta_final"]["envio"] = "Envío no creado"
                #resultado["respuesta_final"]["guia_zoom"] = "Guía no generada"
                resultado["ok"] = False
            else:
                if debug: logger.info(f"Envío creado con éxito, guía Zoom: {guia_zoom}")
                #guia_zoom = envio_creado.get("entidadRespuesta", {}).get("numguia") 
                resultado["respuesta_final"]["envio"] = "Envío creado exitosamente"                
                #resultado["respuesta_final"]["guia_zoom"] = guia_zoom
                resultado["pasos_completados"].append("creacion_envio")
                #resultado["respuesta_final"]["guia_zoom"] = guia_zoom
            
            
            
            
        
        # # ===== PASO 8: OBTENER SEGUIMIENTO INMEDIATO =====
        # if guia_zoom:
        #     try:
        #         tracking = cliente_zoom.obtener_ultimotrack(
        #             codigo=guia_zoom,
        #             codigo_cliente=payload["autenticacion_zoom"]["codigo_cliente"],
        #             tipo_busqueda=1  # Por número de guía
        #         )
        #         #resultado["respuesta_final"]["tracking"] = tracking
        #         if tracking.get("codrespuesta", []) == "COD_000":
        #             resultado["pasos_completados"].append("Tracking inicial")
        #             if debug: logger.info(f"Seguimiento inicial obtenido para guía {guia_zoom}")
        #         else:
        #             resultado["errores"].append("No se pudo obtener tracking inicial")
        #             resultado["ok"] = False
        #             logger.warning(f"No se pudo obtener seguimiento inicial para guía {guia_zoom}")
        #     except Exception as e:
        #         logger.error(f"Error obteniendo seguimiento inicial: {str(e)}")
        #         resultado["ok"] = False
        
        # # ===== PASO 9: GENERAR ETIQUETA TÉRMICA =====
        if (guia_zoom and 
            payload.get("configuracion_envio", {}).get("generar_etiqueta", True)):
            
            try:
                etiqueta = cliente_zoom.etiqueta_termica({
                    "codguia": [guia_zoom],
                    "termicaPdf": "1",
                    "terminos": "1"
                })

                resultado["respuesta_final"]["etiqueta_envio"] = etiqueta["entidadRespuesta"]["guiaPDF"]
                
                logger.info(f"Etiqueta generada exitosamente para guía {guia_zoom}")                
                resultado["pasos_completados"].append("generacion_etiqueta")

                # guardar de etiqueta en pdf
                crear_pdf_etiqueta_zoom(cliente_zoom, etiqueta=etiqueta["entidadRespuesta"]["guiaPDF"], guia_zoom=guia_zoom)
                

            except Exception as e:
                logger.warning(f"No se pudo generar etiqueta: {str(e)}")
                resultado["errores"].append("generacion_etiqueta_fallida")
                resultado["ok"] = False
        
        # # ===== PASO 10: GUARDAR EN BASE DE DATOS LOCAL =====
        try:
            # Extras mínimos para persistencia y respuesta (sin mutar payload)
            extras = {
                "errores_zoom":resultado["errores"],
                "guia_zoom": guia_zoom,
                "token": token,
                "certificado": certificado,
                "etiqueta_pdf": (etiqueta or {}).get("entidadRespuesta", {}).get("guiaPDF")
            }
            payload["datos_devueltos"] = extras  # Solo para referencia en BD            
            db_cliente = _guardar_cliente_zoom(payload)
            if db_cliente:
                if debug: logger.info(f"Cliente guardado en BD con ID: {db_cliente}")
                db_envio = _persistir_envio_zoom(payload, extras, db_cliente)
                if debug: logger.info(f"Envío guardado en BD con resultado: {db_envio}")
            #db_resultado = guardar_envio_en_bd(payload, resultado)
                resultado["respuesta_final"]["db"] = db_envio
                resultado["pasos_completados"].append("almacenado_bd")
            else:
                logger.error("No se pudo guardar cliente en BD")
                logger.error ("No se pudo guardar envío en BD")
                resultado["errores"].append("persistencia_bd_fallida")
                resultado["ok"] = False
        except Exception as e:
            logger.error(f"Error guardando en BD: {str(e)}")
            resultado["errores"].append("persistencia_bd_fallida")
            # Continuamos aunque falle la BD, el envío ya se creó en Zoom
        
        # ===== RESPUESTA FINAL =====
        
        resultado["timestamp_final"] = datetime.now().isoformat()
        
        return jsonify(resultado), 201
        
    except Exception as e:
        logger.exception("Error crítico en proceso orquestado")
        return jsonify({
            "ok": False,
            "error": f"Error crítico en proceso: {str(e)}",
            "pasos_completados": resultado.get("pasos_completados", []),
            "errores": resultado.get("errores", []),
            "ultimo_paso": resultado.get("pasos_completados", [])[-1] if resultado.get("pasos_completados") else None
        }), 500


# ===== FUNCIONES AUXILIARES =====
def crear_pdf_etiqueta_zoom(cliente: ClienteZoom, etiqueta: dict, guia_zoom: str) -> dict:
    """Genera PDF de una etiqueta térmica existente"""
    try:
        
        if Configuracion.ZOOM_IMPRESION_ETIQUETA:              
            # Decodificar y guardar
            with open("etiqueta.pdf", "wb") as f:
                f.write(base64.b64decode(etiqueta))  
                #pass
            if Configuracion.ZOOM_GUARDA_PDF_ETIQUETA:
                ruta = Configuracion.ZOOM_DIR_ETIQUETAS
                os.makedirs(ruta, exist_ok=True)
                # Nombre del archivo
                nombre_archivo = f"{ruta}/etiqueta_{guia_zoom}.pdf"

                # Guardar el PDF
                with open(nombre_archivo, "wb") as f:
                    f.write(base64.b64decode(etiqueta))
                if debug: logger.info(f"PDF guardado en: {nombre_archivo}")
        logger.info(f"Etiqueta PDF generada para guía {guia_zoom}")
    
        return {"ok": True, "ruta": nombre_archivo}            
    
    except Exception as e:
        logger.error(f"Error generando etiqueta PDF : {str(e)}")
        return {"error": f"Error generando etiqueta: {str(e)}"}
    

def validar_payload_estructura(payload: dict) -> tuple[bool, str]:
    """Valida la estructura básica del payload"""
    
    campos_requeridos = [
        "autenticacion_zoom",
        "configuracion_envio",
        "servicio",
        "ubicacion_origen",
        "ubicacion_destino",
        "remitente",
        "destinatario",
        "paquete"
    ]
    
    for campo in campos_requeridos:
        if campo not in payload:
            logger.error(f"Campo requerido faltante: {campo}")            
            return False, f"Campo requerido faltante: {campo}"
        elif debug: logger.info(f"Payload recibido: {payload}")
    
    # Validar autenticación
    auth = payload["autenticacion_zoom"]
    if "login" not in auth or "clave" not in auth:
        logger.error("Faltan credenciales de autenticación")
        return False, "Faltan credenciales de autenticación"
    elif debug: logger.info(f"Payload recibido: {payload}")
    
    # Validar configuración
    config = payload["configuracion_envio"]
    if "tipo_envio" not in config:
        logger.error("Falta tipo_envio en configuración")
        return False, "Falta tipo_envio en configuración"
    elif debug: logger.info(f"Payload recibido: {payload}")
    
    # Validar servicio
    servicio = payload["servicio"]
    if "codservicio" not in servicio:
        logger.error("Falta codservicio en servicio")
        return False, "Falta codservicio en servicio"
    elif debug: logger.info(f"Payload recibido: {payload}")
    
    # Validar ubicaciones básicas
    for ubicacion in ["ubicacion_origen", "ubicacion_destino"]:
        ubic = payload[ubicacion]
        if "ciudad" not in ubic or "codciudad" not in ubic["ciudad"]:
            logger.error(f"Falta información de ciudad en {ubicacion}")
            return False, f"Falta información de ciudad en {ubicacion}"
        elif debug: logger.info(f"Payload recibido: {payload}")
    
    # Validar remitente y destinatario
    for contacto in ["remitente", "destinatario"]:
        cont = payload[contacto]
        if "datos_personales" not in cont:
            logger.error(f"Faltan datos personales en {contacto}")
            return False, f"Faltan datos personales en {contacto}"
        elif debug: logger.info(f"Payload recibido: {payload}")
        
        datos = cont["datos_personales"]
        if "nombre_completo" not in datos:
            logger.error(f"Falta nombre_completo en {contacto}")
            return False, f"Falta nombre_completo en {contacto}"
        elif debug: logger.info(f"Payload recibido: {payload}")
        if "numero_documento" not in datos:
            logger.error(f"Falta numero_documento en {contacto}")
            return False, f"Falta numero_documento en {contacto}"
        elif debug: logger.info(f"Payload recibido: {payload}")
    
    # Validar paquete
    paquete = payload["paquete"]
    if "peso_total" not in paquete or "numero_piezas" not in paquete:
        logger.error("Falta información básica del paquete")
        return False, "Falta información básica del paquete"
    elif debug: logger.info(f"Payload recibido: {payload}")
    
    # Validar tipo de envío específico
    tipo_envio = config["tipo_envio"]
    if tipo_envio not in ["nacional", "internacional", "casillero_aereo", "casillero_maritimo"]:
        logger.error(f"Tipo de envío no válido: {tipo_envio}")
        return False, f"Tipo de envío no válido: {tipo_envio}"
    elif debug: logger.info(f"Payload recibido: {payload}")
    if debug: logger.info(f"Payload recibido completo y con éxito: {payload}")
    return True, ""


def obtener_autenticacion_zoom(cliente: ClienteZoom, payload: dict) -> dict:
    """Obtiene token y certificado de Zoom"""
    
    auth = payload["autenticacion_zoom"]
    login = auth["login"]
    clave = auth["clave"]
    
    resultado = {}
    
    try:
        # 1. Obtener token
        #print (f"Login: {login}, Clave: {clave}")
        if not login or not clave:
            logger.error("Faltan credenciales de login o clave")
            return {"error": "Faltan credenciales de login o clave"}                    
        elif debug: logger.info(f"Payload recibido: {payload}")
        token_resp = cliente.crear_token({
            "login": login,
            "clave": clave
        })
        
        entidad_token = token_resp.get("entidadRespuesta")
        token = None
        
        if entidad_token:
            # if isinstance(entidad_token, list) and len(entidad_token) > 0:
            #     token = entidad_token[0].get("token")
            # elif isinstance(entidad_token, dict):
            token = entidad_token.get("token")
        
        if token:
            resultado["token"] = token
            if debug: 
                logger.info(f"Token obtenido exitosamente para login: {login}, clave: {clave}")
        else:
            resultado["error"] = token_resp
            logger.error(f"Error obteniendo token: {token_resp}, no se procede. login: {login}, clave: {clave}")
            return resultado
    
        # 2. Obtener certificado
        if token and payload.get("configuracion_envio", {}).get("requerir_certificado", False):            
            cert_resp = cliente.zoom_cert({
                "login": login,
                "password": clave,
                "token": token,
                "frase_privada": auth.get("frase_secreta", "")
            })
            
            if debug: 
                logger.info(f"Certificado obtenido para los datos de login: {login} y clave: {clave}")
            
            entidad_cert = cert_resp.get("entidadRespuesta")
            certificado = None
            
            if entidad_cert:
                if isinstance(entidad_cert, list):
                    # Buscar certificado en la lista
                    for item in entidad_cert:
                        if isinstance(item, dict) and "certificado" in item:
                            certificado = item["certificado"]
                            break
                elif isinstance(entidad_cert, dict):
                    certificado = entidad_cert.get("certificado")
            
            if certificado:
                resultado["certificado"] = certificado
                if debug: 
                    logger.info(f"Certificado obtenido exitosamente para login: {login}, clave: {clave}")
            else:
                resultado["error"] = cert_resp
                logger.error(f"Error obteniendo certificado: {cert_resp}, login: {login}, clave: {clave}")
                return resultado
            
            logger.info(f"Certificado obtenido para los datos de login: {login} y clave: {clave}")
        
        return resultado
        
    except Exception as e:
        logger.error(f"Error en autenticación: {str(e)}")
        resultado["error"] = f"Error de autenticación: {str(e)}"
    if debug: logger.info(f"Resultado de autenticación: {resultado}")
    return resultado


def calcular_tarifa_envio(cliente: ClienteZoom, payload: dict) -> dict:
    """Calcula la tarifa según el tipo de envío"""
    
    tipo_envio = payload["configuracion_envio"]["tipo_envio"]
    
    try:
        if tipo_envio == "nacional":
            # Usar CalcularTarifa para nacionales
            params = {
                "tipo_tarifa": payload["servicio"]["tipo_tarifa"],
                "modalidad_tarifa": payload["servicio"]["modalidad_tarifa"],
                "ciudad_remitente": payload["ubicacion_origen"]["ciudad"]["codciudad"],
                "ciudad_destinatario": payload["ubicacion_destino"]["ciudad"]["codciudad"],
                #oficina solo es requerido si configuracion--> retira_oficina es True
                "oficina_retirar": payload["ubicacion_destino"]["oficina"]["codoficina"] if payload.get("destinatario", {}).get("configuracion", {}).get("retira_oficina") else "",
                "cantidad_piezas": payload["paquete"]["numero_piezas"],
                "peso": payload["paquete"]["peso_total"],
                "valor_mercancia": payload["paquete"]["valores"]["valor_mercancia"],
                "valor_declarado": payload["paquete"]["valores"]["valor_declarado"],
                "codpais": payload["ubicacion_origen"]["pais"]["codpais"],
                "tipo_envio": "0",  # COD y Nacional
                "zona_postal": payload["ubicacion_origen"]["ciudad"].get("codpostal"),
                "alto": payload["paquete"]["dimensiones"]["alto"],
                "ancho": payload["paquete"]["dimensiones"]["ancho"],
                "largo": payload["paquete"]["dimensiones"]["largo"]
            }
            
            # Agregar oficina si es retirar por oficina
            # if payload.get("destinatario", {}).get("configuracion", {}).get("retira_oficina"):
            #     params["oficina_retirar"] = payload["ubicacion_destino"]["oficina"]["codoficina"]
            #print (f"Parametros para calcular tarifa nacional: {params}")
            return cliente.obtener_tarifa(**params)
        
        elif tipo_envio == "internacional":
            # Usar consultarPreciosWs para internacional
            return cliente.consultar_precio_internacional(
                pesob=payload["paquete"]["peso_total"],
                fecha_envio=datetime.now().strftime("%Y-%m-%d"),
                siglas_pd=payload["ubicacion_destino"]["pais"]["siglas_pais"],
                ciudad_d=payload["ubicacion_destino"]["ciudad"]["nombre"],
                siglas_po=payload["ubicacion_origen"]["pais"]["siglas_pais"],
                ciudad_o=payload["ubicacion_origen"]["ciudad"]["nombre"],
                valor_declarado=payload["paquete"]["valores"]["valor_declarado"],
                merdoc="M" if payload["paquete"]["tipo_paquete"] == "M" else "D",
                codciudadori=payload["ubicacion_origen"]["ciudad"]["codciudad"],
                alto=payload["paquete"]["dimensiones"]["alto"],
                ancho=payload["paquete"]["dimensiones"]["ancho"],
                largo=payload["paquete"]["dimensiones"]["largo"],
                zipcode_d=payload["ubicacion_destino"]["ciudad"].get("codpostal"),
                zipcode_o=payload["ubicacion_origen"]["ciudad"].get("codpostal")
            )
        
        elif tipo_envio == "casillero_aereo":
            return cliente.consultar_precio_casillero_aereo(
                codpais_remitente=payload["ubicacion_origen"]["pais"]["codpais"],
                codpais_destinatario=payload["ubicacion_destino"]["pais"]["codpais"],
                oficina_retirar=1 if payload.get("destinatario", {}).get("configuracion", {}).get("retira_oficina") else 2,
                peso=payload["paquete"]["peso_total"],
                valor_mercancia=payload["paquete"]["valores"]["valor_mercancia"],
                ciudad_destinatario=payload["ubicacion_destino"]["ciudad"]["codciudad"] 
                    if payload["ubicacion_destino"]["pais"]["codpais"] == 124 else None
            )
        
        elif tipo_envio == "casillero_maritimo":
            return cliente.consultar_precio_casillero_maritimo(
                codpais_remitente=payload["ubicacion_origen"]["pais"]["codpais"],
                codpais_destinatario=payload["ubicacion_destino"]["pais"]["codpais"],
                oficina_retirar=1 if payload.get("destinatario", {}).get("configuracion", {}).get("retira_oficina") else 2,
                peso=payload["paquete"]["peso_total"],
                valor_mercancia=payload["paquete"]["valores"]["valor_mercancia"],
                ciudad_destinatario=payload["ubicacion_destino"]["ciudad"]["codciudad"] 
                    if payload["ubicacion_destino"]["pais"]["codpais"] == 124 else None,
                alto=payload["paquete"]["dimensiones"]["alto"],
                ancho=payload["paquete"]["dimensiones"]["ancho"],
                largo=payload["paquete"]["dimensiones"]["largo"]
            )
    
    except Exception as e:
        logger.error(f"Error calculando tarifa: {str(e)}")
        return {"error": f"Error calculando tarifa: {str(e)}"}
    
    return {"error": f"Tipo de envío no soportado para cálculo: {tipo_envio}"}


def guardar_remitente_zoom(cliente: ClienteZoom, payload: dict) -> Optional[str]:
    """Guarda/actualiza remitente en Zoom"""
    
    try:
        remitente_data = {
            "codigo_oficina": payload["ubicacion_origen"]["oficina"]["codoficina"],
            "nombre_remitente": payload["remitente"]["datos_personales"]["nombre_completo"],
            "cirif": f"{payload['remitente']['datos_personales']['tipo_documento']}{payload['remitente']['datos_personales']['numero_documento']}",
            "contacto_remitente": payload["remitente"]["datos_personales"].get("contacto", 
                payload["remitente"]["datos_personales"]["nombre_completo"]),
            "direccion_remitente": payload["remitente"]["direccion"]["direccion_completa"],
            "ciudad_remitente": payload["ubicacion_origen"]["ciudad"]["codciudad"],
            "telefono_remitente": payload["remitente"]["datos_personales"]["telefono_movil"] or 
                                  payload["remitente"]["datos_personales"]["telefono_fijo"],
            "observacion": payload.get("informacion_adicional", {}).get("observaciones", ""),
            "codigo_usuario": payload["autenticacion_zoom"].get("cliente_id"),
            "parroquia_remitente": payload["ubicacion_origen"]["parroquia"]["codparroquia"],
            "municipio_remitente": payload["ubicacion_origen"]["municipio"]["codmunicipio"],
            "codpostal_remitente": payload["ubicacion_origen"]["ciudad"].get("codpostal"),
            "ciudad_ipostel": payload["remitente"]["configuracion"].get("ciudad_ipostel"),
            "inmueble_remitente": payload["remitente"]["direccion"]["inmueble"],
            "celular_remitente": payload["remitente"]["datos_personales"]["telefono_movil"],
            #"codremitente": payload["remitente"].get("remitente_id")
        }
        #print (f"Datos para guardar remitente: {remitente_data}")
        respuesta = cliente.guardar_remitente_ws(remitente_data)
        #print (f"Respuesta al guardar remitente: {respuesta}")
        if respuesta.get("codrespuesta")!="COD_001":
            logger.error(f"Error en respuesta al guardar remitente: {respuesta}")
            return None
        #print (respuesta)
        return respuesta.get("entidadRespuesta", {}).get("codremitente") 
    
    except Exception as e:
        logger.error(f"Error guardando remitente: {str(e)}")
        return None


def guardar_destinatario_zoom(cliente: ClienteZoom, payload: dict) -> Optional[str]:
    """Guarda/actualiza destinatario en Zoom"""
    
    try:
        destinatario_data = {
            "codigo_usuario": payload["autenticacion_zoom"].get("cliente_id", ""),
            "nombre_destinatario": payload["destinatario"]["datos_personales"]["nombre_completo"],
            "direccion_destino": payload["destinatario"]["direccion"]["direccion_completa"],
            "contacto_destinatario": payload["destinatario"]["datos_personales"].get("contacto", 
                payload["destinatario"]["datos_personales"]["nombre_completo"]),
            "cirif_destinatario": f"{payload['destinatario']['datos_personales']['tipo_documento']}{payload['destinatario']['datos_personales']['numero_documento']}",
            "telefono_destinatario": payload["destinatario"]["datos_personales"]["telefono_movil"] or 
                                     payload["destinatario"]["datos_personales"]["telefono_fijo"],
            "fax_destinatario": payload["destinatario"]["datos_personales"].get("telefono_movil"),
            "email_destinatario": payload["destinatario"]["datos_personales"].get("email", ""),
            "codciudad_destino": payload["ubicacion_destino"]["ciudad"]["codciudad"],
            "codpais_destino": payload["ubicacion_destino"]["pais"]["codpais"],
            "ciudad_destinoint": payload["ubicacion_destino"]["ciudad"]["nombre"],
            "referencia": payload["paquete"]["referencias"].get("referencia_cliente", ""),
            "municipio_destino": payload["ubicacion_destino"]["municipio"]["codmunicipio"],
            "parroquia_destino": payload["ubicacion_destino"]["parroquia"]["codparroquia"],
            "codpostal_destino": payload["ubicacion_destino"]["ciudad"].get("codpostal"),
            "ciudad_ipostel": payload["destinatario"]["configuracion"].get("ciudad_ipostel"),
            "estado_destino": payload["ubicacion_destino"]["estado"]["nombre"],
            "immueble_destinatario": payload["destinatario"]["direccion"]["inmueble"],
            "celular_destinatario": payload["destinatario"]["datos_personales"]["telefono_movil"]
        }
        
        respuesta = cliente.guardar_destinatarios_ws(destinatario_data)
        #print (respuesta)
        if respuesta.get("codrespuesta")!="COD_001":
            logger.error(f"Error en respuesta al guardar destinatario: {respuesta}")
            return None
        return respuesta
    
    except Exception as e:
        logger.error(f"Error guardando destinatario: {str(e)}")
        return None


def crear_envio_segun_tipo(cliente: ClienteZoom, payload: dict, tipo_envio: str, token: str, certificado: Optional[str] = None) -> dict:
    """Crea el envío según el tipo"""
    
    if tipo_envio == "nacional":
        return crear_envio_nacional(cliente, payload, token)
    elif tipo_envio in ["internacional", "casillero_aereo", "casillero_maritimo"]:
        # Pasar certificado en una copia para no mutar el payload original
        payload_int = {**payload}
        if certificado is not None:
            payload_int["_certificado"] = certificado
        return crear_envio_internacional(cliente, payload_int, tipo_envio)
    else:
        return {"error": f"Tipo de envío no soportado: {tipo_envio}"}


def crear_envio_nacional(cliente: ClienteZoom, payload: dict, token: str) -> dict:
    """Crea envío nacional"""
    
    envio_data = {
        "login": payload["autenticacion_zoom"]["login"],
        "clave": payload["autenticacion_zoom"]["clave"],
        "codservicio": payload["servicio"]["codservicio"],
        "remitente": payload["remitente"]["datos_personales"]["nombre_completo"],
        "contacto_remitente": payload["remitente"]["datos_personales"].get("contacto", 
            payload["remitente"]["datos_personales"]["nombre_completo"]),
        "codciudadrem": payload["ubicacion_origen"]["ciudad"]["codciudad"],
        "tiporifcirem": payload["remitente"]["datos_personales"]["tipo_documento"],
        "cirifrem": payload["remitente"]["datos_personales"]["numero_documento"],
        "codmunicipiorem": payload["ubicacion_origen"]["municipio"]["codmunicipio"],
        "codparroquiarem": payload["ubicacion_origen"]["parroquia"]["codparroquia"],
        "zona_postal_remitente": payload["remitente"]["direccion"]["zona_postal"],
        "telefono_remitente": payload["remitente"]["datos_personales"]["telefono_fijo"] 
                            or payload["remitente"]["datos_personales"].get("telefono_movil"),
        "codcelurem": payload["remitente"]["datos_personales"].get("telefono_movil")[0:4],
        "celularrem": payload["remitente"]["datos_personales"].get("telefono_movil")[-7:],
        "direccion_remitente": payload["remitente"]["direccion"]["direccion_completa"],
        "inmueble_remitente": payload["remitente"]["direccion"]["inmueble"],
        "retira_oficina": 1 if payload.get("destinatario", {}).get("configuracion", {}).get("retira_oficina") else 0,
        "codciudaddes": payload["ubicacion_destino"]["ciudad"]["codciudad"],
        "destinatario": payload["destinatario"]["datos_personales"]["nombre_completo"],
        "codciudaddes": payload["ubicacion_destino"]["ciudad"]["codciudad"],
        "codmunicipiodes": payload["ubicacion_destino"]["municipio"]["codmunicipio"],
        "codparroquiades": payload["ubicacion_destino"]["parroquia"]["codparroquia"],
        "zona_postal_destino": payload["destinatario"]["direccion"].get("zona_postal", ""),
        "codoficinades":payload["ubicacion_destino"]["oficina"]["codoficina"],# if payload.get("destinatario", {}).get("configuracion", {}).get("retira_oficina") else "",
        "destinatario": payload["destinatario"]["datos_personales"]["nombre_completo"],
        "contacto_destino": payload["destinatario"]["datos_personales"].get("contacto", 
            payload["destinatario"]["datos_personales"]["nombre_completo"]),
        "tiporifcidest": payload["destinatario"]["datos_personales"]["tipo_documento"],
        "cirif_destinatario": payload["destinatario"]["datos_personales"]["numero_documento"],
        "codceludest": payload["destinatario"]["datos_personales"].get("telefono_movil")[0:4],
        "celular": payload["destinatario"]["datos_personales"].get("telefono_movil")[-7:],
        "telefono_destino": payload["destinatario"]["datos_personales"]["telefono_fijo"],
        "direccion_destino": payload["destinatario"]["direccion"]["direccion_completa"],
        "inmueble_destino": payload["destinatario"]["direccion"]["inmueble"],
        "descripcion_contenido": payload["paquete"]["descripcion"],
        "referencia": payload["paquete"]["referencias"]["referencia_cliente"],
        "numero_piezas": payload["paquete"]["numero_piezas"],
        "campo1": payload.get("informacion_adicional", {}).get("observaciones", ""),
        "campo2": payload.get("informacion_adicional", {}).get("observaciones", ""),
        "campo3": payload.get("informacion_adicional", {}).get("observaciones", ""),
        "numero_piezas": payload["paquete"]["numero_piezas"],
        "peso_bruto": payload["paquete"]["peso_total"],
        "tipo_envio": payload["paquete"]["tipo_paquete"],
        "valor_declarado": payload["paquete"]["valores"]["valor_declarado"],
        "seguro": 1 if payload["servicio"]["seguro"] else 0,
        "valor_mercancia": payload["paquete"]["valores"]["valor_mercancia"],
        "modalidad_cod": payload["servicio"].get("modalidad_cod", 0),
        "codigo_casillero": payload.get("casillero_codigo", ""),
        "siglas_casillero": payload.get("casillero_siglas", ""),
        "web_services": 1
    }
    #try:
    #print (f"Datos para crear envío nacional: {envio_data}")
    #agergar el token con append
    
    return cliente.create_shipment(envio_data , token)         
    # except Exception as e:
    #        logger.error(f"Error creando envío nacional: {str(e)}")
    #        return {"error": f"Error creando envío nacional: {str(e)}"}


def crear_envio_internacional(cliente: ClienteZoom, payload: dict, tipo_envio: str) -> dict:
    """Crea envío internacional o casillero"""
    
    if tipo_envio == "internacional":
        codservicio = 3  # Servicio internacional estándar
    elif tipo_envio == "casillero_aereo":
        codservicio = 4
    elif tipo_envio == "casillero_maritimo":
        codservicio = 5
    else:
        codservicio = 99  # Genérico
    
    envio_data = {
        "login": payload["autenticacion_zoom"]["login"],
        "clave": payload["autenticacion_zoom"]["clave"],
        "certificado": payload.get("_certificado", ""),
        "codservicio": codservicio,
        "remitente": payload["remitente"]["datos_personales"]["nombre_completo"],
        "contacto_remitente": payload["remitente"]["datos_personales"].get("contacto", 
            payload["remitente"]["datos_personales"]["nombre_completo"]),
        "telefono_remitente": payload["remitente"]["datos_personales"]["telefono_fijo"],
        "direccion_remitente": payload["remitente"]["direccion"]["direccion_completa"],
        "codpaisdes": payload["ubicacion_destino"]["pais"]["codpais"],
        "ciudaddes": payload["ubicacion_destino"]["ciudad"]["nombre"],
        "destinatario": payload["destinatario"]["datos_personales"]["nombre_completo"],
        "contacto_destino": payload["destinatario"]["datos_personales"].get("contacto", 
            payload["destinatario"]["datos_personales"]["nombre_completo"]),
        "rif_ci_destinatario": f"{payload['destinatario']['datos_personales']['tipo_documento']}{payload['destinatario']['datos_personales']['numero_documento']}",
        "telefono_destino": payload["destinatario"]["datos_personales"]["telefono_fijo"],
        "direcciondes": payload["destinatario"]["direccion"]["direccion_completa"],
        "tipo_envio": payload["paquete"]["tipo_paquete"],
        "numero_piezas": payload["paquete"]["numero_piezas"],
        "peso_bruto": payload["paquete"]["peso_total"],
        "valor_declarado": payload["paquete"]["valores"]["valor_declarado"],
        "descripcion_contenido": payload["paquete"]["descripcion"],
        "web_services": 1,
        "retira_oficina": 1 if payload.get("destinatario", {}).get("configuracion", {}).get("retira_oficina") else 0,
        "seguro": 1 if payload["servicio"]["seguro"] else 0
    }
    
    # Agregar dimensiones si están disponibles
    if "dimensiones" in payload["paquete"]:
        envio_data.update({
            "alto": payload["paquete"]["dimensiones"]["alto"],
            "ancho": payload["paquete"]["dimensiones"]["ancho"],
            "largo": payload["paquete"]["dimensiones"]["largo"]
        })
    
    # Agregar oficina de destino si es retirar por oficina
    if payload.get("destinatario", {}).get("configuracion", {}).get("retira_oficina"):
        envio_data["codoficinades"] = payload["ubicacion_destino"]["oficina"]["codoficina"]
    
    return cliente.create_shipment_internacional(envio_data)

#-------------------------------------------------fin endpoint orquestador propio------------------------------------------------------
# ===== Reimpresion de etiquetas =====
@bp_privadas.post("/delivery/zoom/ReimprimirEtiqueta")
@requerir_api_key(Delivery_Empresa="ZOOM")
def reimprimir_etiqueta():
    payload = request.get_json(silent=True) or {}
    cliente = _cliente_Zoom()
    guia = payload.get("guia_zoom")
    data = reimprimir_guia(cliente, guia)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

@bp_privadas.post("/delivery/zoom/ConsultaTracking")
@requerir_api_key(Delivery_Empresa="ZOOM")
def consulta_tracking():
    payload = request.get_json(silent=True) or {}
    cliente = _cliente_Zoom()
    #guia = payload.get("guia_zoom")
    data = cliente.consulta_tracking(payload)
    # if data.get("error"):
    #     return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify(data)
# ------------------------ ZOOM ---------------------------------------

@bp_privadas.post("/GuardarRemitenteWs")
@requerir_api_key(Delivery_Empresa="ZOOM")
def guardar_remitente_ws():
    payload = request.get_json(silent=True) or {}
    cliente = _cliente_Zoom()
    data = cliente.guardar_remitente_ws(payload)
    return jsonify({"ok": True, "data": data})

@bp_privadas.post("/GuardarDestinatariosWs")
@requerir_api_key(Delivery_Empresa="ZOOM")
def guardar_destinatarios_ws():
    payload = request.get_json(silent=True) or {}
    cliente = _cliente_Zoom()
    data = cliente.guardar_destinatarios_ws(payload)
    return jsonify({"ok": True, "data": data})

@bp_privadas.post("/crearToken")
@requerir_api_key(Delivery_Empresa="ZOOM")
def crear_token():
    payload = request.get_json(silent=True) or {}
    cliente = _cliente_Zoom()
    data = cliente.crear_token(payload)
    return jsonify({"ok": True, "data": data})

@bp_privadas.post("/createShipmentInternacional")
@requerir_api_key(Delivery_Empresa="ZOOM")
def create_shipment_internacional():
    payload = request.get_json(silent=True) or {}
    cliente = _cliente_Zoom()
    data = cliente.create_shipment_internacional(payload)
    return jsonify({"ok": True, "data": data})

@bp_privadas.post("/etiquetaTermica")
@requerir_api_key(Delivery_Empresa="ZOOM")
def etiqueta_termica():
    payload = request.get_json(silent=True) or {}
    cliente = _cliente_Zoom()
    data = cliente.etiqueta_termica(payload)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

@bp_privadas.post("/crearRecolectaWs")
@requerir_api_key(Delivery_Empresa="ZOOM")
def crear_recolecta_ws():
    payload = request.get_json(silent=True) or {}
    cliente = _cliente_Zoom()
    data = cliente.crear_recolecta_ws(payload)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

@bp_privadas.post("/crearClienteWs")
@requerir_api_key(Delivery_Empresa="ZOOM")
def crear_cliente_ws():
    payload = request.get_json(silent=True) or {}
    cliente = _cliente_Zoom()
    data = cliente.crear_cliente_ws(payload)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})


# ------------------------ ARMI ---------------------------------------
#-----Businesses (Negocios)-----
@bp_privadas.post("/armi/monitor/business/create")
@requerir_api_key(Delivery_Empresa="ARMI")
def crear_negocio_armi():    
    payload = request.get_json(silent=True) or {}
    cliente = _cliente_Armi()
    data = cliente.crear_negocio(payload)
    # if data.get("error"):
    #     return jsonify({"ok": False, "error": data.get("error")}), 400
    # return jsonify({"ok": True, "data": data})
    return jsonify(data)

@bp_privadas.get("/armi/monitor/business/<int:negocio_id>")
@requerir_api_key(Delivery_Empresa="ARMI")
def consultar_negocio_armi(negocio_id: int):    
    cliente = _cliente_Armi()
    data = cliente.consultar_negocio(negocio_id)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

@bp_privadas.delete("/armi/monitor/business/<int:negocio_id>")
@requerir_api_key(Delivery_Empresa="ARMI")
def eliminar_negocio_armi(negocio_id: int):    
    cliente = _cliente_Armi()
    data = cliente.eliminar_negocio(negocio_id)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

@bp_privadas.get("/armi/monitor/business/all/<int:user_id>")
@requerir_api_key(Delivery_Empresa="ARMI")
def listar_negocios_usuario_armi(user_id: int):
    cliente = _cliente_Armi()
    data = cliente.negocios_del_usuario(user_id)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

@bp_privadas.post("/armi/monitor/business/update/<int:negocio_id>")
@requerir_api_key(Delivery_Empresa="ARMI")
def actualizar_negocio_armi(negocio_id: int):
    payload = request.get_json(silent=True) or {}
    cliente = _cliente_Armi()
    data = cliente.actualizar_negocio(negocio_id, payload)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

#-----Branch Offices (Sucursales)-----
@bp_privadas.post("/armi/monitor/branchOffice/create")
@requerir_api_key(Delivery_Empresa="ARMI")
def crear_sucursal_armi():
    payload = request.get_json(silent=True) or {}
    cliente = _cliente_Armi()
    data = cliente.crear_sucursal(payload)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

@bp_privadas.get("/armi/monitor/branchOffice/all/<int:business_id>")
@requerir_api_key(Delivery_Empresa="ARMI")
def listar_sucursales_armi(business_id: int):
    cliente = _cliente_Armi()
    data = cliente.sucursales_del_negocio(business_id)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})
#Error en el endpoint eliminar sucursal (pide código de la ciudad o de país???)
@bp_privadas.delete("/armi/monitor/branchOffice/delete")
@requerir_api_key(Delivery_Empresa="ARMI")
def eliminar_sucursal_armi():
    payload = request.get_json(silent=True) or {}
    branch_office_id = payload.get("branchOfficeId")
    business_id = payload.get("businessId")
    if not branch_office_id or not business_id:
        return jsonify({"ok": False, "error": "branchOfficeId y businessId son requeridos"}), 400
    cliente = _cliente_Armi()
    data = cliente.eliminar_sucursal(int(branch_office_id), int(business_id))
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

#-----Orders (Órdenes)-----
@bp_privadas.post("/armi/monitor/order/create")
@requerir_api_key(Delivery_Empresa="ARMI")
def crear_orden_armi():
    payload = request.get_json(silent=True) or {}
    cliente = _cliente_Armi()
    data = cliente.crear_orden(payload)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data}), 201

@bp_privadas.post("/armi/monitor/order/cancel")
@requerir_api_key(Delivery_Empresa="ARMI")
def cancelar_orden_armi():
    payload = request.get_json(silent=True) or {}
    cliente = _cliente_Armi()
    data = cliente.cancelar_orden(payload)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

@bp_privadas.get("/armi/monitor/order/status/<int:order_id>")
@requerir_api_key(Delivery_Empresa="ARMI")
def estado_orden_armi(order_id: int):
    cliente = _cliente_Armi()
    data = cliente.estado_orden(order_id)
    catalogo_por_nombre = {item["NAME"]: item["DESCRIPTION"] for item in catalogo_dict.values()}
    nombre_estado = data.get("orderStatus") 
    if nombre_estado and nombre_estado in catalogo_por_nombre:
        data["orderStatusDescription"] = catalogo_por_nombre[nombre_estado]
    # Si también quieres el ID
        data["orderStatusId"] = next(item["ID"] for item in catalogo_dict.values() if item["NAME"] == nombre_estado)
    else:
        data["orderStatusDescription"] = "Estado desconocido"
    
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify( data)

@bp_privadas.get("/armi/monitor/city/<string:city>")
@requerir_api_key(Delivery_Empresa="ARMI")
def codigo_ciudad_armi(city: str):    
    cliente = _cliente_Armi()    
    data = cliente.codigo_ciudad(city)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify(data)

@bp_privadas.post("/armi/monitor/order/delivery-cost")
@requerir_api_key(Delivery_Empresa="ARMI")
def costo_envio_armi():
    payload = request.get_json(silent=True) or {}
    cliente = _cliente_Armi()
    data = cliente.costo_envio(payload)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify(data)

# ------ INSTALEAP INTEGRATION ----------------

@bp_privadas.post("/armi/monitor/instaleap/create")
@requerir_api_key(Delivery_Empresa="ARMI_INSTALEAP")
def crear_orden_instaleap():
    """
    Endpoint para recibir órdenes desde Instaleap
    """
    payload = request.get_json(silent=True) or {}
    
    logger.info(f"Instaleap create - Payload recibido. Task ID: {payload.get('task_id')}")
    
    # Validar campos mínimos
    campos_requeridos = ["task_id", "job_number", "client_id", "created_at"]
    for campo in campos_requeridos:
        if campo not in payload:
            return jsonify({
                "ok": False,
                "error": f"Campo requerido faltante: {campo}",
                "task_id": payload.get("task_id")
            }), 400
    
    cliente = _cliente_Armi()
    
    try:
        # ===== 1. TRANSFORMAR PAYLOAD =====
        payload_armi = transformar_payload_instaleap_a_armi(payload)
        
        
        # ===== 2. BUSCAR MAPEO DE TIENDA =====
        # store_ref = payload.get("origin", {}).get("store_reference", "")
        # client_id = payload.get("client_id", "")
        branch_office_id = payload.get("origin", {}).get("store_reference", "")
        business_id = payload.get("client_id", "")
        
        # business_id, branch_office_id = buscar_mapa_tienda_instaleap(store_ref, client_id)
        
        # if not business_id:
        #     return jsonify({
        #         "ok": False,
        #         "error": f"Tienda no configurada: {store_ref}",
        #         "task_id": payload.get("task_id")
        #     }), 400
        
        # ===== 3. COMPLETAR IDs EN PAYLOAD =====
        payload_armi["business_id"] = business_id
        for producto in payload_armi.get("products", []):
            producto["store_id"] = branch_office_id
        
        logger.debug(f"Payload ARMI completo: {json.dumps(payload_armi, indent=2)}")
        
        # ===== 4. ENVIAR A ARMI =====        
        data = cliente.crear_orden(payload_armi)
        
        if data.get("error"):
            logger.error(f"Error ARMI: {data.get('error')}")
            return jsonify({
                "ok": False,
                "error": f"Error en ARMI: {data.get('error')}",
                "task_id": payload.get("task_id")
            }), 500
        
        # ===== 5. GUARDAR en bd =====
        order_id_armi = data.get("orderId") or data.get("data", {}).get("orderId") or data.get("data", {}).get("id")
        
        # guardar_relacion_instaleap_armi(
        #     task_id=payload.get("task_id"),
        #     job_number=payload.get("job_number"),
        #     client_id=branch_office_id,
        #     order_id_armi=order_id_armi,
        #     business_id=business_id,
        #     branch_office_id=branch_office_id,
        #     payload_original=payload,
        #     payload_armi=payload_armi
        # )
        
        ressultadobd=guardar_envio_instaleap_armi(payload_instaleap=payload , payload_armi=payload_armi)
        print(f"Resultado guardado en bd: {ressultadobd}")
        # ===== 6. RESPONDER =====
        return jsonify({
            "ok": True,
            "data": {
                "instaleap": {
                    "task_id": payload.get("task_id"),
                    "job_number": payload.get("job_number"),
                    "client_id": branch_office_id
                },
                "armi": {
                    "order_id": order_id_armi,
                    "business_id": business_id,
                    "branch_office_id": branch_office_id
                },
                "status": "CREATED",
                "timestamp": datetime.now().isoformat()
            },
            "message": "Orden procesada exitosamente"
        })
        
    except Exception as e:
        logger.exception(f"Error procesando orden Instaleap: {str(e)}")
        return jsonify({
            "ok": False,
            "error": f"Error interno: {str(e)}",
            "task_id": payload.get("task_id")
        }), 500

@bp_privadas.post("/armi/monitor/instaleap/update")
@requerir_api_key(Delivery_Empresa="ARMI")
def actualizar_orden_instaleap():
    """
    Endpoint para actualizar órdenes desde Instaleap
    Según documentación: POST {url_base_integrador_instaleap}/monitor/instaleap/update
    """
    payload = request.get_json(silent=True) or {}
    
    # DEBUG: Log del payload recibido
    logger.info(f"Instaleap update - Payload recibido: {json.dumps(payload, indent=2)}")
    
    # Validar campos mínimos
    if "task_id" not in payload:
        return jsonify({
            "ok": False,
            "error": "Campo requerido faltante: task_id",
            "campos_recibidos": list(payload.keys())
        }), 400
    
    cliente = _cliente_Armi()
    
    try:
        # Llamar a ARMI
        data = cliente.actualizar_orden_instaleap(payload)
        
        if data.get("error"):
            logger.error(f"Error ARMI al actualizar orden Instaleap: {data.get('error')}")
            return jsonify({
                "ok": False,
                "error": data.get("error"),
                "task_id": payload.get("task_id")
            }), 500
            
        logger.info(f"Orden Instaleap actualizada exitosamente: {payload.get('task_id')}")
        return jsonify({
            "ok": True,
            "data": data,
            "message": "Orden actualizada exitosamente",
            "task_id": payload.get("task_id")
        })
        
    except Exception as e:
        logger.exception(f"Error crítico actualizando orden Instaleap: {str(e)}")
        return jsonify({
            "ok": False,
            "error": f"Error actualizando orden: {str(e)}",
            "task_id": payload.get("task_id")
        }), 500


@bp_privadas.get("/armi/monitor/instaleap/tracking-order")
@requerir_api_key(Delivery_Empresa="ARMI")
def tracking_orden_instaleap():
    """
    Endpoint para seguimiento de ubicación en tiempo real
    Según documentación: GET {url_base_integrador_instaleap}/monitor/instaleap/tracking-order
    """
    # Obtener país del header (según documentación)
    country = request.headers.get("country", "COL")
    
    logger.info(f"Instaleap tracking - Country: {country}")
    
    cliente = _cliente_Armi()
    
    try:
        # Este endpoint es especial porque necesita country en header
        data = cliente.tracking_orden_instaleap(country)
        
        if data.get("error"):
            logger.error(f"Error ARMI tracking Instaleap: {data.get('error')}")
            return jsonify({
                "ok": False,
                "error": data.get("error")
            }), 500
            
        logger.info(f"Tracking Instaleap obtenido exitosamente")
        return jsonify({
            "ok": True,
            "data": data,
            "message": "Tracking obtenido exitosamente"
        })
        
    except Exception as e:
        logger.exception(f"Error crítico obteniendo tracking Instaleap: {str(e)}")
        return jsonify({
            "ok": False,
            "error": f"Error obteniendo tracking: {str(e)}"
        }), 500


@bp_privadas.put("/armi/monitor/instaleap/cash/received")
@requerir_api_key(Delivery_Empresa="ARMI")
def confirmar_cash_recibido_instaleap():
    """
    Endpoint para confirmar pago en efectivo recibido
    Según documentación: PUT {url_base_integrador_instaleap}/monitor/instaleap/cash/received
    """
    payload = request.get_json(silent=True) or {}
    
    # DEBUG: Log del payload recibido
    logger.info(f"Instaleap cash received - Payload recibido: {json.dumps(payload, indent=2)}")
    
    # Validar campos según documentación
    if "id" not in payload or "type" not in payload:
        return jsonify({
            "ok": False,
            "error": "Campos requeridos faltantes: id y type",
            "campos_recibidos": list(payload.keys())
        }), 400
    
    # Validar que sea evento CLIENT_RECEIVED
    if payload.get("type") != "CLIENT_RECEIVED":
        return jsonify({
            "ok": False,
            "error": f"Tipo de evento no válido: {payload.get('type')}. Se espera CLIENT_RECEIVED",
            "warning": "Este endpoint solo procesa eventos CLIENT_RECEIVED"
        }), 400
    
    cliente = _cliente_Armi()
    
    try:
        # Llamar a ARMI
        data = cliente.confirmar_cash_recibido(payload)
        
        if data.get("error"):
            logger.error(f"Error ARMI confirmando cash: {data.get('error')}")
            return jsonify({
                "ok": False,
                "error": data.get("error"),
                "event_id": payload.get("id")
            }), 500
            
        logger.info(f"Cash recibido confirmado exitosamente: {payload.get('id')}")
        return jsonify({
            "ok": True,
            "data": data,
            "message": "Pago en efectivo confirmado exitosamente",
            "event_id": payload.get("id")
        })
        
    except Exception as e:
        logger.exception(f"Error crítico confirmando cash Instaleap: {str(e)}")
        return jsonify({
            "ok": False,
            "error": f"Error confirmando pago: {str(e)}",
            "event_id": payload.get("id")
        }), 500

# ---- Callback de Notificación de estados ----
#propio
@bp_callbacks.post("/status")
def callback_estado_armi():
    """
    Callback que ARMI llama para notificar cambios de estado
    Según documentación: POST {url_base_integrador}/update/status
    """
    payload = request.get_json(silent=True) or {}
    
    logger.info(f"Callback ARMI estado recibido: {json.dumps(payload, indent=2)}")
    
    # Validar campos mínimos
    campos_requeridos = ["orderId", "status"]
    for campo in campos_requeridos:
        if campo not in payload:
            logger.error(f"Campo requerido faltante en callback: {campo}")
            return jsonify({
                "ok": False,
                "error": f"Campo requerido faltante: {campo}"
            }), 400
    
    # Procesar el cambio de estado
    try:
        order_id = payload.get("orderId")
        status_code = payload.get("status")
        order_invoice = payload.get("orderInvoice")
        created_at = payload.get("createdAt")
        
        # Aquí debes implementar tu lógica de negocio
        # Ejemplo: Actualizar tu base de datos, notificar a otros sistemas, etc.
        
        logger.info(f"Procesando cambio de estado ARMI - Order: {order_id}, Status: {status_code}")
        
        
        if status_code in catalogo_dict:
            estado = catalogo_dict[status_code]            
            estado_name = estado['NAME']
            estado_description = estado['DESCRIPTION']
        else:            
            estado_name = f"DESCONOCIDO_{status_code}"
            estado_description = "Estado no reconocido en el catálogo"
        
        # TODO: Implementar lógica de procesamiento aquí
        # Por ejemplo:
        # - Buscar orden en tu DB por orderId
        # - Actualizar estado
        # - Registrar histórico
        # - Notificar a sistemas internos
        
        # Respuesta exitosa
        return jsonify({
            "ok": True,
            "message": "Estado procesado exitosamente",
            #"orderId": order_id,
            "status_id": status_code,
            "status_name": estado_name,
            "status_description": estado_description,
            "status_fecha": created_at
            })
        
    except Exception as e:
        logger.exception(f"Error procesando callback ARMI: {str(e)}")
        return jsonify({
            "ok": False,
            "error": f"Error procesando callback: {str(e)}",
            "orderId": payload.get("orderId")
        }), 500


