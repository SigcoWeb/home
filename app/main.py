from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import init_db
from app.migrations.runner import ejecutar_migraciones_pendientes
from app.auth.middleware import auth_middleware
from app.auth.router import router as auth_router
from app.auth import utils as auth_utils  # noqa

# Importar todos los modelos para que create_all los registre
from app.core import models as core_models          # noqa
from app.licencias import models as lic_models      # noqa

# Modelos de Walter — app/models/
from app.models import agenda_clientes              # noqa
from app.models import agenda_proveedores           # noqa
from app.models import almacen                      # noqa
from app.models import catalogo_gastos              # noqa
from app.models import catalogo_productos           # noqa
from app.models import clasificador_clientes        # noqa
from app.models import clasificador_gastos          # noqa
from app.models import clasificador_productos       # noqa
from app.models import config_globales              # noqa
from app.models import config_numerador             # noqa
from app.models import config_rutas                 # noqa
from app.models import doc_identidad                # noqa
from app.models import docsunat                     # noqa
from app.models import empleados                    # noqa
from app.models import empresa                      # noqa
from app.models import entidades                    # noqa
from app.models import forma_pago                   # noqa
from app.models import guia_ingreso                 # noqa
from app.models import guia_salida                  # noqa
from app.models import marcas                       # noqa
from app.models import operaciones                  # noqa
from app.models import operaciones_gre              # noqa
from app.models import tesoreria                    # noqa
from app.models import tipocambio                   # noqa
from app.models import transportistas               # noqa
from app.models import ubigeo                       # noqa
from app.models import unidades                     # noqa
from app.models import usuarios                     # noqa


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[sigcoWeb] Iniciando en modo: {settings.MODO_DEPLOY}")
    # Orden correcto:
    # 1) Migraciones primero: crean y ajustan el schema segun los .sql versionados.
    # 2) create_all despues: solo como safety net, crea tablas que tengan modelo
    #    Python pero aun no tengan migracion propia. NUNCA modifica tablas existentes.
    # Regla: todo cambio de schema nuevo va por migracion SQL. Ver app/modulos/README.md.
    await ejecutar_migraciones_pendientes()
    await init_db()
    yield
    print("[sigcoWeb] Cerrando...")


app = FastAPI(
    title=settings.APP_NOMBRE,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.ENTORNO == "development" else None,
    redoc_url=None,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(BaseHTTPMiddleware, dispatch=auth_middleware)
app.include_router(auth_router)

# Módulo UI "Tablas" (zWalter-01)
from app.modulos.almacen.router import router as almacen_router
from app.modulos.catalogo.router import router as catalogo_router
from app.modulos.transportistas.router import router as transportistas_router
# Módulo UI "Configuración" (zWalter-02 + zWalter-04)
from app.modulos.usuarios.router import router as usuarios_router
from app.modulos.permisos.router import router as permisos_router

app.include_router(almacen_router)
app.include_router(catalogo_router)
app.include_router(transportistas_router)
app.include_router(usuarios_router)
app.include_router(permisos_router)

# Dashboard: endpoint puente /ir-a-modulo/{id} (zWalter-05)
from app.modulos.dashboard.router import router as dashboard_router
app.include_router(dashboard_router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/walter", response_class=HTMLResponse)
async def walter(request: Request):
    return templates.TemplateResponse("preguntas.html", {"request": request})


@app.get("/ping")
async def ping():
    return {"status": "ok", "version": settings.APP_VERSION, "modo": settings.MODO_DEPLOY}