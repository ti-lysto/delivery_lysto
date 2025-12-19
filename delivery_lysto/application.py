"""
Aplicación Flask para integrar servicios de ZOOM (envíos) – Español
=================================================================

- Expone endpoints públicos (catálogos, tracking, precios)
- Expone endpoints privados (crear cliente, crear envío, imprimir envío)
- Preparada para despliegue en Azure App Service (gunicorn)
"""
from flask import Flask, jsonify
from .configuracion import Configuracion
from .core.registro import configurar_logging
from .core.errores import registrar_manejadores_errores
from .rutas.publicas import bp_publicas
from .rutas.privadas import bp_privadas
from .rutas.proxy import bp_proxy
from .db.conexion import probar_conexion
import logging as logger



def crear_aplicacion() -> Flask:
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)
    
    
    # Cargar configuración desde variables de entorno
    app.config.from_mapping(
        ZOOM_BASE_URL=Configuracion.ZOOM_BASE_URL,
        ZOOM_API_KEY=Configuracion.ZOOM_API_KEY,
        ZOOM_FRASE_SECRETA=Configuracion.ZOOM_FRASE_SECRETA,
        ZOOM_TIMEOUT=Configuracion.ZOOM_TIMEOUT,
        ZOOM_REINTENTOS=Configuracion.ZOOM_REINTENTOS,
        #ENTORNO=Configuracion.ENTORNO,
        DEBUG=Configuracion.DEBUG,
        LOG_NIVEL=Configuracion.LOG_NIVEL,
        ARMI_BASE_URL=Configuracion.ARMI_BASE_URL,
        ARMI_API_KEY=Configuracion.ARMI_API_KEY
    )
    #app.run(debug=app.config.get("DEBUG"), use_reloader=True)

    configurar_logging(app.config.get("LOG_NIVEL", "INFO"))
    registrar_manejadores_errores(app)
    if app.config.get("DEBUG"):
        logger.getLogger().info("Aplicación iniciada en modo DEBUG")
    probar_conexion()

    # Registro de blueprints (rutas)
    app.register_blueprint(bp_publicas, url_prefix="/api")
    app.register_blueprint(bp_privadas, url_prefix="/privadas")
    app.register_blueprint(bp_proxy, url_prefix="/api")

    @app.get("/health")
    def health():
        from .db.conexion import probar_conexion        
        try:
            probar_conexion()
            return jsonify({"status": "ok"})
            logger.info("Health check exitoso")
        except Exception as e:
            logger.error(f"Health check fallido: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.get("/info")
    def info():
        cfg = {k: app.config.get(k) for k in [
            "ZOOM_BASE_URL",
            "ZOOM_TIMEOUT",
            "ZOOM_REINTENTOS",
        ]}
        return jsonify({"app": "zoom-api", "config": cfg})

    return app


# Objeto de aplicación para gunicorn (Azure)
app = crear_aplicacion()
