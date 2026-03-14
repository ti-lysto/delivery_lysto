from flask import Blueprint, request, jsonify, current_app
from ..servicios.cliente_zoom import ClienteZoom

bp_publicas = Blueprint("publicas", __name__)


def _arg_str(name: str, required: bool = False) -> str | None:
    value = request.args.get(name)
    if required and not value:
        raise ValueError(f"{name} es requerido")
    return value


def _arg_int(name: str, required: bool = False) -> int | None:
    raw = request.args.get(name)
    if raw is None or raw == "":
        if required:
            raise ValueError(f"{name} es requerido")
        return None
    try:
        return int(raw)
    except Exception as exc:
        raise ValueError(f"{name} debe ser entero") from exc


def _arg_float(name: str, required: bool = False) -> float | None:
    raw = request.args.get(name)
    if raw is None or raw == "":
        if required:
            raise ValueError(f"{name} es requerido")
        return None
    try:
        return float(raw)
    except Exception as exc:
        raise ValueError(f"{name} debe ser numérico") from exc


def _arg_bool(name: str, required: bool = False) -> bool | None:
    raw = request.args.get(name)
    if raw is None or raw == "":
        if required:
            raise ValueError(f"{name} es requerido")
        return None
    value = raw.strip().lower()
    if value in ("1", "true", "t", "yes", "y", "si", "sí"):
        return True
    if value in ("0", "false", "f", "no", "n"):
        return False
    raise ValueError(f"{name} debe ser booleano")


def _req_str(name: str) -> str:
    value = _arg_str(name, required=True)
    if value is None:
        raise ValueError(f"{name} es requerido")
    return value


def _req_int(name: str) -> int:
    value = _arg_int(name, required=True)
    if value is None:
        raise ValueError(f"{name} es requerido")
    return value


def _req_float(name: str) -> float:
    value = _arg_float(name, required=True)
    if value is None:
        raise ValueError(f"{name} es requerido")
    return value


def _req_bool(name: str) -> bool:
    value = _arg_bool(name, required=True)
    if value is None:
        raise ValueError(f"{name} es requerido")
    return value


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
    try:
        tipo_busqueda = _arg_int("tipo_busqueda")
        codigo = _req_str("codigo")
        codigo_cliente = _req_int("codigo_cliente")
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    cliente = _cliente()
    data = cliente.obtener_infotracking(tipo_busqueda=tipo_busqueda, codigo=codigo, codigo_cliente=codigo_cliente)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"tipo_busqueda": tipo_busqueda, "codigo": codigo, "codigo_cliente": codigo_cliente}})

@bp_publicas.get("/getTipoTarifa")
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

@bp_publicas.get("/getCiudades")
def listar_ciudades():
    codestado_str = request.args.get("codestado")
    filtro = request.args.get("filtro")
    idioma = request.args.get("idioma")

    if not codestado_str or not codestado_str.isdigit():
        return jsonify({"ok": False, "error": "codestado debe ser un número entero válido"}), 400

    codestado = int(codestado_str)
    cliente = _cliente()

    try:
        data = cliente.obtener_ciudades(codestado=codestado, filtro=filtro, idioma=int(idioma) if idioma and idioma.isdigit() else None)
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

    return jsonify({"ciudades": data})

@bp_publicas.get("/getOficinas")
def obtener_oficinas():
    try:
        codciudad = _req_str("codciudad")
        codservicio = _req_int("codservicio")
        codpais = _arg_int("codpais")
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    siglas = request.args.get("siglas")
    cliente = _cliente()
    data = cliente.obtener_oficinas(codciudad=codciudad, codservicio=codservicio, siglas=siglas, codpais=codpais or 0)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"codciudad": codciudad, "codservicio": codservicio, "siglas": siglas, "codpais": codpais}})

@bp_publicas.get("/getPaises")
def listar_paises():
    try:
        tipo = _req_int("tipo")
        idioma = _arg_int("idioma")
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
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
    try:
        tipo_tarifa = _arg_int("tipo_tarifa")
        modalidad_tarifa = _arg_int("modalidad_tarifa")
        ciudad_remitente = _arg_int("ciudad_remitente")
        ciudad_destinatario = _arg_int("ciudad_destinatario")
        oficina_retirar = _arg_int("oficina_retirar")
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
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
    try:
        codigo = _req_str("codigo")
        tipo_busqueda = _req_int("tipo_busqueda")
        web = _arg_int("web")
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
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
    try:
        id_language = _arg_int("id_language")
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    codrespuesta = request.args.get("codrespuesta")
    cliente = _cliente()
    data = cliente.obtener_respuestastags(id_language=id_language, codrespuesta=codrespuesta)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"id_language": id_language, "codrespuesta": codrespuesta}})

@bp_publicas.get("/getLastTracking")
def obtener_lasttrack():
    try:
        tipo_busqueda = _arg_int("tipo_busqueda")
        codigo = _req_str("codigo")
        codigo_cliente = _req_int("codigo_cliente")
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    cliente = _cliente()
    data = cliente.obtener_ultimotrack(tipo_busqueda=tipo_busqueda, codigo=codigo, codigo_cliente=codigo_cliente)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"tipo_busqueda": tipo_busqueda, "codigo": codigo, "codigo_cliente": codigo_cliente}})

