"""
Rutas públicas (catálogos, tracking, precios) – Español
------------------------------------------------------
"""
from flask import Blueprint, request, jsonify, current_app
from ..servicios.cliente_zoom import ClienteZoom
from ..configuracion import Configuracion

bp_publicas = Blueprint("publicas", __name__)


def _cliente() -> ClienteZoom:
    cfg = current_app.config
    return ClienteZoom(
        base_url=cfg["ZOOM_BASE_URL"],
        api_key=cfg.get("ZOOM_API_KEY", ""),
        frase_secreta=cfg.get("ZOOM_FRASE_SECRETA", ""),
        timeout=cfg.get("ZOOM_TIMEOUT", 10.0),
        reintentos=cfg.get("ZOOM_REINTENTOS", 3),
    )

@bp_publicas.get("/getInfoTracking")
def obtener_infotracking():
    tipo_busqueda = request.args.get("tipo_busqueda")
    codigo = request.args.get("codigo")
    codigo_cliente = request.args.get("codigo_cliente")
    cliente = _cliente()
    data = cliente.obtener_infotracking(tipo_busqueda=tipo_busqueda, codigo=codigo, codigo_cliente=codigo_cliente)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"tipo_busqueda": tipo_busqueda, "codigo": codigo, "codigo_cliente": codigo_cliente}})

@bp_publicas.get("/catalog/tipotarifa")
def obtener_tipotarifa():
    cliente = _cliente()
    data = cliente.obtener_infoTarifa()
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

@bp_publicas.get("/getModalidadTarifa")
def modalidad_tarifa():
    cliente = _cliente()
    data = cliente.obtener_modalidad_tarifa()
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

@bp_publicas.get("/catalog/ciudades")
def listar_ciudades():
    estado = request.args.get("estado")
    codestado = request.args.get("codestado")
    idioma = request.args.get("idioma")
    cliente = _cliente()
    data = cliente.obtener_ciudades(estado=estado, codestado=codestado, idioma=idioma)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"estado": estado, "codestado": codestado,"idioma": idioma}})

@bp_publicas.get("/getOficinas")
def obtener_oficinas():
    codciudad = request.args.get("codciudad")
    codservicio = request.args.get("codservicio")
    siglas = request.args.get("siglas")
    codpais = request.args.get("codpais")    
    cliente = _cliente()
    data = cliente.obtener_oficinas(codciudad=codciudad, codservicio=codservicio, siglas=siglas, codpais=codpais)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"codciudad": codciudad, "codservicio": codservicio, "siglas": siglas, "codpais": codpais}})

@bp_publicas.get("/getPaises")
def listar_paises():
    tipo = request.args.get("tipo")
    idioma = request.args.get("idioma")
    cliente = _cliente()
    data = cliente.obtener_paises(tipo=tipo, idioma=idioma)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"tipo": tipo, "idioma": idioma}})

@bp_publicas.get("/getTipoEnvio")
def listar_tipo_envio():
    cliente = _cliente()
    data = cliente.obtener_tipo_envio()
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

@bp_publicas.get("/CalcularTarifa")
def calcular_tarifa():
    tipo_tarifa = request.args.get("tipo_tarifa")
    modalidad_tarifa = request.args.get("modalidad_tarifa")
    ciudad_remitente = request.args.get("ciudad_remitente")
    ciudad_destinatario = request.args.get("ciudad_destinatario")
    oficina_retirar = request.args.get("oficina_retirar")
    cantidad_piezas = request.args.get("cantidad_piezas")
    peso = request.args.get("peso")
    valor_mercancia = request.args.get("valor_mercancia")
    valor_declarado = request.args.get("valor_declarado")
    cliente = _cliente()
    data = cliente.obtener_tarifa(tipo_tarifa=tipo_tarifa, modalidad_tarifa=modalidad_tarifa, ciudad_remitente=ciudad_remitente, ciudad_destinatario=ciudad_destinatario, oficina_retirar=oficina_retirar, cantidad_piezas=cantidad_piezas, peso=peso, valor_mercancia=valor_mercancia, valor_declarado=valor_declarado)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"tipo_tarifa": tipo_tarifa, "modalidad_tarifa": modalidad_tarifa, "ciudad_remitente": ciudad_remitente, "ciudad_destinatario": ciudad_destinatario, "oficina_retirar": oficina_retirar, "cantidad_piezas": cantidad_piezas, "peso": peso, "valor_mercancia": valor_mercancia, "valor_declarado": valor_declarado}})

