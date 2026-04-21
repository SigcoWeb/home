"""
Router del sub-módulo "Usuarios" del módulo UI Configuración.
CRUD sobre sgc_usuarios con hashing compartido con sgc_sys_usuarios_master.
Permisos aplicados via require_permission (dependency-factory).
"""
from typing import Optional

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.usuarios import SgcUsuario
from app.core.models import UsuarioMaster
from app.auth.utils import hash_password
from app.core.auditoria import get_estacion
from app.core.permisos import require_permission
from app.core.templating import templates, build_context


router = APIRouter(tags=["configuracion"])


@router.get("/config")
async def landing_config():
    return RedirectResponse(url="/config/usuarios", status_code=302)


usuarios_router = APIRouter(prefix="/config/usuarios", tags=["configuracion"])


def _parse_sys_master(raw: Optional[str]) -> Optional[int]:
    if raw is None or raw.strip() == "":
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _parse_activo(raw: Optional[str]) -> bool:
    return (raw or "").lower() in {"on", "true", "1", "yes"}


@usuarios_router.get("", response_class=HTMLResponse)
async def listar_usuarios(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("CONFIGURACIONES", "Usuarios")),
):
    result = await db.execute(select(SgcUsuario).order_by(SgcUsuario.id_usuario))
    usuarios = result.scalars().all()
    return templates.TemplateResponse(
        "configuracion/usuarios/index.html",
        await build_context(request, db, current_user, usuarios=usuarios),
    )


@usuarios_router.get("/nuevo", response_class=HTMLResponse)
async def form_nuevo(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("CONFIGURACIONES", "Usuarios", "btn_nuevo")),
):
    return templates.TemplateResponse(
        "configuracion/usuarios/_modal_form.html",
        await build_context(request, db, current_user, usuario=None),
    )


@usuarios_router.get("/{id_usuario}/editar", response_class=HTMLResponse)
async def form_editar(
    id_usuario: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("CONFIGURACIONES", "Usuarios", "btn_editar")),
):
    u = await db.get(SgcUsuario, id_usuario)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return templates.TemplateResponse(
        "configuracion/usuarios/_modal_form.html",
        await build_context(request, db, current_user, usuario=u),
    )


@usuarios_router.post("", response_class=HTMLResponse)
async def crear_usuario(
    request: Request,
    usuario: str = Form(...),
    clave: str = Form(...),
    nombre_completo: Optional[str] = Form(None),
    activo: Optional[str] = Form(None),
    id_sys_master: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("CONFIGURACIONES", "Usuarios", "btn_nuevo")),
):
    nuevo = SgcUsuario(
        usuario=usuario.strip(),
        clave=hash_password(clave),
        nombre_completo=(nombre_completo or None),
        activo=_parse_activo(activo) if activo is not None else True,
        id_sys_master=_parse_sys_master(id_sys_master),
        id_usuario_creador=current_user.id_usuario,
        estacion=get_estacion(request),
    )
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return templates.TemplateResponse(
        "configuracion/usuarios/_row.html",
        await build_context(request, db, current_user, u=nuevo),
    )


@usuarios_router.put("/{id_usuario}", response_class=HTMLResponse)
async def actualizar_usuario(
    id_usuario: int,
    request: Request,
    usuario: str = Form(...),
    clave: Optional[str] = Form(None),
    nombre_completo: Optional[str] = Form(None),
    activo: Optional[str] = Form(None),
    id_sys_master: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("CONFIGURACIONES", "Usuarios", "btn_editar")),
):
    u = await db.get(SgcUsuario, id_usuario)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    u.usuario = usuario.strip()
    u.nombre_completo = (nombre_completo or None)
    u.activo = _parse_activo(activo)
    u.id_sys_master = _parse_sys_master(id_sys_master)
    u.estacion = get_estacion(request)
    u.id_usuario_creador = current_user.id_usuario

    if clave and clave.strip():
        u.clave = hash_password(clave)

    await db.commit()
    await db.refresh(u)
    return templates.TemplateResponse(
        "configuracion/usuarios/_row.html",
        await build_context(request, db, current_user, u=u),
    )


@usuarios_router.delete("/{id_usuario}")
async def eliminar_usuario(
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("CONFIGURACIONES", "Usuarios", "btn_eliminar")),
):
    u = await db.get(SgcUsuario, id_usuario)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    await db.delete(u)
    await db.commit()
    return Response(status_code=200, content="")


@usuarios_router.get("/{id_usuario}/reset-password", response_class=HTMLResponse)
async def form_reset_password(
    id_usuario: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("CONFIGURACIONES", "Usuarios", "btn_otro")),
):
    u = await db.get(SgcUsuario, id_usuario)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return templates.TemplateResponse(
        "configuracion/usuarios/_modal_reset_password.html",
        await build_context(request, db, current_user, usuario=u),
    )


@usuarios_router.put("/{id_usuario}/clave", response_class=HTMLResponse)
async def reset_password(
    id_usuario: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("CONFIGURACIONES", "Usuarios", "btn_otro")),
):
    form = await request.form()
    nueva = (form.get("nueva_clave") or "").strip()
    confirmar = (form.get("confirmar_clave") or "").strip()

    if not nueva or len(nueva) < 4:
        raise HTTPException(status_code=400, detail="La clave debe tener al menos 4 caracteres")
    if nueva != confirmar:
        raise HTTPException(status_code=400, detail="Las claves no coinciden")

    user = await db.get(SgcUsuario, id_usuario)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    hashed = hash_password(nueva)
    user.clave = hashed

    if user.id_sys_master:
        sys_user = await db.get(UsuarioMaster, user.id_sys_master)
        if sys_user:
            sys_user.clave_hash = hashed

    await db.commit()

    # HTMX OOB: cerrar modal + mostrar toast.
    return HTMLResponse(
        '<div id="modal-root" hx-swap-oob="true"></div>'
        '<div id="toast-root" hx-swap-oob="true">'
        '  <div class="toast-ok">Clave actualizada correctamente.</div>'
        '</div>',
        status_code=200,
    )


router.include_router(usuarios_router)
