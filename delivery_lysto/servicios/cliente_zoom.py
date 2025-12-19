"""
Cliente HTTP para APIs de ZOOM – Español
----------------------------------------
Centraliza las llamadas HTTP (públicas y privadas), mapeo de códigos y reintentos.
"""
from __future__ import annotations
import time
import json
import logging
from typing import Any, Dict, Optional
import httpx
from ..configuracion import Configuracion

from ..core.errores import (
    lanzar_por_codigo,
    ErrorZoom,
)

logger = logging.getLogger(__name__)


class ClienteZoom:
    """Cliente HTTP simple para ZOOM (sincrónico)."""

    def __init__(
        self,
        base_url: str,
        api_key: str = "",
        frase_secreta: str = "",
        timeout: float = 10.0,
        reintentos: int = 3,

        #privado: bool = False,
    ) -> None:
        # Usa la dirección QA en debug; normal en producción. Limpia espacios.
        self.base_url = (Configuracion.ZOOM_BASE_URL_qa if Configuracion.DEBUG else base_url).strip().rstrip("/")
        #self.base_url=base_url.strip().rstrip("/")
        self.api_key = api_key
        self.frase_secreta = frase_secreta
        self.timeout = timeout
        self.reintentos = max(0, reintentos)

    def _headers_publicos(self) -> Dict[str, str]:
        return {"Content-Type": "application/json"}

    def _headers_privados(self, cuerpo: Optional[dict] = None, usatoken: Optional[bool] = False, token: Optional[str] = None) -> Dict[str, str]:
        cabeceras = {"Content-Type": "application/json"}
        if self.api_key and not usatoken:
            cabeceras["Authorization"] = f"Bearer {self.api_key}"
        elif usatoken and token:
            cabeceras["Authorization"] = f"Bearer {token}"
        # Si se requiere firma HMAC por parte de ZOOM, descomentar/ajustar:
        # if self.frase_secreta and cuerpo is not None:
        #     from zoom_api.core.autenticacion import generar_firma_hmac
        #     firma = generar_firma_hmac(cuerpo, self.frase_secreta)
        #     cabeceras["X-Zoom-Firma"] = firma
        return cabeceras

    def validacion_campo_requerido(self, **kwargs) -> bool:
        return all(v is not None for v in kwargs.values())

    def _solicitar(
        self,
        ruta: str,
        metodo: str = "GET",
        parametros: Optional[Dict[str, Any]] = None,
        cuerpo: Optional[Dict[str, Any]] = None,
        privado: bool = False,
        url_alternativa: Optional[bool] = False,
        usatoken: Optional[bool] = False,
        token: Optional[str] = None,
        
    ) -> Any:
        url = f"{Configuracion.ZOOM_BASE_URL_qa2}/{ruta.lstrip('/')}" if url_alternativa else f"{self.base_url}/{ruta.lstrip('/')}" if privado else f"{Configuracion.ZOOM_BASE_URL}/{ruta.lstrip('/')}"
        print(f"URL solicitada: {url} cuerpo: {cuerpo}")
        if not (url.startswith("http://") or url.startswith("https://")):
            raise ErrorZoom("ZOOM_BASE_URL inválida: falta esquema http/https")
        backoff = 0.5

        for intento in range(1, self.reintentos + 2):
            try:
                headers = self._headers_privados(cuerpo, usatoken=usatoken, token=token) if privado else self._headers_publicos()
                with httpx.Client(timeout=self.timeout, follow_redirects=True) as cliente:
                    resp = cliente.request(metodo.upper(), url, params=parametros, json=cuerpo, headers=headers)
                logger.info(f"ZOOM {metodo.upper()} {url} -> {resp.status_code} (final URL: {str(resp.request.url)})")
                # Intentar parsear JSON
                try:
                    data = resp.json()
                except Exception:
                    data = {"status_code": resp.status_code, "texto": resp.text}

                # Manejo de códigos de ZOOM (si existen en respuesta)
                if isinstance(data, dict) and "Codrespuesta" in data:
                    codigo = data.get("Codrespuesta")
                    mensaje = data.get("Mensaje", "Error en respuesta de ZOOM")
                    if codigo and codigo != "OK":
                        lanzar_por_codigo(codigo, mensaje)

                # Levantar por status HTTP si no es exitoso y no trae código propio
                if resp.status_code >= 400:
                    raise ErrorZoom(f"HTTP {resp.status_code}: {data}")

                return data

            except (httpx.ConnectError, httpx.ReadTimeout) as e:
                logger.warning(f"Error de red ({e}), intento {intento} de {self.reintentos + 1}")
                if intento > self.reintentos:
                    raise ErrorZoom("Fallo de red al comunicar con ZOOM")
                time.sleep(backoff)
                backoff *= 2
            except ErrorZoom:
                # Errores mapeados desde ZOOM: no reintentar
                raise
            except Exception as e:
                logger.exception("Error inesperado en cliente ZOOM")
                raise ErrorZoom(str(e))

    # Métodos de conveniencia públicos
    def obtener_infotracking(self, tipo_busqueda: Optional[int], codigo: str, codigo_cliente:int):
        params={"tipo_busqueda": tipo_busqueda, "codigo": codigo, "codigo_cliente": codigo_cliente}
        return self._solicitar(Configuracion.RUTA_ZOOM_INFOTRACKING, "GET", parametros=(params or None))
    
    def obtener_infoTarifa(self):
        return self._solicitar(Configuracion.RUTA_ZOOM_TIPOTARIFA, "GET")

    def obtener_modalidad_tarifa(self):
        return self._solicitar(Configuracion.RUTA_ZOOM_MODALIDADTARIFA, "GET")

    def obtener_ciudades(self, codestado: int ,filtro:Optional[str]=None,idioma: Optional[int] = None):
        """Obtiene ciudades. La API puede esperar `codestado` en lugar de `estado`.
        Aceptamos ambos y enviamos el que corresponda.
        """
        if not self.validacion_campo_requerido(codestado=codestado):
            raise ValueError("codestado es un campo requerido")
        params = {}        
        params["codestado"] = codestado
        params["filtro"] = filtro
        params["idioma"] = idioma        
        return self._solicitar(Configuracion.RUTA_ZOOM_CIUDADES, "GET", parametros=(params or None))

    def obtener_oficinas(self, codciudad: str, codservicio: int, siglas: Optional[str] = None, codpais: int = 0):
        if not self.validacion_campo_requerido(codciudad=codciudad, codservicio=codservicio):
            raise ValueError("codpais es un campo requerido")        
        params = {}        
        params["siglas"] = siglas
        params["codpais"] = codpais        
        params["codciudad"] = codciudad        
        params["codservicio"] = codservicio

        return self._solicitar(Configuracion.RUTA_ZOOM_OFICINAS, "GET", parametros=params if params else None)

    def obtener_paises (self,tipo: int,idioma:Optional[int]=None):
        params = {}
        if not self.validacion_campo_requerido(tipo=tipo,):
            raise ValueError("tipo es un campo requerido")        
        params["tipo"] = tipo
        params["idioma"] = idioma
        return self._solicitar(Configuracion.RUTA_ZOOM_PAISES, "GET",parametros=params if params else None)

    def obtener_tipo_envio(self):
        return self._solicitar(Configuracion.RUTA_ZOOM_TIPOENVIO, "GET")

    def obtener_tarifa (
            self, 
            tipo_tarifa:Optional[int]=None, 
            modalidad_tarifa:Optional[int]=None, 
            ciudad_remitente :Optional[int]=None, 
            ciudad_destinatario:Optional[int]=None, 
            oficina_retirar:Optional[int]=None, 
            cantidad_piezas:Optional[str]=None, 
            peso:Optional[str]=None, 
            valor_mercancia:Optional[str]=None, 
            valor_declarado:Optional[str]=None, 
            codpais:Optional[str]=None,
            tipo_envio:Optional[str]=None,
            zona_postal:Optional[str]=None,
            alto:Optional[str]=None,
            ancho:Optional[str]=None,
            largo:Optional[str]=None
            ):
        params = {}
        params["tipo_tarifa"] = tipo_tarifa
        params["modalidad_tarifa"] = modalidad_tarifa
        params["ciudad_remitente"] = ciudad_remitente
        params["ciudad_destinatario"] = ciudad_destinatario
        params["oficina_retirar"] = oficina_retirar
        params["cantidad_piezas"] = cantidad_piezas
        params["peso"] = peso
        params["valor_mercancia"] = valor_mercancia
        params["valor_declarado"] = valor_declarado
        params["codpais"] = codpais
        params["tipo_envio"] = tipo_envio
        params["zona_postal"] = zona_postal
        params["alto"] = alto
        params["ancho"] = ancho
        params["largo"] = largo
        return self._solicitar(Configuracion.RUTA_ZOOM_CALCULAR_TARIFA, "GET", parametros=params if params else None)

    def obtener_trackws (
            self,
            codigo:str,
            tipo_busqueda: int,
            web:Optional[bool] = None            
            ):
        if not self.validacion_campo_requerido(codigo=codigo, tipo_busqueda=tipo_busqueda):
            raise ValueError("codigo y tipo_busqueda son campos requeridos")
        params = {}
        params["codigo"] = codigo
        params["tipo_busqueda"] = tipo_busqueda
        params["web"] = web
        return self._solicitar(Configuracion.RUTA_ZOOM_TRACKWS, "GET", parametros=params if params else None)
    
    def obtener_idiomas (self):
        return self._solicitar(Configuracion.RUTA_ZOOM_LANGUAGES, "GET")
    
    def obtener_respuestastags (
            self,
            id_language:Optional[int] = None,
            codrespuesta:Optional[str] = None
            ):
        params = {}
        params["id_language"] = id_language
        params["codrespuesta"] = codrespuesta
        return self._solicitar(Configuracion.RUTA_ZOOM_RTAGS, "GET", parametros=params if params else None)
    
    def obtener_ultimotrack (
            self,
            codigo:str,
            codigo_cliente:int,
            tipo_busqueda:Optional[int] = None
    ):
        if not self.validacion_campo_requerido(codigo=codigo, codigo_cliente=codigo_cliente):
            raise ValueError("codigo y codigo_cliente son campos requeridos")
        params = {}
        params["tipo_busqueda"] = tipo_busqueda
        params["codigo"] = codigo
        params["codigo_cliente"] = codigo_cliente
        return self._solicitar(Configuracion.RUTA_ZOOM_LASTTRACKING, "GET", parametros=params if params else None)

    def obtener_municipios(self, codciudad: int, remitente: Optional[str] = None):
        """Obtiene municipios. Flexibiliza nombres: estado/codestado y ciudad/codciudad."""
        if not self.validacion_campo_requerido(codciudad=codciudad):
            raise ValueError("codciudad es un campo requerido")
        params = {}
        params["codciudad"] = codciudad
        params["remitente"] = remitente
        return self._solicitar(Configuracion.RUTA_ZOOM_MUNICIPIOS, "GET", parametros=params if params else None)

    def obtener_parroquias(self, codmunicipio: int, codciudad: int, remitente: Optional[str] = None):
        """Obtiene parroquias usando nombres de parámetros esperados por la API remota.

        La respuesta que vimos exige `codmunicipio` y `codciudad`.
        """
        if not self.validacion_campo_requerido(codmunicipio=codmunicipio, codciudad=codciudad):
            raise ValueError("codmunicipio y codciudad son campos requeridos")
        params = {}        
        params["codmunicipio"] = codmunicipio        
        params["codciudad"] = codciudad
        params["remitente"] = remitente
        return self._solicitar(Configuracion.RUTA_ZOOM_PARROQUIAS, "GET", parametros=(params or None))

    def obtener_oficinasGE(self, codigo_ciudad_destino: int, modalidad_tarifa: Optional[int] = None,tipo_tarifa: Optional[int] =None):
        """Obtiene oficinas GE. Flexibiliza nombres: estado/codestado y ciudad/codciudad."""
        if not self.validacion_campo_requerido(codigo_ciudad_destino=codigo_ciudad_destino):
            raise ValueError("codigo_ciudad_destino es un campo requerido")
        params = {}
        params["codigo_ciudad_destino"] = codigo_ciudad_destino
        params["modalidad_tarifa"] = modalidad_tarifa
        params["tipo_tarifa"] = tipo_tarifa
        return self._solicitar(Configuracion.RUTA_ZOOM_OFICINASGE, "GET", parametros=params if params else None)

    def obtener_status(self):
        return self._solicitar(Configuracion.RUTA_ZOOM_STATUS, "GET")

    def obtener_ciudades_ofi(self, codestado: str,recolecta: Optional[int] = None):
        """Obtiene ciudades. La API puede esperar `codestado` en lugar de `estado`.
        Aceptamos ambos y enviamos el que corresponda.
        """
        if not self.validacion_campo_requerido(codestado=codestado):
            raise ValueError("codestado es un campo requerido")
        params = {}        
        params["codestado"] = codestado
        params["recolecta"] = recolecta
        return self._solicitar(Configuracion.RUTA_ZOOM_CIUDADESOFI, "GET", parametros=(params or None))

    def obtener_sucursales(self, codciudad: int,idioma: Optional[int] = None):
        """Obtiene sucursales. La API puede esperar `codciudad`.
        Aceptamos ambos y enviamos el que corresponda.
        """
        if not self.validacion_campo_requerido(codciudad=codciudad):
            raise ValueError("codciudad es un campo requerido")
        params = {}        
        params["codciudad"] = codciudad
        params["idioma"] = idioma
        return self._solicitar(Configuracion.RUTA_ZOOM_SUCURSALES, "GET", parametros=(params or None))

    def obtener_tipo_ruta_envio(self,codciudadori: int,codciudaddes: int):
        """Obtiene tipo de ruta de envio. La API puede esperar `codciudadori` y `codciudaddes`.
        Aceptamos ambos y enviamos el que corresponda.
        """
        if not self.validacion_campo_requerido(codciudadori=codciudadori, codciudaddes=codciudaddes):
            raise ValueError("codciudadori y codciudaddes son campos requeridos")
        params = {}
        params["codciudadori"] = codciudadori
        params["codciudaddes"] = codciudaddes
        return self._solicitar(Configuracion.RUTA_ZOOM_TIPORUTAENVIO, "GET", parametros=(params or None))

    def obtener_modalidad_cod(self):
        return self._solicitar(Configuracion.RUTA_ZOOM_MODALIDADCOD, "GET")
        
    def obtener_estados(self,filtro: Optional[str] = None):
        """Obtiene estados. La API puede esperar `filtro`.
        Aceptamos ambos y enviamos el que corresponda.
        """
        params = {}
        params["filtro"] = filtro
        return self._solicitar(Configuracion.RUTA_ZOOM_ESTADOS, "GET", parametros=(params or None))

    def obtener_consulta_preciows(self, codciudad_origen:int,codciudad_destino:int,peso:float,
                                  valor_declarado:float,proteccion:bool,codigo_cliente:int,
                                  codservicio:int,modalidad:int,codoficina:int,
                                  retirar_oficina:bool):
        if not self.validacion_campo_requerido(codciudad_origen=codciudad_origen,codciudad_destino=codciudad_destino,peso=peso,
                                  valor_declarado=valor_declarado,proteccion=proteccion,codigo_cliente=codigo_cliente,
                                  codservicio=codservicio,modalidad=modalidad,codoficina=codoficina,
                                  retirar_oficina=retirar_oficina):
            raise ValueError("Todos los campos son requeridos")
        params = {}
        params["codciudad_origen"] = codciudad_origen
        params["codciudad_destino"] = codciudad_destino
        params["peso"] = peso
        params["valor_declarado"] = valor_declarado
        params["proteccion"] = proteccion
        params["codigo_cliente"] = codigo_cliente
        params["codservicio"] = codservicio
        params["modalidad"] = modalidad
        params["codoficina"] = codoficina
        params["retirar_oficina"] = retirar_oficina
        return self._solicitar(Configuracion.RUTA_ZOOM_CONSULTAPRECIOWS, "GET", parametros=params if params else None)

    def obtener_consulta_oficinaestadows(self,codestado:int):
        if not self.validacion_campo_requerido(codestado=codestado):
            raise ValueError("codestado es un campo requerido")
        params = {}
        params["codestado"] = codestado
        return self._solicitar(Configuracion.RUTA_ZOOM_GETOFICINAESTADOWS, "GET", parametros=params if params else None)

    def obtener_tipopreciows(self):
        return self._solicitar(Configuracion.RUTA_ZOOM_TIPOPRECIOWS, "GET")