@bp_publicas.get("/getZoomTrackWs")
def rastrear_envio():
    codigo = request.args.get("codigo")
    tipo_busqueda = request.args.get("tipo_busqueda")
    web = request.args.get("web")
    cliente = _cliente()
    data = cliente.obtener_trackws(codigo=codigo, tipo_busqueda=tipo_busqueda, web=web)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"codigo": codigo, "tipo_busqueda": tipo_busqueda, "web": web}})

@bp_publicas.get("/getlanguages")
def obtener_languages():
    cliente = _cliente()
    data = cliente.obtener_idiomas()
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

@bp_publicas.get("/getRespuestastags")
def obtener_rtags():
    id_language = request.args.get("id_language")
    codrespuesta = request.args.get("codrespuesta")
    cliente = _cliente()
    data = cliente.obtener_respuestastags(id_language=id_language, codrespuesta=codrespuesta)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"id_language": id_language, "codrespuesta": codrespuesta}})

@bp_publicas.get("/getLastTracking")
def obtener_lasttrack():
    tipo_busqueda = request.args.get("tipo_busqueda")
    codigo = request.args.get("codigo")
    codigo_cliente = request.args.get("codigo_cliente")
    cliente = _cliente()
    data = cliente.obtener_ultimotrack(tipo_busqueda=tipo_busqueda, codigo=codigo, codigo_cliente=codigo_cliente)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"tipo_busqueda": tipo_busqueda, "codigo": codigo, "codigo_cliente": codigo_cliente}})

@bp_publicas.get("/getMunicipios")
def listar_municipios():
    codciudad = request.args.get("codciudad")
    remitente = request.args.get("remitente")
    cliente = _cliente()
    data = cliente.obtener_municipios(codciudad=codciudad, remitente=remitente)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"codciudad": codciudad, "remitente": remitente}})

@bp_publicas.get("/getParroquias")
def listar_parroquias():
    codmunicipio = request.args.get("codmunicipio")
    codciudad = request.args.get("codciudad")
    remitente = request.args.get("remitente")
    cliente = _cliente()
    data = cliente.obtener_parroquias(codmunicipio=codmunicipio, codciudad=codciudad, remitente=remitente)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"codmunicipio": codmunicipio, "codciudad": codciudad, "remitente": remitente}})

@bp_publicas.get("/getOficinasGE")
def listar_oficinasGE():
    codigo_ciudad_destino = request.args.get("codigo_ciudad_destino")
    modalidad_tarifa = request.args.get("modalidad_tarifa")
    tipo_tarifa = request.args.get("tipo_tarifa")
    cliente = _cliente()
    data = cliente.obtener_oficinasGE(codigo_ciudad_destino=codigo_ciudad_destino, modalidad_tarifa=modalidad_tarifa, tipo_tarifa=tipo_tarifa)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"codigo_ciudad_destino": codigo_ciudad_destino, "modalidad_tarifa": modalidad_tarifa, "tipo_tarifa": tipo_tarifa}})

@bp_publicas.get("/getStatus")
def obtener_status():
    cliente = _cliente()
    data = cliente.obtener_status()
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

@bp_publicas.get("/getCiudadesOfi")
def obtener_ciudades_ofi():
    codestado = request.args.get("codestado")
    recolecta = request.args.get("recolecta")
    cliente = _cliente()
    data = cliente.obtener_ciudades_ofi(codestado=codestado, recolecta=recolecta)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"codestado": codestado}})

@bp_publicas.get("/getsucursales")
def obtener_sucursales():
    codciudad = request.args.get("codciudad")
    idioma = request.args.get("idioma")
    cliente = _cliente()
    data = cliente.obtener_sucursales(codciudad=codciudad, idioma=idioma)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"codciudad": codciudad, "idioma": idioma}})

@bp_publicas.get("/getTipoRutaEnvio")
def obtener_tipo_ruta_envio():
    codciudadori = request.args.get("codciudadori")
    codciudaddes = request.args.get("codciudaddes")
    cliente = _cliente()
    data = cliente.obtener_tipo_ruta_envio(codciudadori=codciudadori, codciudaddes=codciudaddes)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"codciudadori": codciudadori, "codciudaddes": codciudaddes}})

