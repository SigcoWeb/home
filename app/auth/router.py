from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from app.database import AsyncSessionLocal, get_db
from app.auth.utils import verify_password, crear_token
from app.core.models import Empresa
from app.core.auditoria import get_current_user_walter
from app.core.templating import templates as central_templates, build_context
from app.models.usuarios import SgcModulo, SgcUsuario

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    # Si ya está autenticado, redirigir al dashboard
    token = request.cookies.get("session_token")
    if token:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login_post(
    request: Request,
    usuario: str = Form(...),
    clave: str = Form(...),
):
    error = None

    # Buscar empresa por RUC o nombre de usuario master
    # En esta versión: el login es usuario operativo dentro de un tenant
    # El usuario ingresa: usuario (o DNI) + clave
    # Necesitamos identificar a qué tenant pertenece
    # Por ahora: login de usuario master (schema public) para el panel de Walter

    async with AsyncSessionLocal() as db:
        # Buscar en usuarios master (admin de empresa)
        result = await db.execute(
            text("""
                SELECT m.id, m.clave_hash, m.nombre, m.id_empresa, m.es_superadmin,
                       e.schema_db, e.ruc
                FROM sgc_sys_usuarios_master m
                LEFT JOIN sgc_sys_empresas e ON e.id = m.id_empresa
                WHERE m.email = :usuario AND m.activo = true
            """),
            {"usuario": usuario}
        )
        user = result.fetchone()

        if not user or not verify_password(clave, user.clave_hash):
            error = "Usuario o clave incorrectos"
            return templates.TemplateResponse(
                "login.html",
                {"request": request, "error": error},
                status_code=401
            )

        # Generar token
        schema = user.schema_db or "public"
        token = crear_token({
            "sub": str(user.id),
            "schema": schema,
            "nombre": user.nombre,
            "es_superadmin": user.es_superadmin,
        })

    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        max_age=3600 * 8,
        samesite="lax",
    )
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("session_token")
    return response


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(get_current_user_walter),
):
    result = await db.execute(
        select(SgcModulo).where(SgcModulo.activo.is_(True)).order_by(SgcModulo.orden)
    )
    modulos = result.scalars().all()

    return central_templates.TemplateResponse(
        "dashboard.html",
        await build_context(
            request, db, current_user,
            nombre=current_user.nombre_completo or current_user.usuario,
            modulos=modulos,
        ),
    )
