"""
Rutas privadas unificadas (clientes y envíos) ZOOM y ARMI
------------------------------------------------------
"""
import json
import logging
import base64, os
from datetime import datetime
from typing import Optional

from flask import Blueprint, request, jsonify, current_app
from ..core.autenticacion import requerir_api_key
from ..servicios.cliente_zoom import ClienteZoom
from ..servicios.cliente_armi import ClienteArmi
from ..configuracion import Configuracion
from ..db.conexion import ejecutar_sp_resultados

bp_privadas = Blueprint("privadas", __name__)
logger = logging.getLogger(__name__)
debug = Configuracion.DEBUG

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
        num_documento = datos_personales.get("numero_documento")
        if len(num_documento) > 10:
            num_documento = num_documento[:10]  # Truncar si es muy largo
        
        # Obtener teléfono (VARCHAR(14) en BD)
        telefono = datos_personales.get("telefono_movil") or datos_personales.get("telefono_fijo")
        if len(telefono) > 14:
            telefono = telefono[:14]
        
        # Obtener email (VARCHAR(50) en BD)
        mail = datos_personales.get("email")
        if len(mail) > 50:
            mail = mail[:50]
        
        # Obtener dirección (VARCHAR(200) en BD)
        direccion_completa = direccion.get("direccion_completa")
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
        print (f"Respuesta sp_guarda_cliente_zoom: {res}")
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