@bp_publicas.get("/getModalidadCod")
def obtener_modalidad_cod():
    cliente = _cliente()
    data = cliente.obtener_modalidad_cod()
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

@bp_publicas.get("/getEstados")
def listar_estados():
    filtro = request.args.get("filtro")
    cliente = _cliente()
    data = cliente.obtener_estados(filtro=filtro)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"filtro": filtro}})

@bp_publicas.get("/ConsultaPreciosWs")
def consulta_preciows():
    codciudad_origen = request.args.get("codciudad_origen")
    codciudad_destino = request.args.get("codciudad_destino")
    peso = request.args.get("peso")
    valor_declarado = request.args.get("valor_declarado")
    proteccion = request.args.get("proteccion")
    codigo_cliente = request.args.get("codigo_cliente")
    codservicio = request.args.get("codservicio")
    modalidad = request.args.get("modalidad")
    codoficina = request.args.get("codoficina")
    retirar_oficina = request.args.get("retirar_oficina")
    cliente = _cliente()
    data = cliente.obtener_consulta_preciows(codciudad_origen=codciudad_origen, codciudad_destino=codciudad_destino, peso=peso, 
                                             valor_declarado=valor_declarado, proteccion=proteccion, codigo_cliente=codigo_cliente, 
                                             codservicio=codservicio, modalidad=modalidad, codoficina=codoficina, retirar_oficina=retirar_oficina)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"codciudad_origen": codciudad_origen, "codciudad_destino": codciudad_destino, "peso": peso, 
                                                          "valor_declarado": valor_declarado, "proteccion": proteccion, "codigo_cliente": codigo_cliente, 
                                                          "codservicio": codservicio, "modalidad": modalidad, "codoficina": codoficina, "retirar_oficina": retirar_oficina}})

@bp_publicas.get("/getOficinaEstadoWs")
def listar_oficinasofi():
    codestado = request.args.get("codestado")
    cliente = _cliente()
    data = cliente.obtener_consulta_oficinaestadows(codestado=codestado)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"codestado": codestado}})

@bp_publicas.get("/getTipoPrecioWs")
def tipo_precio_ws():
    cliente = _cliente()
    data = cliente.obtener_tipopreciows()
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

