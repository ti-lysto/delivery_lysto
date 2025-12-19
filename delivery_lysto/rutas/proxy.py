"""
Proxy genérico para acceder a cualquier endpoint documentado de ZOOM.
Útil para pruebas rápidas mientras se implementan endpoints específicos.

Advertencia: Mantener protegido; respeta `X-API-Key` para marcar llamadas privadas.
"""
from flask import Blueprint, request, jsonify, current_app
from ..servicios.cliente_zoom import ClienteZoom

bp_proxy = Blueprint("proxy", __name__)


def _cliente() -> ClienteZoom:
    cfg = current_app.config
    return ClienteZoom(
        base_url=cfg["ZOOM_BASE_URL"],
        api_key=cfg.get("ZOOM_API_KEY", ""),
        frase_secreta=cfg.get("ZOOM_FRASE_SECRETA", ""),
        timeout=cfg.get("ZOOM_TIMEOUT", 10.0),
        reintentos=cfg.get("ZOOM_REINTENTOS", 3),
    )


@bp_proxy.route("/proxy/<path:ruta>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_zoom(ruta: str):
    cliente = _cliente()
    metodo = request.method
    params = request.args.to_dict(flat=True)
    body = request.get_json(silent=True) or {}
    privado = bool(request.headers.get("X-API-Key"))

    data = cliente._solicitar(ruta, metodo=metodo, parametros=params or None, cuerpo=body or None, privado=privado)
    return jsonify({"ok": True, "ruta": ruta, "metodo": metodo, "data": data})