#------- consultarpreciows
    # consulta de precios COD (1) y Nacional (2)
    def consultar_precio_cod_nacional(
        self,
        tipo_precio: int,
        tipo_tarifa: int,
        modalidad_tarifa: int,
        ciudad_remitente: int,
        ciudad_destinatario: int,
        oficina_retirar: int,
        cantidad_piezas: int,
        peso: float,
        #valor_mercancia: float = 0,
        valor_declarado: float = 0
        #tipo_envio: int = 1,
    ):
        """Consulta precio COD (tipo_precio=1)."""
        if not self.validacion_campo_requerido(
            tipo_precio=tipo_precio,
            tipo_tarifa=tipo_tarifa,
            modalidad_tarifa=modalidad_tarifa,
            ciudad_remitente=ciudad_remitente,
            ciudad_destinatario=ciudad_destinatario,
            cantidad_piezas=cantidad_piezas,
            peso=peso
        ):raise ValueError("Todos los campos son requeridos para consultar precio COD/Nacional")
        params = {
            "tipo_precio": tipo_precio,
            "tipo_tarifa": tipo_tarifa,
            "modalidad_tarifa": modalidad_tarifa,
            "ciudad_remitente": ciudad_remitente,
            "ciudad_destinatario": ciudad_destinatario,
            "oficina_retirar": oficina_retirar,
            "cantidad_piezas": cantidad_piezas,
            "peso": peso,
            #"valor_mercancia": valor_mercancia,
            "valor_declarado": valor_declarado
            #"tipo_envio": tipo_envio,
        }
        return self._solicitar(Configuracion.RUTA_ZOOM_CONSULTAPRECIOWS, "GET", parametros=params)
    
    #Consulta precio Internacional (tipo_precio=3) 
    def consultar_precio_internacional(
        self,
        pesob: float,
        fecha_envio: str,
        siglas_pd: str,
        ciudad_d: str,        
        siglas_po: str,
        ciudad_o: str,        
        valor_declarado: float,
        merdoc: str,
        codciudadori: int,
        alto: float,
        ancho: float,
        largo: float,
        zipcode_d: str = None,
        suburb_d: str = None,
        zipcode_o: str = None,
        suburb_o: str = None
    ):
        """Consulta precio Internacional (tipo_precio=3)."""
        if not self.validacion_campo_requerido(
            pesob=pesob,
            fecha_envio=fecha_envio,
            siglas_pd=siglas_pd,
            ciudad_d=ciudad_d,
            siglas_po=siglas_po,
            ciudad_o=ciudad_o,
            valor_declarado=valor_declarado,
            merdoc=merdoc,
            codciudadori=codciudadori,
            alto=alto,
            ancho=ancho,
            largo=largo
        ):raise ValueError("Todos los campos son requeridos para consultar precio Internacional")
        params = {
            "tipo_precio": 3,
            "pesob": pesob,
            "fecha_envio": fecha_envio,
            "siglas_pd": siglas_pd,
            "ciudad_d": ciudad_d,
            "siglas_po": siglas_po,
            "ciudad_o": ciudad_o,
            "valor_declarado": valor_declarado,
            "merdoc": merdoc,
            "codciudadori": codciudadori,
            "alto": alto,
            "ancho": ancho,
            "largo": largo,
        }

        # Para destino
        if not suburb_d and not zipcode_d:
            raise ErrorZoom("Se requiere zipcode_d o suburb_d para destino")
        elif suburb_d and zipcode_d:
            # Ambos presentes - incluir ambos
            params["zipcode_d"] = zipcode_d
            params["suburb_d"] = suburb_d
        elif not suburb_d:  # Solo zipcode_d
            params["zipcode_d"] = zipcode_d
        else:  # Solo suburb_d
            params["suburb_d"] = suburb_d
        # Para origen
        if not suburb_o and not zipcode_o:
            raise ErrorZoom("Se requiere zipcode_o o suburb_o para origen")
        elif suburb_o and zipcode_o:
            # Ambos presentes - incluir ambos
            params["zipcode_o"] = zipcode_o
            params["suburb_o"] = suburb_o
        elif not suburb_o:  # Solo zipcode_o
            params["zipcode_o"] = zipcode_o
        else:  # Solo suburb_o
            params["suburb_o"] = suburb_o
        
        return self._solicitar(Configuracion.RUTA_ZOOM_CONSULTAPRECIOWS, "GET", parametros=params)

    # Consulta precio Casillero Internacional Áereo (tipo_precio=4)
    def consultar_precio_casillero_aereo(
        self,
        codpais_remitente: int,
        codpais_destinatario: int,
        oficina_retirar: int,
        peso: float,
        valor_mercancia: float = 0,
        codtipoenv: int = 1,
        codservicio: int = 0,
        ciudad_destinatario: int = None,
    ):
        """Consulta precio Casillero Internacional Áereo (tipo_precio=4)."""
        if not self.validacion_campo_requerido(
            codpais_remitente=codpais_remitente,
            codpais_destinatario=codpais_destinatario,
            peso=peso,
            codtipoenv=codtipoenv,
            codservicio=codservicio
        ): raise ValueError("Todos los campos son requeridos para consultar precio Casillero Internacional Áereo")
        if codpais_destinatario == 124 and ciudad_destinatario is None: raise ValueError("ciudad_destinatario es requerido)")
        params = {
            "tipo_precio": 4,
            "tipo_tarifa": 90,
            "codpais_remitente": codpais_remitente,
            "codpais_destinatario": codpais_destinatario,
            "oficina_retirar": oficina_retirar,
            "peso": peso,
            "valor_mercancia": valor_mercancia,
            "codtipoenv": codtipoenv,
            "codservicio": codservicio,
        }
        if codpais_destinatario == 124: params["ciudad_destinatario"] = ciudad_destinatario
        return self._solicitar(Configuracion.RUTA_ZOOM_CONSULTAPRECIOWS, "GET", parametros=params)

    # Consulta precio Casillero Internacional Marítimo (tipo_precio=5)
    def consultar_precio_casillero_maritimo(
        self,
        codpais_remitente: int,
        codpais_destinatario: int,
        oficina_retirar: int,
        peso: float,
        valor_mercancia: float = 0,
        codtipoenv: int = 1,
        codservicio: int = 0,
        ciudad_destinatario: int = None,
        alto: float = None,
        ancho: float = None,
        largo: float = None,
    ):
        """Consulta precio Casillero Internacional Marítimo (tipo_precio=5)."""
        if not self.validacion_campo_requerido(
            codpais_remitente=codpais_remitente,
            codpais_destinatario=codpais_destinatario,
            codtipoenv=codtipoenv,
            codservicio=codservicio,
            alto=alto,
            ancho=ancho,
            largo=largo
        ): raise ValueError("Todos los campos son requeridos para consultar precio Casillero Internacional Marítimo")
        if codpais_destinatario == 124 and ciudad_destinatario is None: raise ValueError("ciudad_destinatario es requerido)")
        params = {
            "tipo_precio": 5,
            "tipo_tarifa": 102,
            "codpais_remitente": codpais_remitente,
            "codpais_destinatario": codpais_destinatario,
            "oficina_retirar": oficina_retirar,
            "peso": peso,
            "valor_mercancia": valor_mercancia,
            "codtipoenv": codtipoenv,
            "codservicio": codservicio,
            "alto": alto,
            "ancho": ancho,
            "largo": largo
        }
        if codpais_destinatario == 124 and ciudad_destinatario is not None:
            params["ciudad_destinatario"] = ciudad_destinatario
        return self._solicitar(Configuracion.RUTA_ZOOM_CONSULTAPRECIOWS, "GET", parametros=params)

    # Consulta precio Venta de Divisas Envío Internacional WU (tipo_precio=6)
    def consultar_precio_venta_divisas_internacional(
        self,
        monto: float,
    ):
        """Consulta precio Venta de Divisas Envío Internacional WU (tipo_precio=6)."""
        if not self.validacion_campo_requerido(monto=monto): raise ValueError("Todos los campos son requeridos para consultar precio Venta de Divisas Envío Internacional WU")  
        params = {
            "tipo_precio": 6,
            "monto": monto,
        }
        return self._solicitar(Configuracion.RUTA_ZOOM_CONSULTAPRECIOWS, "GET", parametros=params)

    # Consulta precio Compra de Divisas en Efectivo (tipo_precio=7)
    def consultar_precio_compra_divisas_efectivo(
        self,
        monto: float,
    ):
        """Consulta precio Compra de Divisas en Efectivo (tipo_precio=7)."""
        if not self.validacion_campo_requerido(monto=monto): raise ValueError("Todos los campos son requeridos para consultar precio Compra de Divisas en Efectivo")
        params = {
            "tipo_precio": 7,
            "monto": monto,
        }
        return self._solicitar(Configuracion.RUTA_ZOOM_CONSULTAPRECIOWS, "GET", parametros=params)

    # Consulta precio Venta en Divisas en Efectivo (tipo_precio=8)
    def consultar_precio_venta_divisas_efectivo(
        self,
        monto: float,
    ):
        """Consulta precio Venta en Divisas en Efectivo (tipo_precio=8)."""
        if not self.validacion_campo_requerido(monto=monto): raise ValueError("Todos los campos son requeridos para consultar precio Venta en Divisas en Efectivo")
        params = {
            "tipo_precio": 8,
            "monto": monto,
        }
        return self._solicitar(Configuracion.RUTA_ZOOM_CONSULTAPRECIOWS, "GET", parametros=params)
