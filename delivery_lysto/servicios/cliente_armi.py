"""

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
                    resp = client.request(
                        metodo.upper(),
                        url,
                        headers=self._headers(),
                        params=parametros,
                        json=cuerpo,
                    )
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

    # Negocios adicionales
    def negocios_del_usuario(self, user_id: int) -> Dict[str, Any]:
        return self.solicitar(f"monitor/business/all/{user_id}", metodo="GET")

    def actualizar_negocio(self, negocio_id: int, datos: Dict[str, Any]) -> Dict[str, Any]:
        return self.solicitar(f"monitor/business/update/{negocio_id}", metodo="POST", cuerpo=datos)

    # Sucursales
    def crear_sucursal(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        return self.solicitar("monitor/branchOffice/create", metodo="POST", cuerpo=datos)

    def sucursales_del_negocio(self, business_id: int) -> Dict[str, Any]:
        return self.solicitar(f"monitor/branchOffice/all/{business_id}", metodo="GET")

    def eliminar_sucursal(self, branch_office_id: int, business_id: int) -> Dict[str, Any]:
        body = {"branchOfficeId": branch_office_id, "businessId": business_id}
        return self.solicitar("monitor/branchOffice/delete", metodo="DELETE", cuerpo=body)

    # Órdenes
    def crear_orden(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        return self.solicitar("monitor/order/create", metodo="POST", cuerpo=datos)

    def cancelar_orden(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        return self.solicitar("monitor/order/cancel", metodo="POST", cuerpo=datos)

    def estado_orden(self, order_id: int) -> Dict[str, Any]:
        return self.solicitar(f"monitor/order/status/{order_id}", metodo="GET")

    # Ciudades y costo de envío
    def codigo_ciudad(self, city: str) -> Dict[str, Any]:
        return self.solicitar(f"monitor/city/{city}", metodo="GET")

    def costo_envio(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        return self.solicitar("monitor/order/delivery-cost", metodo="POST", cuerpo=datos)