@bp_publicas.get("/getMunicipios")
def listar_municipios():
    try:
        codciudad = _req_int("codciudad")
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    remitente = request.args.get("remitente")
    cliente = _cliente()
    data = cliente.obtener_municipios(codciudad=codciudad, remitente=remitente)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"codciudad": codciudad, "remitente": remitente}})

@bp_publicas.get("/getParroquias")
def listar_parroquias():
    try:
        codmunicipio = _req_int("codmunicipio")
        codciudad = _req_int("codciudad")
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    remitente = request.args.get("remitente")
    cliente = _cliente()
    data = cliente.obtener_parroquias(codmunicipio=codmunicipio, codciudad=codciudad, remitente=remitente)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"codmunicipio": codmunicipio, "codciudad": codciudad, "remitente": remitente}})

@bp_publicas.get("/getOficinasGE")
def listar_oficinasGE():
    try:
        codigo_ciudad_destino = _req_int("codigo_ciudad_destino")
        modalidad_tarifa = _arg_int("modalidad_tarifa")
        tipo_tarifa = _arg_int("tipo_tarifa")
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    cliente = _cliente()
    data = cliente.obtener_oficinasGE(codigo_ciudad_destino=codigo_ciudad_destino, modalidad_tarifa=modalidad_tarifa, tipo_tarifa=tipo_tarifa)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"codigo_ciudad_destino": codigo_ciudad_destino, "modalidad_tarifa": modalidad_tarifa, "tipo_tarifa": tipo_tarifa}})

@bp_publicas.get("/getEstatus")
def obtener_status():
    cliente = _cliente()
    data = cliente.obtener_status()
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

@bp_publicas.get("/getCiudadesOfi")
def obtener_ciudades_ofi():
    try:
        codestado = _req_str("codestado")
        recolecta = _arg_int("recolecta")
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    cliente = _cliente()
    data = cliente.obtener_ciudades_ofi(codestado=codestado, recolecta=recolecta)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"codestado": codestado}})

@bp_publicas.get("/getSucursales")
def obtener_sucursales():
    try:
        codciudad = _req_int("codciudad")
        idioma = _arg_int("idioma")
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    cliente = _cliente()
    data = cliente.obtener_sucursales(codciudad=codciudad, idioma=idioma)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"codciudad": codciudad, "idioma": idioma}})

@bp_publicas.get("/getTipoRutaEnvio")
def obtener_tipo_ruta_envio():
    try:
        codciudadori = _req_int("codciudadori")
        codciudaddes = _req_int("codciudaddes")
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
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
    filtro = request.args.get("filtro", "124")  # 124 es Venezuela
    cliente = _cliente()
    data = cliente.obtener_estados(filtro=filtro)

    # Si la respuesta es una lista, no tiene .get()
    if isinstance(data, list):
        # Asumimos que no hay error si es una lista válida
        return jsonify({"ok": True, "data": data, "params": {"filtro": filtro}})

    # Si es un diccionario, verifica si hay error
    if isinstance(data, dict) and data.get("error"):
        return jsonify({"ok": False, "error": data["error"]}), 400

    # Si es un dict pero sin error, envíalo como data
    return jsonify({"ok": True, "data": data, "params": {"filtro": filtro}})