#------- consultarpreciows

    def obtener_consulta_trackingws(self,tipo_busqueda:int, numero:str, web:bool):
        if not self.validacion_campo_requerido(tipo_busqueda=tipo_busqueda, numero=numero, web=web):raise ValueError("Todos los campos son requeridos para consultar precio Venta en Divisas en Efectivo")
        params = {}
        params["tipo_busqueda"] = tipo_busqueda
        params["numero"] = numero
        params["web"] = web
        return self._solicitar(Configuracion.RUTA_ZOOM_CONSULTATRACKINGWS, "GET", parametros=params if params else None)

    def obtener_zonas_noservidasws(self,codciudad:int):
        if not self.validacion_campo_requerido(codciudad=codciudad):
            raise ValueError("codciudad es un campo requerido")
        params = {}
        params["codciudad"] = codciudad
        return self._solicitar(Configuracion.RUTA_ZOOM_ZONASNOSERVIDASWS, "GET", parametros=params if params else None) 

    def obtener_tipo_documento(self):
        return self._solicitar(Configuracion.RUTA_ZOOM_TIPODOCUMENTO, "GET")
        
    def obtener_listado_generico_ciudades(self):
        return self._solicitar(Configuracion.RUTA_ZOOM_LISTADOGENERICOCIUDADES, "GET")

    def informe_cliente(
        self,
        codcliente: int,
        clave: str,
        fechaDesde: str,
        fechaHasta: str
    ):
        if not self.validacion_campo_requerido(
            codcliente=codcliente,
            clave=clave,
            fechaDesde=fechaDesde,
            fechaHasta=fechaHasta
        ): raise ValueError("Todos los campos son requeridos para informe_cliente")
        datos = {
            "codcliente": codcliente,
            "clave": clave,
            "fechaDesde": fechaDesde,
            "fechaHasta": fechaHasta
        }
        return self._solicitar(Configuracion.RUTA_ZOOM_INFORMECLIENTE, "POST", cuerpo=datos, privado=True)

    def obtener_ciudadesws(self, tipoEntrega:int):
        if not self.validacion_campo_requerido(tipoEntrega=tipoEntrega):
            raise ValueError("tipoEntrega es un campo requerido")
        params = {}
        params["tipoEntrega"] = tipoEntrega
        return self._solicitar(Configuracion.RUTA_ZOOM_CIUDADESWS, "GET", parametros=params if params else None)