#-----------------consultarPreciosWs
@bp_publicas.get("/consultarPreciosWs")
def consultar_precios_ws():
    tipo_precio = request.args.get("tipo_precio", type=int)
    cliente = _cliente()
    
    match tipo_precio:
        case 1,2:
            # COD=1 y Nacional=2
            tipo_tarifa = request.args.get("tipo_tarifa", type=int)
            modalidad_tarifa = request.args.get("modalidad_tarifa", type=int)
            ciudad_remitente = request.args.get("ciudad_remitente", type=int)
            ciudad_destinatario = request.args.get("ciudad_destinatario", type=int)
            oficina_retirar = request.args.get("oficina_retirar", type=int)
            cantidad_piezas = request.args.get("cantidad_piezas", type=int)
            peso = request.args.get("peso", type=float)
            valor_declarado = request.args.get("valor_declarado", type=float, default=0)
            data = cliente.consultar_precio_cod_nacional(
                tipo_precio,tipo_tarifa, modalidad_tarifa, ciudad_remitente, ciudad_destinatario,
                oficina_retirar, cantidad_piezas, peso, valor_declarado
            )
            
        case 3:
            # Internacional
            pesob = request.args.get("pesob", type=float)
            fecha_envio = request.args.get("fecha_envio")
            siglas_pd = request.args.get("siglas_pd")
            ciudad_d = request.args.get("ciudad_d")
            zipcode_d = request.args.get("zipcode_d")
            suburb_d = request.args.get("suburb_d")            
            siglas_po = request.args.get("siglas_po")
            ciudad_o = request.args.get("ciudad_o")
            zipcode_o = request.args.get("zipcode_o")
            suburb_o = request.args.get("suburb_o")            
            valor_declarado = request.args.get("valor_declarado", type=float)
            merdoc = request.args.get("merdoc")
            codciudadori = request.args.get("codciudadori", type=int)
            alto = request.args.get("alto", type=float)
            ancho = request.args.get("ancho", type=float)
            largo = request.args.get("largo", type=float)
            
            data = cliente.consultar_precio_internacional(
                pesob, fecha_envio, siglas_pd, ciudad_d, siglas_po, ciudad_o,
                valor_declarado, merdoc, codciudadori, alto, ancho, largo,
                zipcode_d, suburb_d, zipcode_o, suburb_o
            )
            
        case 4:
            # Casillero Internacional Áereo
            codpais_remitente = request.args.get("codpais_remitente", type=int)
            codpais_destinatario = request.args.get("codpais_destinatario", type=int)
            oficina_retirar = request.args.get("oficina_retirar", type=int)
            peso = request.args.get("peso", type=float)
            valor_mercancia = request.args.get("valor_mercancia", type=float, default=0)
            codtipoenv = request.args.get("codtipoenv", type=int, default=1)
            codservicio = request.args.get("codservicio", type=int, default=0)
            ciudad_destinatario = request.args.get("ciudad_destinatario", type=int)
            data = cliente.consultar_precio_casillero_aereo(
                codpais_remitente, codpais_destinatario, oficina_retirar, peso,
                valor_mercancia, codtipoenv, codservicio, ciudad_destinatario
            )
            if data.get("error"):
                return jsonify({"ok": False, "error": data.get("error")}), 400
            return jsonify({"ok": True, "data": data})
        case 5:
            # Casillero Internacional Marítimo
            codpais_remitente = request.args.get("codpais_remitente", type=int)
            codpais_destinatario = request.args.get("codpais_destinatario", type=int)
            oficina_retirar = request.args.get("oficina_retirar", type=int)
            peso = request.args.get("peso", type=float)
            valor_mercancia = request.args.get("valor_mercancia", type=float, default=0)
            codtipoenv = request.args.get("codtipoenv", type=int, default=1)
            codservicio = request.args.get("codservicio", type=int, default=0)
            ciudad_destinatario = request.args.get("ciudad_destinatario", type=int)
            alto = request.args.get("alto", type=float)
            ancho = request.args.get("ancho", type=float)
            largo = request.args.get("largo", type=float)
            data = cliente.consultar_precio_casillero_maritimo(
                codpais_remitente, codpais_destinatario, oficina_retirar, peso,
                valor_mercancia, codtipoenv, codservicio, ciudad_destinatario,
                alto, ancho, largo
            )
            
        case 6:
            # Venta de Divisas Envío Internacional WU
            monto = request.args.get("monto", type=float)            
            data = cliente.consultar_precio_venta_divisas_internacional(monto)
            
        case 7:
            # Compra de Divisas en Efectivo
            monto = request.args.get("monto", type=float)            
            data = cliente.consultar_precio_compra_divisas_efectivo(monto)
            
        case 8:
            # Venta en Divisas en Efectivo
            monto = request.args.get("monto", type=float)            
            data = cliente.consultar_precio_venta_divisas_efectivo(monto)
            
        case _:
            data.error = "tipo_precio no soportado"
                    
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})
#-----------------consultarPreciosWs
@bp_publicas.get("/consultaTrackingWs")
def consulta_trackingws():
    tipo_busqueda = request.args.get("tipo_busqueda")
    numero=request.args.get("numero")
    web=request.args.get("web")    
    cliente = _cliente()
    data = cliente.obtener_consulta_trackingws(tipo_busqueda=tipo_busqueda, numero=numero, web=web)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"tipo_busqueda": tipo_busqueda, "numero": numero, "web": web}})

@bp_publicas.get("/zonasNoServidasWs")
def zonas_no_servidasws():
    codciudad = request.args.get("codciudad")
    cliente = _cliente()
    data = cliente.obtener_zonas_noservidasws(codciudad=codciudad)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"codciudad": codciudad}})

@bp_publicas.get("/getTipoDocumento")
def tipo_documento():
    cliente = _cliente()
    data = cliente.obtener_tipo_documento()
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

@bp_publicas.get("/listadoGenericoCiudades")
def listado_generico_ciudades():
    cliente = _cliente()
    data = cliente.obtener_listado_generico_ciudades()
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

@bp_publicas.get("/getCiudadesWs")
def listar_ciudadesws():
    tipoEntrega = request.args.get("tipoEntrega", type=int)
    cliente = _cliente()
    data = cliente.obtener_ciudadesws(tipoEntrega=tipoEntrega)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

#------------------------------ armi -----------------------------