@bp_publicas.get("/ConsultaPreciosWs")
def consulta_preciows():
    try:
        codciudad_origen = _req_int("codciudad_origen")
        codciudad_destino = _req_int("codciudad_destino")
        peso = _req_float("peso")
        valor_declarado = _req_float("valor_declarado")
        proteccion = _req_bool("proteccion")
        codigo_cliente = _req_int("codigo_cliente")
        codservicio = _req_int("codservicio")
        modalidad = _req_int("modalidad")
        codoficina = _req_int("codoficina")
        retirar_oficina = _req_bool("retirar_oficina")
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
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
    try:
        codestado = _req_int("codestado")
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
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
    try:
        
        tipo_precio_raw = request.args.get("tipo_precio")
        
        if tipo_precio_raw is None:
            return jsonify({"ok": False, "error": "tipo_precio es requerido y debe ser entero"}), 400
        tipo_precio = int(tipo_precio_raw)
        print(f"tipo_precio recibido: {tipo_precio} ({type(tipo_precio)})")
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "tipo_precio es requerido y debe ser entero"}), 400
    cliente = _cliente()
    #try:
        
    match tipo_precio:
        case 1,2:
            # COD=1 y Nacional=2
            tipo_tarifa = _req_int("tipo_tarifa")
            modalidad_tarifa = _req_int("modalidad_tarifa")
            ciudad_remitente = _req_int("ciudad_remitente")
            ciudad_destinatario = _req_int("ciudad_destinatario")
            oficina_retirar = _req_int("oficina_retirar")
            cantidad_piezas = _req_int("cantidad_piezas")
            peso = _req_float("peso")
            valor_declarado = request.args.get("valor_declarado", type=float, default=0)
            data = cliente.consultar_precio_cod_nacional(
                tipo_precio, tipo_tarifa, modalidad_tarifa, ciudad_remitente, ciudad_destinatario,
                oficina_retirar, cantidad_piezas, peso, valor_declarado
            )
        
        case 3:
            # Internacional
            pesob = _req_float("pesob")
            fecha_envio = _req_str("fecha_envio")
            siglas_pd = _req_str("siglas_pd")
            ciudad_d = _req_str("ciudad_d")
            zipcode_d = request.args.get("zipcode_d")
            suburb_d = request.args.get("suburb_d")
            siglas_po = _req_str("siglas_po")
            ciudad_o = _req_str("ciudad_o")
            zipcode_o = request.args.get("zipcode_o")
            suburb_o = request.args.get("suburb_o")
            valor_declarado = _req_float("valor_declarado")
            merdoc = _req_str("merdoc")
            codciudadori = _req_int("codciudadori")
            alto = _req_float("alto")
            ancho = _req_float("ancho")
            largo = _req_float("largo")

            data = cliente.consultar_precio_internacional(
                pesob, fecha_envio, siglas_pd, ciudad_d, siglas_po, ciudad_o,
                valor_declarado, merdoc, codciudadori, alto, ancho, largo,
                zipcode_d, suburb_d, zipcode_o, suburb_o
            )
        
        case 4:
            # Casillero Internacional Áereo
            codpais_remitente = _req_int("codpais_remitente")
            codpais_destinatario = _req_int("codpais_destinatario")
            oficina_retirar = _req_int("oficina_retirar")
            peso = _req_float("peso")
            valor_mercancia = request.args.get("valor_mercancia", type=float, default=0)
            codtipoenv = request.args.get("codtipoenv", type=int, default=1)
            codservicio = request.args.get("codservicio", type=int, default=0)
            ciudad_destinatario = request.args.get("ciudad_destinatario", type=int)
            data = cliente.consultar_precio_casillero_aereo(
                codpais_remitente, codpais_destinatario, oficina_retirar, peso,
                valor_mercancia, codtipoenv, codservicio, ciudad_destinatario
            )
        case 5:
            # Casillero Internacional Marítimo
            codpais_remitente = _req_int("codpais_remitente")
            codpais_destinatario = _req_int("codpais_destinatario")
            oficina_retirar = _req_int("oficina_retirar")
            peso = _req_float("peso")
            valor_mercancia = request.args.get("valor_mercancia", type=float, default=0)
            codtipoenv = request.args.get("codtipoenv", type=int, default=1)
            codservicio = request.args.get("codservicio", type=int, default=0)
            ciudad_destinatario = request.args.get("ciudad_destinatario", type=int)
            alto = _req_float("alto")
            ancho = _req_float("ancho")
            largo = _req_float("largo")
            data = cliente.consultar_precio_casillero_maritimo(
                codpais_remitente, codpais_destinatario, oficina_retirar, peso,
                valor_mercancia, codtipoenv, codservicio, ciudad_destinatario,
                alto, ancho, largo
            )
        
        case 6:
            # Venta de Divisas Envío Internacional WU
            monto = _req_float("monto")
            data = cliente.consultar_precio_venta_divisas_internacional(monto)
        
        case 7:
            # Compra de Divisas en Efectivo
            monto = _req_float("monto")
            data = cliente.consultar_precio_compra_divisas_efectivo(monto)
        
        case 8:
            # Venta en Divisas en Efectivo
            monto = _req_float("monto")
            data = cliente.consultar_precio_venta_divisas_efectivo(monto)
        
        case _:
            return jsonify({"ok": False, "error": "tipo_precio no soportado"}), 400
    # except ValueError as e:
    #     return jsonify({"ok": False, "error": str(e)}), 400
    # 
    # if data.get("error"):
    #     return jsonify({"ok": False, "error": data.get("error")}), 400
    # return jsonify({"ok": True, "data": data})
#-----------------consultarPreciosWs
@bp_publicas.get("/consultaTrackingWs")
def consulta_trackingws():
    try:
        tipo_busqueda = _req_int("tipo_busqueda")
        numero = _req_str("numero")
        web = _req_bool("web")
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    cliente = _cliente()
    data = cliente.obtener_consulta_trackingws(tipo_busqueda=tipo_busqueda, numero=numero, web=web)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data, "params": {"tipo_busqueda": tipo_busqueda, "numero": numero, "web": web}})

@bp_publicas.get("/zonasNoServidasWs")
def zonas_no_servidasws():
    try:
        codciudad = _req_int("codciudad")
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
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
    if tipoEntrega is None:
        return jsonify({"ok": False, "error": "tipoEntrega es requerido y debe ser entero"}), 400
    cliente = _cliente()
    data = cliente.obtener_ciudadesws(tipoEntrega=tipoEntrega)
    if data.get("error"):
        return jsonify({"ok": False, "error": data.get("error")}), 400
    return jsonify({"ok": True, "data": data})

#------------------------------ armi -----------------------------












