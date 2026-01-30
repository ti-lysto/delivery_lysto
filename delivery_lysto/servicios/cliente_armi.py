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
        url = f"{Configuracion.ARMI_BASE_URL}/{ruta.lstrip('/')}"
        print ("configuracion.ARMI_BASE_URL:", Configuracion.ARMI_BASE_URL )
        print("URL ARMI:", url) 
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
                    return {"error": str(e), "mensaje": e.response.json()}
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
        respuesta= self.solicitar(Configuracion.RUTA_ARMI_CREA_NEGOCIO, metodo="POST", cuerpo=datos)
        # print(f"Respuesta crear negocio ARMI: {respuesta}")
        # print(f"estatus: ", respuesta.get("status"))
        # print(respuesta.get("mensaje", {}).get("status"))
        if respuesta.get("error") is None :
            # respuesta_JSON= {
            #     "status": True,
            #     "message": "Success",
            #     "id": respuesta.get("id"),
            #     "name": respuesta.get("name"),
            #     "type": respuesta.get("type"),
            #     "ownerId": respuesta.get("ownerId"),
            #     "deliveryPerWeek": respuesta.get("deliveryPerWeek"),
            #     "branchOfficeList": None,
            #     "imageUrl": respuesta.get("imageUrl")
            #     }
            respuesta_JSON= respuesta
            logger.info(f"Negocio ARMI creado exitosamente: {respuesta_JSON}")
        else:
            respuesta_JSON= {                
                "status": False,
                "message": respuesta.get("mensaje",{}).get("message"),
                "id": 0,
                "name": None,
                "type": None,
                "ownerId": 0,
                "deliveryPerWeek": 0,
                "branchOfficeList": None,
                "imageUrl": None
                }
            logger.error(f"Error al crear negocio ARMI: {respuesta.get('error')}, datos: {datos}, respuesta: {respuesta}")
        return respuesta_JSON
    # Ejemplo de método para consultar negocio
    def consultar_negocio(self, negocio_id: int) -> Dict[str, Any]:
        respuesta = self.solicitar(f"monitor/business/{negocio_id}", metodo="GET")
        print(f"Respuesta consultar negocio ARMI: {respuesta}")
        return respuesta

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
        respuesta= self.solicitar(f"monitor/order/status/{order_id}", metodo="GET")
        print (f"Respuesta estado orden ARMI: {respuesta}")
        if respuesta.get("status")=="OK":
            json_respuesta = {
                "OK": True,
                "message": "Success",
                "orderStatus": respuesta.get("data", {}).get("status")
                #"orderStatusDescription": descripcion_estado
                }
        else:
            json_respuesta = {
                "OK": False,
                "message": "Error al obtener estado de orden",
                "orderStatus": None
                #"orderStatusDescription": None
            }
        return json_respuesta

    # Ciudades y costo de envío
    def codigo_ciudad(self, city: str) -> Dict[str, Any]:
        respuesta = self.solicitar(f"monitor/city/{city}", metodo="GET")        
        if respuesta.get("status")=="OK":
            
            json_respuesta = {
                "status": True,
                "city": respuesta.get("data")
            }
        else:
            error_msg = respuesta.get("data", {}).get("message", "Desconocido")
            logger.error(f"Error al obtener código de ciudad ARMI: {error_msg}, datos: {city}, respuesta: {respuesta}")
            json_respuesta = {
                "status": False,
                "city": None
            }
        return json_respuesta

    def costo_envio(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        respuesta=  self.solicitar("monitor/order/delivery-cost", metodo="POST", cuerpo=datos)
        #print(f"Respuesta costo envío ARMI: {respuesta}")
        if respuesta.get("status")=="OK":
            json_respuesta = {
                "status": True,
                "deliveryCost": respuesta.get("data", {}).get("deliveryCost"), 
                "distance": respuesta.get("data", {}).get("distance"),
                "margin": respuesta.get("data", {}).get("margin"),
                "totalCost": respuesta.get("data", {}).get("totalCost")
            }
        else:
            error_msg = respuesta.get("data", {}).get("message", "Desconocido")
            logger.error(f"Error al obtener costo de envío ARMI: {error_msg} datos: {datos}, respuesta: {respuesta}")
            json_respuesta = {
                "status": False,
                "deliveryCost": None,
                "distance": None,
                "margin": None,
                "totalCost": None
            }
        return json_respuesta
    
    # ------ INTEGRACIÓN INSTALEAP ------
    def crear_orden_instaleap(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Crea una orden desde Instaleap"""
        # procesar la solicitud de instaleap
        
        return self.solicitar("monitor/instaleap/create", metodo="POST", cuerpo=datos)
    
    def actualizar_orden_instaleap(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Actualiza una orden desde Instaleap"""
        return self.solicitar("monitor/instaleap/update", metodo="POST", cuerpo=datos)
    
    def tracking_orden_instaleap(self, country: str = "COL") -> Dict[str, Any]:
        """Obtiene tracking de órdenes Instaleap"""
        headers = {
            "Content-Type": "application/json",
            "armi-business-api-key": self.api_key,
            "country": country  # Sobreescribir country si es necesario
        }
        # Este endpoint es GET sin body
        url = f"{self.base_url}/monitor/instaleap/tracking-order"
        
        for intento in range(self.reintentos + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.request("GET", url, headers=headers)
                resp.raise_for_status()
                logger.info(f"ARMI Instaleap tracking OK: {resp.status_code}")
                return resp.json()
            except Exception as e:
                logger.error(f"ARMI Instaleap tracking error: {str(e)}")
                if intento == self.reintentos:
                    return {"error": str(e)}
        return {"error": "No se pudo completar el tracking Instaleap"}
    
    def confirmar_cash_recibido(self, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Confirma pago en efectivo recibido"""
        # Este endpoint usa PUT
        return self.solicitar("monitor/instaleap/cash/received", metodo="PUT", cuerpo=datos)