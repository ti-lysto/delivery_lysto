# Zoom Envíos API (Flask)

API en Flask para interactuar con los servicios de ZOOM (catálogos, precios, tracking y operaciones privadas de envíos y clientes).

## Requisitos

- Python 3.10+
- Paquetes: ver `requirements.txt`
	- Incluye `PyMySQL` para conexión MySQL

## Instalación

```bash
cd zoom/zoom_api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Crea un archivo `.env` (opcional) con tus variables:

```env
ZOOM_BASE_URL=https://sandbox-services.zoom.red
ZOOM_API_KEY=tu_api_key
ZOOM_FRASE_SECRETA=opcional_si_aplica
ZOOM_TIMEOUT=10
ZOOM_REINTENTOS=3
DEBUG=True
LOG_NIVEL=INFO
```

## Ejecutar en desarrollo

Ejecutando desde este directorio (`zoom/zoom_api`):

```bash
export FLASK_APP=application:app
flask run --host 0.0.0.0 --port 8000 --debug
```

Si ejecutas desde el raíz del repo o desde `zoom/`:

```bash
export FLASK_APP=zoom.zoom_api.application:app
flask run --host 0.0.0.0 --port 8000 --debug
```

## Endpoints de prueba
- `GET /health`
- `GET /info`
- `GET /api/catalog/estados`
- `GET /api/catalog/municipios?estado=<id>&ciudad=<id>`
- `GET /api/catalog/parroquias?codmunicipio=<id>&codciudad=<id>`
- `GET /api/catalog/ciudades?estado=<id>`
- `GET /api/catalog/oficinas?ciudad=<id>`
- `GET /api/precios?origen=...&destino=...&peso=...`
- `GET /api/tracking/<guia>`

### Proxy genérico (para el resto de endpoints del documento)

Permite probar cualquier ruta publicada por ZOOM mientras se implementan endpoints dedicados:

```bash
curl "http://localhost:8000/api/proxy/getEstados"            # GET sin auth
curl "http://localhost:8000/api/proxy/tracking/ABC123"       # GET tracking
curl -X POST "http://localhost:8000/api/proxy/crearCliente" \
	-H "Content-Type: application/json" \
	-H "X-API-Key: $ZOOM_API_KEY" \
	-d '{"nombre":"Ejemplo"}'
```

Reglas del proxy:
- Usa `X-API-Key` para marcar llamadas privadas (añade Authorization).
- Reenvía método, query params y JSON body tal cual.

Privados (requieren header `X-API-Key`):
- `POST /api/envios` (JSON con datos de envío)
- `POST /api/envios/<guia>/imprimir`
- `POST /api/clientes`

## Despliegue (Azure App Service)

Usa gunicorn con el objeto `app`:

Si el directorio de trabajo es `zoom/zoom_api`:

```bash
gunicorn -w 2 -k gthread -b 0.0.0.0:${PORT:-8000} application:app
```

Si el directorio de trabajo es el raíz del repo:

```bash
gunicorn -w 2 -k gthread -b 0.0.0.0:${PORT:-8000} zoom.zoom_api.application:app
```

Configura variables en App Settings y define el Startup command según corresponda.

## Base de datos (MySQL)

Variables soportadas (con defaults):

```env
DB_HOST=localhost
DB_PORT=3306
DB_NAME=LystoLocal
DB_USER=root
DB_PASSWORD=root
```

Para crear la base y una tabla de prueba (`pruebas_zoom`):

```bash
python -m zoom_api.scripts.init_db
```

Nota: solo crea la base/tabla. La integración de persistencia en endpoints se hará luego.
