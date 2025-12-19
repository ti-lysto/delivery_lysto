#!/usr/bin/env python3
"""
Script simple para probar endpoints de la API local.

Uso:
    python test_endpoints.py --base http://localhost:8000 --api-key TU_KEY

Requiere: httpx (se instala con requirements de zoom_api)
"""
import argparse
import json
import os
import sys
import httpx

# Variables configurables para pruebas más realistas (usar export en shell)
ESTADO_COD = "25"
CIUDAD_COD = os.getenv("CIUDAD_COD", "EXAMPLE_CIUDAD")
MUNICIPIO_COD = os.getenv("MUNICIPIO_COD", "EXAMPLE_MUNICIPIO")


def probar_get(cliente: httpx.Client, ruta: str, parametros: dict | None = None):
    # Construir URL para mostrar
    url_para_mostrar = f"{cliente.base_url}{ruta}"
    if parametros:
        url_para_mostrar += "?" + "&".join(f"{k}={v}" for k, v in parametros.items())
    
    print(f"🔍 URL: {url_para_mostrar}")
    
    # Hacer la solicitud REAL con los parámetros
    if parametros:
        r = cliente.get(ruta, params=parametros)  # ✅ CORRECCIÓN: Pasar parámetros aquí
    else:
        r = cliente.get(ruta)
    
    print(f"📡 Status: {r.status_code}")
    try:
        respuesta = r.json()
        print("📄 Respuesta JSON:")
        print(json.dumps(respuesta, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"❌ Error JSON: {e}")
        print(f"📄 Respuesta texto: {r.text[:500]}")
    print("-" * 60)


def probar_post(cliente: httpx.Client, ruta: str, body: dict, api_key: str | None):
    url = f"{cliente.base_url}{ruta}"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    r = cliente.post(ruta, json=body, headers=headers)
    print(f"POST {url} -> {r.status_code}")
    try:
        print(json.dumps(r.json(), ensure_ascii=False, indent=2)[:800])
    except Exception:
        print(r.text[:800])
    print("-" * 60)


def main():
    
    p = argparse.ArgumentParser()
    p.add_argument("--base", default=os.getenv("ZOOM_BASE_URL", "http://localhost:8000"))
    p.add_argument("--api-key", default=os.getenv("ZOOM_API_KEY"))
    args = p.parse_args()
    key= "api_key_zoom"#os.getenv("ZOOM_API_KEY")""

    with httpx.Client(base_url=args.base, timeout=15.0) as c:
        # Salud e info
        print (os.getenv("ZOOM_BASE_URL"))
        print (args.base)
        print (key)#(args.api_key)
        print (os.getenv("ZOOM_API_KEY"))
        print (os.getenv("ZOOM_RUTA_CREAR_CLIENTE"))

        # probar_get(c, "/health")
        
        # params_info_tracking = {
        #     "tipo_busqueda": "1",
        #     "codigo": "71090585", 
        #     "codigo_cliente": "407940"
        # }
        # probar_get(c, "/api/getInfoTracking?tipo_busqueda=1&codigo=71090585&codigo_cliente=407940",params_info_tracking)
        # Rutas públicas correctas van bajo "/api" en tu app
        probar_get(c, "/api/catalog/tipotarifa") 
        # probar_get(c, "/api/getModalidadTarifa")
        # # Ciudades: admite estado o codestado (probamos ambos si se desea)
        # params = {"codestado": 25}
        # probar_get(c, "/api/ciudades", params)
        # params = {
        #     "codciudad": "19",
        #     "codservicio": "1"
        # }
        # probar_get(c, "/api/getOficinas",params)
        # params = {"tipo":"1"}
        # probar_get(c, "/api/getPaises", params)
        
        

        # params={"tipo_tarifa": "1","modalidad_tarifa": "2","ciudad_remitente": "1","ciudad_destinatario": "19","oficina_retirar": "46","cantidad_piezas": "5","peso": "10","valor_mercancia": "1000","valor_declarado": "2500"}
        # probar_get(c, "/api/CalcularTarifa",params)

        # params={"codigo": "1301902812","tipo_busqueda": "1","web": "1"}
        # probar_get(c, "/api/getZoomTrackWs",params)
        # probar_get(c, "/api/getlanguages")
        # params={"id_language": "1","codrespuesta": "CODE_003"}
        # probar_get(c, "/api/getRespuestastags",params)
        # params={"tipo_busqueda": "1","codigo": "71090585", "codigo_cliente": "407940"}
        # probar_get(c, "/api/getLastTracking",params)
        # params={"codciudad": "14"}
        # probar_get(c, "/api/getMunicipios",params)
        # params={"codmunicipio": "15", "codciudad": "16"}
        # probar_get(c, "/api/getParroquias",params)
        # params={"codigo_ciudad_destino": "16"}
        # probar_get(c, "/api/getOficinasGE",params)
        # probar_get(c, "/api/getStatus")
        # params={"codestado": "3"}
        # probar_get(c, "/api/getCiudadesOfi",params)
        # params={"codciudad": "12", "idioma": "2"}
        # probar_get(c, "/api/getsucursales",params)
        # params={"codciudadori": "12", "codciudaddes": "15"}
        # probar_get(c, "/api/getTipoRutaEnvio",params)
        # probar_get(c, "/api/getModalidadCod")
        # params={"filtro": "3"}
        # probar_get(c, "/api/getEstados",params)
        # params={"codciudad_origen": "12", "codciudad_destino": "19", "peso": "0.5", "valor_declarado": "30373", "codigo_cliente": "100000817", "proteccion": "1", "codservicio": "1", "modalidad": "1", "codoficina": "46", "retirar_oficina": "1"}
        # probar_get(c, "/api/ConsultaPreciosWs",params)
        # params={"codestado": "8"}
        # probar_get(c, "/api/getOficinaEstadoWs",params)
        # params={"tipo_precio": "1","tipo_tarifa": "1","modalidad_tarifa": "1","ciudad_remitente": "19","ciudad_destinatario": "4","oficina_retirar": "136","cantidad_piezas": "1","peso": "1","valor_mercancia": "0","valor_declarado": "125","tipo_envio": "1"}
        # probar_get(c, "/api/getTipoPrecioWs")
        
        
        # params={"tipo_busqueda": "1", "numero": "1000242115", "web": "1"}
        # probar_get(c, "/api/consultaTrackingWs", params)
        # params={"codciudad": "19"}
        # probar_get(c, "/api/zonasNoServidasWs", params)

        
        



        # # Endpoints privados (siempre se prueban, con o sin API key)
        # print("\n--- Pruebas de endpoints privados ---\n")
        # probar_post(c, "/privadas/clientes", {
        #     "nombre": "Ejemplo Cliente",
        #     "documento": "V-12345678",
        #     "telefono": "04141234567",
        #     "direccion": "Calle Falsa 123"
        # }, args.api_key)

        # probar_post(c, "/privadas/envios", {
        #     "origen": "Ciudad A",
        #     "destino": "Ciudad B",
        #     "remitente": "Ejemplo Cliente",
        #     "destinatario": "Cliente Destino",
        #     "peso": 1.5
        # }, args.api_key)

        # probar_post(c, "/privadas/envios/EXAMPLEGUIA/imprimir", {
        #     "formato": "PDF"
        # }, args.api_key)

        # probar_post(c, "/privadas/crearClienteWs", {
        #     "nombre": "Cliente WS",
        #     "documento": "J-98765432",
        #     "telefono": "04140000000",
        #     "direccion": "Av. Principal 456"
        # }, args.api_key)

        # probar_post(c, "/privadas/crearToken", {
        #     "login": "1",
        #     "clave": "456789"
        # }, args.api_key)

        # probar_post(c, "/privadas/zoomCert", {
        #     "login": "1",
        #     "password": "456789",
        #     "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjE1NjMsInBhc3N3b3JkIjoiNDU2Nzg5IiwiaXNzIjoiaHR0cHM6Ly9zYW5kYm94Lnpvb20ucmVkL2JhYXN6b29tL3B1YmxpYy9ndWlhZWxlY3Ryb25pY2EvZ2VuZXJhclRva2VuIiwiaWF0IjoxNzI0Njg2MDMwLCJleHAiOjE3MjQ2OTMyMzAsIm5iZiI6MTcyNDY4NjAzMCwianRpIjoiYmJpbTB1VEFUaDRqcGVZbiJ9.pVSVBRcYq4MDJvFhPQ70nsaJ5TY3sm6hGOZ57xe3sDU",
        #     "frase_privada": "RH0sVTL9za7O6gutqI43"
        # }, args.api_key)

        # probar_post(c, "/privadas/createShipmentInternacional", {
        #     "login": "513307",
        #     "clave": "456789",
        #     "certificado": "$1$VZ3pDjRN$UneSGUXyLtIm4i2fMoKfH.",
        #     "codservicio": 3,
        #     "codoficinaori": 253,
        #     "remitente": "Hola Express C.A",
        #     "contacto_remitente": "Carmen Gonzalez",
        #     "telefono_remitente": "0053-1472587",
        #     "direccion_remitente": "Calle ana, casa N° 45, Urbanización los cedros de prados del este. Valle del Cauca, Colombia",
        #     "codpaisdes": 124,
        #     "ciudaddes": "valencia",
        #     "destinatario": "YESICA GONCALVES",
        #     "contacto_destino": "YESICA GONCALVES",
        #     "rif_ci_destinatario": "2021154",
        #     "telefono_destino": "0055-123456789",
        #     "direcciondes": "Calle la colina, edificio Don Julio, piso 1, apto 1-A, Urbanización la floresta, Guayaquil, Ecuador",
        #     "tipo_envio": "M",
        #     "numero_piezas": 1,
        #     "peso_bruto": 1,
        #     "valor_declarado": 11,
        #     "alto": 11,
        #     "ancho": 11,
        #     "largo": 11,
        #     "descripcion_contenido": "Prueba de Servicio Web",
        #     "web_services": 1,
        #     "retira_oficina": 1,
        #     "codoficinades": 136,
        #     "seguro": 1
        # }, args.api_key)

        # probar_post(c, "/privadas/etiquetaTermica", {
        #     "codguia": ["1000809676"],
        #     "termicaPdf": "1",
        #     "terminos": "1"
        # }, args.api_key)

        # probar_post(c, "/privadas/crearRecolectaWs", {
        #     "codclientePpal": 1,
        #     "clave": "456789",
        #     "nombreContacto": "TECNOLOGICA NACIONAL DE TUS COSAS C.A",
        #     "personaContacto": "CARLOS PEREZ",
        #     "documentoIdentidad": "V-20175578",
        #     "celular": "04125887034",
        #     "telefono": "02122410789",
        #     "codestado": 2,
        #     "codciudad": 19,
        #     "direccion": "CALLE 13, EDIFICIO LAS VILLAS, PISO 10 APTO 10-13",
        #     "urbanizacion": "LA FLORIDA",
        #     "fechaRecolecta": "18-11-2025",
        #     "tipoVeh": 1,
        #     "tipoServicio": 1,
        #     "codcasillero": "",
        #     "tipoEnvio": "M",
        #     "cantidadPiezas": 1,
        #     "peso": 0.9,
        #     "contenido": "FRANELAS",
        #     "observacion": "PRUEBA DE RECOLECTA"
        # }, args.api_key)

        # probar_post(c, "/privadas/serviciosClientes", {
        #     "login": "1",
        #     "codusuario": 1563,
        #     "codclienteweb": 4,
        #     "codserviciofin": 1,
        #     "nombre": "COD NACIONAL"
        # }, args.api_key)

        # === Envío orquestado (graba en BD + etiqueta opcional) ===
        # probar_post(c, "/privadas/delivery/zoom/envio", {
        #     "solicitar_token": True,
        #     "login_zoom": "1",
        #     "clave_zoom": "456789",
        #     "codservicio": "1",
        #     "remitente": "HIRIBIN GIL",
        #     "contacto_remitente": "HIRIBIN GIL",
        #     "codciudadrem": "44",
        #     "tiporifcirem": "V-",
        #     "cirifrem": "20152013",
        #     "codmunicipiorem": "1303",
        #     "codparroquiarem": "130310",
        #     "zona_postal_remitente": "3009",
        #     "telefono_remitente": "04245163971",
        #     "codcelurem": "",
        #     "celularrem": "",
        #     "direccion_remitente": "42 ENTRE 26 Y 27",
        #     "inmueble_remitente": " DMS REPUESTOS ",
        #     "retira_oficina": "1",
        #     "codciudaddes": "12",
        #     "codmunicipiodes": "1114",
        #     "codparroquiades": "",
        #     "zona_postal_destino": "",
        #     "codoficinades": "59",
        #     "destinatario": "GABRIEL DIAZ",
        #     "contacto_destino": "GABRIEL DIAZ",
        #     "tiporifcidest": "V-",
        #     "cirif_destinatario": "18769615",
        #     "codceludest": "0414",
        #     "celular": "6813148",
        #     "telefono_destino": "00000000000",
        #     "direccion_destino": "SECTOR LOS TRES PLATOS, AV. LOS MEDANOS CRUCE CON AV. INDEPENDENCIA, EDIFICIO AREF, PB., LOCAL 1.",
        #     "inmueble_destino": "",
        #     "descripcion_contenido": "MERCANCIA",
        #     "referencia": "PA-PRUEBA-ENVIO",
        #     "campo1": "123456",
        #     "campo2": "12345645",
        #     "campo3": "QEDDFSD456154",
        #     "numero_piezas": "1",
        #     "peso_bruto": "1.02",
        #     "tipo_envio": "M",
        #     "valor_declarado": "3000",
        #     "seguro": "1",
        #     "valor_mercancia": "0",
        #     "modalidad_cod": "1",
        #     "web_services": "1",
        #     "emitir_etiqueta": True
        # }, args.api_key)

        # probar_post(c, "/privadas/GuardarRemitenteWs", {
        #     "codigo_oficina": "46",
        #     "nombre_remitente": "DENIS RAMIREZ",
        #     "cirif": "V-20175579",
        #     "contacto_remitente": "DENIS RAMIREZ",
        #     "direccion_remitente": "CALLE 3A URBANIZACIÓN LA URBINA",
        #     "ciudad_remitente": "19",
        #     "telefono_remitente": "0412-5887034",
        #     "observacion": "REMITENTE GUARDADO",
        #     "codigo_usuario": "2222",
        #     "parroquia_remitente": "101010",
        #     "municipio_remitente": "1010",
        #     "codpostal_remitente": "1010",
        #     "ciudad_ipostel": "152",
        #     "inmueble_remitente": "EDIFICIO DON PASQUALES PISO PB, APTO 10-80",
        #     "celular_remitente": "0412-5887034"
        # }, args.api_key)

        # probar_post(c, "/privadas/GuardarDestinatariosWs", {
        #     "codigo_usuario": "1563",
        #     "nombre_destinatario": "JOHAN FRANCO",
        #     "direccion_destino": "CUMBRES DE CURUMO",
        #     "contacto_destinatario": "DENIS RAMIREZ",
        #     "cirif_destinatario": "V-20175579",
        #     "telefono_destinatario": "04125887034",
        #     "fax_destinatario": "04125887034",
        #     "email_destinatario": "denisramirez@gmail.com",
        #     "codciudad_destino": "6",
        #     "codpais_destino": "124",
        #     "ciudad_destinoint": "MARACAIBO",
        #     "referencia": "OBJETOS",
        #     "municipio_destino": "2001",
        #     "parroquia_destino": "200100",
        #     "codpostal_destino": "200100",
        #     "ciudad_ipostel": "MARACAIBO",
        #     "estado_destino": "ZULIA",
        #     "inmueble_destinatario": "CASA N45",
        #     "celular_destinatario": "04125887034"
        # }, args.api_key)

        # # ...existing code...

        # # ------------------- ENDPOINTS PÚBLICOS POST (comentados, solo existen en /privadas/) -------------------

        # # Endpoints privados deben usar /privadas/ y pasar api_key
        # probar_post(c, "/privadas/crearToken", {
        #     "login": "1",
        #     "clave": "456789"
        # }, args.api_key)

        # probar_post(c, "/privadas/zoomCert", {
        #     "login": "1",
        #     "password": "456789",
        #     "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOjE1NjMsInBhc3N3b3JkIjoiNDU2Nzg5IiwiaXNzIjoiaHR0cHM6Ly9zYW5kYm94Lnpvb20ucmVkL2JhYXN6b29tL3B1YmxpYy9ndWlhZWxlY3Ryb25pY2EvZ2VuZXJhclRva2VuIiwiaWF0IjoxNzI0Njg2MDMwLCJleHAiOjE3MjQ2OTMyMzAsIm5iZiI6MTcyNDY4NjAzMCwianRpIjoiYmJpbTB1VEFUaDRqcGVZbiJ9.pVSVBRcYq4MDJvFhPQ70nsaJ5TY3sm6hGOZ57xe3sDU",
        #     "frase_privada": "RH0sVTL9za7O6gutqI43"
        # }, args.api_key)

        # probar_post(c, "/privadas/createShipmentInternacional", {
        #     "login": "513307",
        #     "clave": "456789",
        #     "certificado": "$1$VZ3pDjRN$UneSGUXyLtIm4i2fMoKfH.",
        #     "codservicio": 3,
        #     "codoficinaori": 253,
        #     "remitente": "Hola Express C.A",
        #     "contacto_remitente": "Carmen Gonzalez",
        #     "telefono_remitente": "0053-1472587",
        #     "direccion_remitente": "Calle ana, casa N° 45, Urbanización los cedros de prados del este. Valle del Cauca, Colombia",
        #     "codpaisdes": 124,
        #     "ciudaddes": "valencia",
        #     "destinatario": "YESICA GONCALVES",
        #     "contacto_destino": "YESICA GONCALVES",
        #     "rif_ci_destinatario": "2021154",
        #     "telefono_destino": "0055-123456789",
        #     "direcciondes": "Calle la colina, edificio Don Julio, piso 1, apto 1-A, Urbanización la floresta, Guayaquil, Ecuador",
        #     "tipo_envio": "M",
        #     "numero_piezas": 1,
        #     "peso_bruto": 1,
        #     "valor_declarado": 11,
        #     "alto": 11,
        #     "ancho": 11,
        #     "largo": 11,
        #     "descripcion_contenido": "Prueba de Servicio Web",
        #     "web_services": 1,
        #     "retira_oficina": 1,
        #     "codoficinades": 136,
        #     "seguro": 1
        # }, args.api_key)

        # probar_post(c, "/privadas/etiquetaTermica", {
        #     "codguia": ["1000809676"],
        #     "termicaPdf": "1",
        #     "terminos": "1"
        # }, args.api_key)

        # probar_post(c, "/privadas/crearRecolectaWs", {
        #     "codclientePpal": 1,
        #     "clave": "456789",
        #     "nombreContacto": "TECNOLOGICA NACIONAL DE TUS COSAS C.A",
        #     "personaContacto": "CARLOS PEREZ",
        #     "documentoIdentidad": "V-20175578",
        #     "celular": "04125887034",
        #     "telefono": "02122410789",
        #     "codestado": 2,
        #     "codciudad": 19,
        #     "direccion": "CALLE 13, EDIFICIO LAS VILLAS, PISO 10 APTO 10-13",
        #     "urbanizacion": "LA FLORIDA",
        #     "fechaRecolecta": "18-11-2025",
        #     "tipoVeh": 1,
        #     "tipoServicio": 1,
        #     "codcasillero": "",
        #     "tipoEnvio": "M",
        #     "cantidadPiezas": 1,
        #     "peso": 0.9,
        #     "contenido": "FRANELAS",
        #     "observacion": "PRUEBA DE RECOLECTA"
        # }, args.api_key)

        # probar_post(c, "/privadas/serviciosClientes", {
        #     "login": "1",
        #     "codusuario": 1563,
        #     "codclienteweb": 4,
        #     "codserviciofin": 1,
        #     "nombre": "COD NACIONAL"
        # }, args.api_key)

        # probar_post(c, "/privadas/createShipment", {
        #     "login": "1",
        #     "clave": "456789",
        #     "codservicio": "1",
        #     "remitente": "HIRIBIN GIL",
        #     "contacto_remitente": "HIRIBIN GIL",
        #     "codciudadrem": "44",
        #     "tiporifcirem": "V-",
        #     "cirifrem": "20152013",
        #     "codmunicipiorem": "1303",
        #     "codparroquiarem": "130310",
        #     "zona_postal_remitente": "3009",
        #     "telefono_remitente": "04245163971",
        #     "codcelurem": "",
        #     "celularrem": "",
        #     "direccion_remitente": "42 ENTRE 26 Y 27",
        #     "inmueble_remitente": " DMS REPUESTOS ",
        #     "retira_oficina": "1",
        #     "codciudaddes": "12",
        #     "codmunicipiodes": "1114",
        #     "codparroquiades": "",
        #     "zona_postal_destino": "",
        #     "codoficinades": "59",
        #     "destinatario": "GABRIEL DIAZ",
        #     "contacto_destino": "GABRIEL DIAZ",
        #     "tiporifcidest": "V-",
        #     "cirif_destinatario": "18769615",
        #     "codceludest": "0414",
        #     "celular": "6813148",
        #     "telefono_destino": "00000000000",
        #     "direccion_destino": "SECTOR LOS TRES PLATOS, AV. LOS MEDANOS CRUCE CON AV. INDEPENDENCIA, EDIFICIO AREF, PB., LOCAL 1.",
        #     "inmueble_destino": "",
        #     "descripcion_contenido": "MERCANCIA",
        #     "referencia": "PA",
        #     "campo1": "123456",
        #     "campo2": "12345645",
        #     "campo3": "QEDDFSD456154",
        #     "numero_piezas": "1",
        #     "peso_bruto": "1.02",
        #     "tipo_envio": "M",
        #     "valor_declarado": "200",
        #     "seguro": "1",
        #     "valor_mercancia": "0",
        #     "modalidad_cod": "1",
        #     "web_services": "1"
        # }, args.api_key)

        # probar_post(c, "/privadas/GuardarRemitenteWs", {
        #     "codigo_oficina": "46",
        #     "nombre_remitente": "DENIS RAMIREZ",
        #     "cirif": "V-20175579",
        #     "contacto_remitente": "DENIS RAMIREZ",
        #     "direccion_remitente": "CALLE 3A URBANIZACIÓN LA URBINA",
        #     "ciudad_remitente": "19",
        #     "telefono_remitente": "0412-5887034",
        #     "observacion": "REMITENTE GUARDADO",
        #     "codigo_usuario": "2222",
        #     "parroquia_remitente": "101010",
        #     "municipio_remitente": "1010",
        #     "codpostal_remitente": "1010",
        #     "ciudad_ipostel": "152",
        #     "inmueble_remitente": "EDIFICIO DON PASQUALES PISO PB, APTO 10-80",
        #     "celular_remitente": "0412-5887034"
        # }, args.api_key)

        # probar_post(c, "/privadas/GuardarDestinatariosWs", {
        #     "codigo_usuario": "1563",
        #     "nombre_destinatario": "JOHAN FRANCO",
        #     "direccion_destino": "CUMBRES DE CURUMO",
        #     "contacto_destinatario": "DENIS RAMIREZ",
        #     "cirif_destinatario": "V-20175579",
        #     "telefono_destinatario": "04125887034",
        #     "fax_destinatario": "04125887034",
        #     "email_destinatario": "denisramirez@gmail.com",
        #     "codciudad_destino": "6",
        #     "codpais_destino": "124",
        #     "ciudad_destinoint": "MARACAIBO",
        #     "referencia": "OBJETOS",
        #     "municipio_destino": "2001",
        #     "parroquia_destino": "200100",
        #     "codpostal_destino": "200100",
        #     "ciudad_ipostel": "MARACAIBO",
        #     "estado_destino": "ZULIA",
        #     "inmueble_destinatario": "CASA N45",
        #     "celular_destinatario": "04125887034"
        # }, args.api_key)

        # Puedes agregar más pruebas POST aquí según se obtengan los payloads.

        # --- ARMI tests (al final) ---
        # probar_post(c, "/privadas/armi/monitor/business/create", {
        #     "name": "Supermercado Central",
        #     "type": "Retail",
        #     "ownerId": 123,
        #     "deliveryPerWeek": 3,
        #     "imageUrl": "https://example.com/logo.png",
        #     "branchOfficeList": [
        #         {
        #             "businessOwner": 123,
        #             "name": "Sucursal Norte",
        #             "city": "Bogotá",
        #             "state": "Cundinamarca",
        #             "address": "Av. Siempre Viva 742",
        #             "addressIndications": "Frente al parque",
        #             "lat": 4.7110,
        #             "lng": -74.0721,
        #             "phone": "3000000000",
        #             "image": "https://example.com/sucursal.png",
        #             "margins": [
        #                 {
        #                     "baseValue": 0.5,
        #                     "kmExtra": 0.7,
        #                     "otherIncentives": 0.1
        #                 }
        #             ]
        #         }
        #     ]
        # }, args.api_key)

        #========= probar envio zoom control maestro =========

#         probar_post(c,"/createShipment", {
#   "id_cliente": 1,
#   "id_empresa_envio": 1,
#   "referencia_interna": "REF-TEST-001",
#   "token_zoom": "TOKEN_DE_PRUEBA",
#   "codigo_cliente_zoom": "407940",

#   "remitente": "Remitente Demo",
#   "direccion_remitente": "Av. Principal #123",
#   "codciudadrem": 10,
#   "codestadorem": 1,
#   "codmunicipiorem": 2,
#   "codparroquiarem": 3,
#   "zona_postal_remitente": "1001",

#   "destinatario": "Destinatario Demo",
#   "direccion_destino": "Calle Secundaria #456",
#   "codciudaddes": 20,
#   "codestadodes": 2,
#   "codmunicipiodes": 3,
#   "codparroquiades": 4,
#   "zona_postal_destino": "2002",
#   "retira_oficina": "false",
#   "codoficinades": "null",

#   "codservicio": 104,
#   "tipo_tarifa": 1,
#   "modalidad_tarifa": 2,
#   "modalidad_cod": "null",

#   "numero_piezas": 1,
#   "peso_bruto": 1.5,
#   "alto": 10.0,
#   "ancho": 20.0,
#   "largo": 30.0,
#   "tipo_envio": "M",
#   "valor_mercancia": 100.0,
#   "valor_declarado": 0.0,
#   "seguro": "false",

#   "tipo_servicio": 1,
#   "estado_general": "CREADO",
#   "descripcion_contenido": "Caja de prueba",

#   "referencia": "REF-ZOOM-LOCAL",
#   "id_guia_zoom": "GUIA-LOCAL-001"
# }
#         , "api_key_zoom")

        #========= fin probar envio zoom control maestro =========

        # Opcional: probar consulta y eliminación si tienes IDs válidos
        # probar_get(c, "/privadas/armi/monitor/business/123")
        # r = c.delete("/privadas/armi/monitor/business/123", headers={"Authorization": f"Bearer {args.api_key}"})
        # print(f"DELETE /privadas/armi/monitor/business/123 -> {r.status_code}")
        # ...existing code...

        #--- Envío orquestado propio ---
        # Payload mínimo válido según validar_payload_estructura del orquestador
        params_envio = {
            "metadata": {"solicitud_id": "TEST-001"},
            "autenticacion_zoom": {
                "login": "1",
                "clave": "456789",
                "codigo_cliente": 407940,
                "cliente_id": 1
            },
            "configuracion_envio": {
                "tipo_envio": "nacional"
            },
            "servicio": {
                "codservicio": 1,
                "tipo_tarifa": 1,
                "modalidad_tarifa": 2
            },
            "ubicacion_origen": {
                "ciudad": {"codciudad": 44, "nombre": "MARACAIBO"}
            },
            "ubicacion_destino": {
                "ciudad": {"codciudad": 12, "nombre": "VALENCIA"}
            },
            "remitente": {
                "datos_personales": {
                    "nombre_completo": "HIRIBIN GIL",
                    "numero_documento": "20152013"
                },
                "direccion": {"direccion_completa": "42 ENTRE 26 Y 27"}
            },
            "destinatario": {
                "datos_personales": {
                    "nombre_completo": "GABRIEL DIAZ",
                    "numero_documento": "18769615"
                },
                "direccion": {"direccion_completa": "SECTOR LOS TRES PLATOS..."}
            },
            "paquete": {
                "numero_piezas": 1,
                "peso_total": 1.02
            }
        }
        probar_post(c, "/privadas/delivery/zoom/envio", params_envio, key)

if __name__ == "__main__":
    sys.exit(main())