# ================== PROCEDIMIENTOS POST (ORDEN DOCUMENTACIÓN) ==================
    def zoom_cert(self, datos: dict):
        return self._solicitar(Configuracion.RUTA_ZOOM_ZOOMCERT, "POST", cuerpo=datos, privado=True)

    def servicios_clientes(self, datos: dict):
        return self._solicitar(Configuracion.RUTA_ZOOM_SERVICIOSCLIENTES, "POST", cuerpo=datos, privado=True)
    
    def create_shipment(self, datos: dict, token: str):
        return self._solicitar(Configuracion.RUTA_ZOOM_CREARSHIPMENT, "POST", cuerpo=datos, privado=True, usatoken=True, token=token)

    def guardar_remitente_ws(self, datos: dict, url_alternativa: Optional[str] = None):
        return self._solicitar(Configuracion.RUTA_ZOOM_GUARDARREMITENTEWS,  "POST", cuerpo=datos, privado=True, url_alternativa=True)
    
    def guardar_destinatarios_ws(self, datos: dict):
        return self._solicitar(Configuracion.RUTA_ZOOM_GUARDARDESTINATARIOSWS, "POST", cuerpo=datos, privado=True, url_alternativa=True)

    def crear_token(self, datos: dict):
        return self._solicitar(Configuracion.RUTA_ZOOM_CREARTOKEN, "POST", cuerpo=datos, privado=True)

    def create_shipment_internacional(self, datos: dict):
        return self._solicitar(Configuracion.RUTA_ZOOM_CREATE_SHIPMENT_INTERNACIONAL, "POST", cuerpo=datos, privado=True)

    def etiqueta_termica(self, datos: dict):
        return self._solicitar(Configuracion.RUTA_ZOOM_ETIQUETA_TERMICA, "POST", cuerpo=datos, privado=True)
    
    def crear_recolecta_ws(self, datos: dict):
        return self._solicitar(Configuracion.RUTA_ZOOM_CREARRECOLECTAWS, "POST", cuerpo=datos, privado=True)
    
    def crear_cliente_ws(self, datos: dict):
        return self._solicitar(Configuracion.RUTA_ZOOM_CREACIONCLIENTES, "POST", cuerpo=datos, privado=True)