def _persistir_envio_zoom(payload: dict):
    """Mapea el payload completo del proceso orquestado al SP sp_crear_envio_zoom."""
    
    try:
        # Extraer datos del payload
        resultados_previos = payload.get("resultados_previos", {})
        token_data = resultados_previos.get("token", {})
        envio_data = resultados_previos.get("envio", {})
        tarifas = resultados_previos.get("tarifas", {})
        
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
        
        # Obtener guía Zoom de la respuesta del envío
        entidad_respuesta = envio_data.get("entidadRespuesta", [{}])
        if isinstance(entidad_respuesta, list) and len(entidad_respuesta) > 0:
            id_guia_zoom = entidad_respuesta[0].get("numguia")
        else:
            id_guia_zoom = envio_data.get("entidadRespuesta", {}).get("numguia")
        
        # Si no hay guía en la respuesta, intentar del payload
        if not id_guia_zoom:
            id_guia_zoom = payload.get("_guia_zoom")
        
        # Obtener datos del destinatario guardado
        destinatario_guardado = resultados_previos.get("destinatario", {})
        remitente_id = resultados_previos.get("remitente")
        
        # Preparar argumentos para el stored procedure
        args = (
            # Cliente y empresa (asumimos valores por defecto si no están)
            _to_int(autenticacion.get("cliente_id"), 1),  # p_id_cliente
            1,  # p_id_empresa_envio (asumimos ZOOM=1)
            
            # Referencias
            metadata.get("solicitud_id"),  # p_referencia_interna
            payload.get("_token"),  # p_token_zoom
            payload.get("_certificado"),  # p_certificado_zoom
            _to_int(autenticacion.get("codigo_cliente"), 407940),  # p_codigo_cliente_zoom
            
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
            _to_int(paquete.get("numero_piezas"), 1),
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
            str(id_guia_zoom) if id_guia_zoom else "",  # p_id_guia_zoom
            
            # Backups (payload completo)
            json.dumps(payload, ensure_ascii=False, indent=2),  # p_payload_cab
            json.dumps(resultados_previos, ensure_ascii=False, indent=2),  # p_payload_track
            
            # Out params
            None,  # p_exito (OUT)
            None   # p_mensaje (OUT)
        )
        
        # Ejecutar stored procedure
        print (f"Args para sp_crear_envio_zoom: {args}")
        resultados = ejecutar_sp_resultados("sp_crear_envio_zoom", *args)
        print (f"Respuesta sp_crear_envio_zoom: {resultados}")
        
        # Si el stored procedure devuelve los out params, procesarlos
        if resultados and len(resultados) > 0:
            resultado_dict = resultados[0]
            p_exito = resultado_dict.get("p_exito", resultado_dict.get("P_EXITO"))
            p_mensaje = resultado_dict.get("p_mensaje", resultado_dict.get("P_MENSAJE"))
            
            return {
                "p_exito": p_exito if p_exito is not None else True,
                "p_mensaje": p_mensaje or "Envío guardado exitosamente",
                "resultado": resultados,
                "id_envio_cab": resultado_dict.get("id_envio_cab", resultado_dict.get("ID_ENVIO_CAB")),
                "id_guia_zoom": id_guia_zoom
            }
        else:
            return {
                "p_exito": True,
                "p_mensaje": "Envío procesado pero no se obtuvo confirmación de BD",
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
        
        # # Guardar token para uso posterior
        token = token_data.get("token")
        #print (f"Token obtenido: {token}")
        certificado = token_data.get("certificado")
        payload["_token"] = token
        payload["_certificado"] = certificado
        
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
            envio_creado = crear_envio_segun_tipo(cliente_zoom, payload, tipo_envio,token)
            guia_zoom = envio_creado.get("entidadRespuesta", [{}])[0].get("numguia")
            if not guia_zoom and (envio_creado.get("codrespuesta") != "CODE_001"):
                logger.error(f"Error creando envío: {envio_creado.get('error', 'Respuesta inesperada')}")   
                resultado["errores"].append(f"Error creando envío: {envio_creado['error']}")
                resultado["respuesta_final"]["envio"] = "Envío no creado"
                resultado["respuesta_final"]["guia_zoom"] = "Guía no generada"
                resultado["ok"] = False
            else:
                if debug: logger.info(f"Envío creado con éxito, guía Zoom: {guia_zoom}")
                #guia_zoom = envio_creado.get("entidadRespuesta", {}).get("numguia") 
                resultado["respuesta_final"]["envio"] = "Envío creado exitosamente"
                resultado["respuesta_final"]["guia_zoom"] = guia_zoom
                resultado["pasos_completados"].append("creacion_envio")
                #resultado["respuesta_final"]["guia_zoom"] = guia_zoom
            
            
            
            
        
        # # ===== PASO 8: OBTENER SEGUIMIENTO INMEDIATO =====
        if guia_zoom:
            try:
                tracking = cliente_zoom.obtener_ultimotrack(
                    codigo=guia_zoom,
                    codigo_cliente=payload["autenticacion_zoom"]["codigo_cliente"],
                    tipo_busqueda=1  # Por número de guía
                )
                #resultado["respuesta_final"]["tracking"] = tracking
                if tracking.get("codrespuesta", []) == "COD_000":
                    resultado["pasos_completados"].append("Tracking inicial")
                    if debug: logger.info(f"Seguimiento inicial obtenido para guía {guia_zoom}")
                else:
                    resultado["errores"].append("No se pudo obtener tracking inicial")
                    resultado["ok"] = False
                    logger.warning(f"No se pudo obtener seguimiento inicial para guía {guia_zoom}")
            except Exception as e:
                logger.error(f"Error obteniendo seguimiento inicial: {str(e)}")
                resultado["ok"] = False
        
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
            # agergamos todas lasresultados previos al payload para guardarlo todo junto
            payload["resultados_previos"] = {
               "token": token_data,
               "servicios_cliente": servicios_disponibles,
               "tarifas": tarifa_calculada,
               "remitente": remitente_id,
               "destinatario": destinatario,
               "guia": guia_zoom,
               "tracking": tracking,
               "etiqueta": etiqueta
            }
            #print (f"Payload final para BD: {payload}")
            db_cliente= _guardar_cliente_zoom(payload)
            if db_cliente:
                if debug: logger.info(f"Cliente guardado en BD con ID: {db_cliente}")
                db_envio = _persistir_envio_zoom(payload)
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
        
        #token = token_resp["entidadRespuesta"].get("token")        
        if isinstance(token_resp, dict) and token_resp["entidadRespuesta"].get("token"):
            token = token_resp["entidadRespuesta"].get("token")
            resultado["token"] = token
            if debug: logger.info(f"Token obtenido exitosamente para login: {login}, clave: {clave}")
        else:
            resultado["error"] = token_resp
            logger.error(f"Error obteniendo token: {token_resp}, no se procede. login: {login}, clave: {clave}")
            return resultado
    
        
        # 2. Obtener certificado (para envios internacionales o si se requiere)
        # no siempre es necesario y aun no existe en el payload requerido campo "requerir_certificado"
        if token and payload.get("configuracion_envio", {}).get("requerir_certificado", False):
            cert_resp = cliente.zoom_cert({
                "login": login,
                "password": clave,
                "token": token,
                "frase_privada": auth.get("frase_secreta", "")
            })
            if isinstance(cert_resp, dict) and "certificado" in cert_resp:
                resultado["certificado"] = cert_resp["certificado"]
            else:
                resultado["certificado"] = cert_resp
            logger.info(f"Certificado obtenido para los datos de login: {login} y clave: {clave}")
    
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


def crear_envio_segun_tipo(cliente: ClienteZoom, payload: dict, tipo_envio: str, token: str) -> dict:
    """Crea el envío según el tipo"""
    
    if tipo_envio == "nacional":
        return crear_envio_nacional(cliente, payload, token)
    elif tipo_envio in ["internacional", "casillero_aereo", "casillero_maritimo"]:
        return crear_envio_internacional(cliente, payload, tipo_envio)
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
    print (f"Datos para crear envío nacional: {envio_data}")
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


# -- ARMI
@bp_privadas.post("/armi/monitor/business/create")
@requerir_api_key(Delivery_Empresa="ARMI")
def crear_negocio_armi():
    payload = request.get_json(silent=True) or {}
    cliente = _cliente_Armi()
    data = cliente.crear_negocio(payload)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

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

