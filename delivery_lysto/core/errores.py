"""

--------------------------------------
Define excepciones propias y mapeo a respuestas HTTP.
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException


class ErrorZoom(Exception):
    """Error genérico de ZOOM."""

    def __init__(self, mensaje: str, codigo_zoom: str | None = None, status: int = 500):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo_zoom = codigo_zoom
        self.status = status


class RecursoNoEncontrado(ErrorZoom):
    def __init__(self, mensaje: str = "Recurso no encontrado", codigo_zoom: str | None = None):
        super().__init__(mensaje, codigo_zoom, 404)


class ParametrosInvalidos(ErrorZoom):
    def __init__(self, mensaje: str = "Parámetros inválidos", codigo_zoom: str | None = None):
        super().__init__(mensaje, codigo_zoom, 400)


class Conflicto(ErrorZoom):
    def __init__(self, mensaje: str = "Conflicto de datos", codigo_zoom: str | None = None):
        super().__init__(mensaje, codigo_zoom, 409)


class ErrorUpstream(ErrorZoom):
    def __init__(self, mensaje: str = "Error en servicio externo", codigo_zoom: str | None = None):
        super().__init__(mensaje, codigo_zoom, 502)


class NoProcesable(ErrorZoom):
    def __init__(self, mensaje: str = "Entidad no procesable", codigo_zoom: str | None = None):
        super().__init__(mensaje, codigo_zoom, 422)


ZOOM_MAPEO_CODIGOS = {
    "CODE_000": RecursoNoEncontrado,  # no existe en BD
    "CODE_001": ErrorUpstream,        # error consulta
    "CODE_002": ParametrosInvalidos,  # parámetros incorrectos
    "CODE_003": ErrorUpstream,        # error llamada servicio
    "CODE_004": Conflicto,            # registro ya existe
    "CODE_005": NoProcesable,         # no pudo actualizarse
    "CODE_006": ErrorUpstream,        # error conexión SAP
    "CODE_007": NoProcesable,         # no pudo insertarse
}


def lanzar_por_codigo(codigo: str, mensaje: str):
    exc = ZOOM_MAPEO_CODIGOS.get(codigo, ErrorZoom)
    raise exc(mensaje, codigo)


def registrar_manejadores_errores(app):
    @app.errorhandler(ErrorZoom)
    def manejar_error_zoom(err: ErrorZoom):
        respuesta = {
            "ok": False,
            "error": {
                "mensaje": err.mensaje,
                "codigo_zoom": err.codigo_zoom,
            },
        }
        return jsonify(respuesta), err.status

    @app.errorhandler(HTTPException)
    def manejar_http_exception(err: HTTPException):
        respuesta = {
            "ok": False,
            "error": {
                "mensaje": err.description,
                "codigo_zoom": None,
            },
        }
        return jsonify(respuesta), err.code

    @app.errorhandler(Exception)
    def manejar_exception(err: Exception):
        respuesta = {
            "ok": False,
            "error": {
                "mensaje": str(err),
                "codigo_zoom": None,
            },
        }
        return jsonify(respuesta), 500
