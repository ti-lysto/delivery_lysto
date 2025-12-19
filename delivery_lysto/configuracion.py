"""
Configuración de la API de Delivery Lysto
-------------------------------------
Lee variables de entorno y define rutas por defecto de los servicios públicos.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Configuracion:
    """Configuración central de la API."""

    # Entorno (sandbox | produccion)
    #ENTORNO = os.getenv("ENTORNO", "sandbox")
    DEBUG = os.getenv("DEBUG", "False").lower() in ("1", "true", "yes") 
    # Nivel de log
    LOG_NIVEL = os.getenv("LOG_NIVEL", "INFO").upper()
    # Archivo donde guardar logs
    LOG_FILE = "logs/delivery_lysto.log"
    # Cantidad máxima de líneas a retener en el log local
    LOG_MAX_LINES = "200"

    # Base URL (usar siempre la provista en entorno, sin forzar /api ni localhost)
    ZOOM_BASE_URL = os.getenv("ZOOM_BASE_URL", "http://sandbox.zoom.red/baaszoom/public/canguroazul").rstrip("/")
    ZOOM_BASE_URL_qa = "https://miws-qa.zoom.red/api".rstrip("/")
    ZOOM_BASE_URL_qa2 = "https://sandbox.zoom.red/baaszoom/public/guiaelectronica".rstrip("/")
    
    ZOOM_DB_HOST = os.getenv("ZOOM_DB_HOST")
    ZOOM_DB_PORT = int(os.getenv("ZOOM_DB_PORT"))
    ZOOM_DB_NAME = os.getenv("ZOOM_DB_NAME")
    ZOOM_DB_USER = os.getenv("ZOOM_DB_USER")
    ZOOM_DB_PASSWORD = os.getenv("ZOOM_DB_PASSWORD")
    ZOOM_IMPRESION_ETIQUETA = True
    ZOOM_GUARDA_PDF_ETIQUETA = True
    ZOOM_DIR_ETIQUETAS = "/home/alirubio/Documentos/Desarrollo/Python/delivery_lysto_api/etiquetas"
      
    # Credenciales (para endpoints privados)
    ZOOM_API_KEY = os.getenv("ZOOM_API_KEY", "")
    ZOOM_FRASE_SECRETA = os.getenv("ZOOM_FRASE_SECRETA", "")
    ARMI_API_KEY = os.getenv("ARMI_API_KEY", "")

    # Timeout y reintentos
    ZOOM_TIMEOUT = float(os.getenv("ZOOM_TIMEOUT", "15"))
    ZOOM_REINTENTOS = int(os.getenv("ZOOM_REINTENTOS", "3"))

    ARMI_BASE_URL = "https://localhost:8001" if DEBUG else os.getenv("ARMI_BASE_URL")
    #(os.getenv("ARMI_BASE_URL", "https://api.armi.example").rstrip("/"))
    ARMI_COUNTRY = os.getenv("ARMI_COUNTRY", "COL")

   # Rutas ZOOM
   # Rutas públicas 
    RUTA_ZOOM_INFOTRACKING = "getInfoTracking"
    RUTA_ZOOM_TIPOTARIFA = "getTipoTarifa"
    RUTA_ZOOM_MODALIDADTARIFA = "getModalidadTarifa"
    RUTA_ZOOM_CIUDADES = "getCiudades"
    RUTA_ZOOM_OFICINAS = "getOficinas"
    RUTA_ZOOM_PAISES = "getPaises"
    RUTA_ZOOM_TIPOENVIO="getTipoEnvio"
    RUTA_ZOOM_CALCULAR_TARIFA = "CalcularTarifa"
    RUTA_ZOOM_TRACKWS = "getZoomTrackWs"
    RUTA_ZOOM_LANGUAGES = "getlanguages"
    RUTA_ZOOM_RTAGS = "getRespuestastags"
    RUTA_ZOOM_LASTTRACKING = "getLastTracking"
    RUTA_ZOOM_MUNICIPIOS = "getMunicipios"
    RUTA_ZOOM_PARROQUIAS = "getParroquias"
    RUTA_ZOOM_OFICINASGE = "getOficinasGE"
    RUTA_ZOOM_STATUS="getStatus"
    RUTA_ZOOM_CIUDADESOFI="getCiudadesOfi"
    RUTA_ZOOM_SUCURSALES="getSucursales"
    RUTA_ZOOM_TIPORUTAENVIO="getTipoRutaEnvio"
    RUTA_ZOOM_MODALIDADCOD="getModalidadCod"
    RUTA_ZOOM_ESTADOS = "getEstados"
    RUTA_ZOOM_GETOFICINAESTADOWS = "getOficinaEstadoWs"
    RUTA_ZOOM_TIPOPRECIOWS = "getTipoPrecioWs"
    RUTA_ZOOM_CONSULTAPRECIOWS = "consultarPreciosWs"
    RUTA_ZOOM_CONSULTATRACKINGWS="consultaTrackingWs"
    RUTA_ZOOM_ZONASNOSERVIDASWS="zonasNoServidasWs"
    RUTA_ZOOM_TIPODOCUMENTO="getTipoDocumento"
    RUTA_ZOOM_LISTADOGENERICOCIUDADES="listadoGenericoCiudades"
    RUTA_ZOOM_CIUDADESWS="getCiudadesWs"
    # Rutas privadas configurables 
    RUTA_ZOOM_INFORMECLIENTE="informeCliente"
    RUTA_ZOOM_ZOOMCERT="zoomCert"
    RUTA_ZOOM_SERVICIOSCLIENTES="serviciosClientes"
    RUTA_ZOOM_CREARSHIPMENT="createShipment"
    RUTA_ZOOM_GUARDARREMITENTEWS="GuardarRemitenteWs"
    RUTA_ZOOM_GUARDARDESTINATARIOSWS="GuardarDestinatariosWs"
    RUTA_ZOOM_CREARTOKEN="crearToken"
    RUTA_ZOOM_CREATE_SHIPMENT_INTERNACIONAL="createShipmentInternacional"
    RUTA_ZOOM_ETIQUETA_TERMICA="etiquetaTermica"
    RUTA_ZOOM_CREARRECOLECTAWS="crearRecolectaWs"
    RUTA_ZOOM_CREACIONCLIENTES="CreacionClientesWs"
    
    # Rutas ARMI
    RUTA_ARMI_CREA_NEGOCIO = "/monitor/business/create"

