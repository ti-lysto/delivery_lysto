"""
Autenticación para endpoints privados – Español
----------------------------------------------
Valida API Key y genera firma HMAC opcional si se requiere.
"""
import hmac
import hashlib
import json
from functools import wraps
from flask import request, jsonify, current_app
from ..configuracion import Configuracion



def requerir_api_key(Delivery_Empresa=None):
    """Decorator que exige API Key en cabecera Authorization (Bearer)."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            match Delivery_Empresa:            
                case "ZOOM":
                    api_key_config = Configuracion.ZOOM_API_KEY
                    if not api_key_config:
                        return jsonify({"ok": False, "error": {"mensaje": "API Key no configurada"}}), 500
                case "ARMI":
                    api_key_config = Configuracion.ARMI_API_KEY
                    if not api_key_config:
                        return jsonify({"ok": False, "error": {"mensaje": "API Key no configurada"}}), 500
                case _:
                    return jsonify({"ok": False, "error": {"mensaje": "Empresa no configurada"}}), 500
            
            #api_key_config = current_app.config.get("ZOOM_API_KEY", "")
            if not api_key_config:
                return jsonify({"ok": False, "error": {"mensaje": "API Key no configurada"}}), 500

            cabecera = request.headers.get("Authorization", "")
            prefijo = "Bearer "
            if not cabecera.startswith(prefijo):
                return jsonify({"ok": False, "error": {"mensaje": "Autorización requerida"}}), 401

            api_key_recibida = cabecera[len(prefijo) :]
            if api_key_recibida != api_key_config:
                return jsonify({"ok": False, "error": {"mensaje": "API Key inválida"}}), 401

            return func(*args, **kwargs)
        return wrapper
    return decorator


def generar_firma_hmac(datos: dict, frase_secreta: str) -> str:
    """Genera firma HMAC-SHA256 a partir del JSON y una frase secreta.

    Nota: Si la documentación exige otro orden/concatenación de campos,
    esta función se puede ajustar. Por defecto firma el JSON canonizado.
    """
    payload = json.dumps(datos, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hmac.new(frase_secreta.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
