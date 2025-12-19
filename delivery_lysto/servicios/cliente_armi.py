"""
Cliente HTTP para APIs de ARMI – Español
----------------------------------------
Centraliza las llamadas HTTP (públicas y privadas), autenticación y manejo de errores.
"""
import logging
from typing import Any, Dict, Optional
import httpx
from ..configuracion import Configuracion

logger = logging.getLogger(__name__)

class ClienteArmi:
    """Cliente HTTP simple para ARMI (sincrónico)."""

    def __init__(
        self,
        base_url: str,
        api_key: str = "",
        country: Optional[str] = None,
        timeout: float = 10.0,
        reintentos: int = 3,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.country = country or Configuracion.ARMI_COUNTRY
        self.timeout = timeout
        self.reintentos = max(0, reintentos)

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "armi-business-api-key": self.api_key,
            "country": self.country
        }

    def solicitar(
        self,
        ruta: str,
        metodo: str = "GET",
        parametros: Optional[Dict[str, Any]] = None,
        cuerpo: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{ruta.lstrip('/')}"
        for intento in range(self.reintentos + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    if metodo.upper() == "GET":
                        resp = client.get(url, headers=self._headers(), params=parametros)
                    elif metodo.upper() == "POST":
                        resp = client.post(url, headers=self._headers(), json=cuerpo)
                    elif metodo.upper() == "DELETE":
                        resp = client.delete(url, headers=self._headers(), params=parametros)
                    else:
                        raise ValueError(f"Método HTTP no soportado: {metodo}")
                resp.raise_for_status()
                logger.info(f"ARMI {metodo} {url} OK: {resp.status_code}")
                return resp.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"ARMI error HTTP {e.response.status_code}: {e.response.text}")
                if intento == self.reintentos:
                    return {"error": str(e)}
            except Exception as e:
                logger.error(f"ARMI error: {str(e)}")
                if intento == self.reintentos:
                    return {"error": str(e)}
        return {"error": "No se pudo completar la solicitud ARMI"}

    def validar_campo_requerido(self, **campos: Any) -> bool:
        """Valida que los campos requeridos no sean None o cadenas vacías."""
        for nombre, valor in campos.items():
            if valor is None or (isinstance(valor, str) and not valor.strip()):
                logger.error(f"Campo requerido faltante o inválido: {nombre}")
                return False
        return True
    
    # Ejemplo de método para crear negocio
    def crear_negocio(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        return self.solicitar(Configuracion.RUTA_ARMI_CREA_NEGOCIO, metodo="POST", cuerpo=datos)

    # Ejemplo de método para consultar negocio
    def consultar_negocio(self, negocio_id: int) -> Dict[str, Any]:
        return self.solicitar(f"monitor/business/{negocio_id}", metodo="GET")

    # Ejemplo de método para eliminar negocio
    def eliminar_negocio(self, negocio_id: int) -> Dict[str, Any]:
        return self.solicitar(f"monitor/business/{negocio_id}", metodo="DELETE")

    # Puedes agregar más métodos según la documentación de ARMI
