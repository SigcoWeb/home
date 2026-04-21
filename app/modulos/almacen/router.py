"""
Router del sub-módulo "Almacén" del módulo UI Tablas.
CRUD sobre sgc_almacen con respuestas HTMX (partials) y permisos granulares.
"""
from typing import Optional

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.almacen import SgcAlmacen
from app.models.catalogo_productos import SgcCatalogoGrupo
from app.models.usuarios import SgcUsuario
from app.core.auditoria import get_estacion
from app.core.permisos import require_permission
from app.core.templating import templates, build_context


router = APIRouter(tags=["tablas"])


@router.get("/tablas")
async def landing_tablas():
    return RedirectResponse(url="/tablas/almacen", status_code=302)


almacen_router = APIRouter(prefix="/tablas/almacen", tags=["tablas"])


async def _cargar_grupos(db: AsyncSession):
    result = await db.execute(select(SgcCatalogoGrupo).order_by(SgcCatalogoGrupo.nombre_grupo))
    return result.scalars().all()


def _parse_grupo(raw: Optional[str]) -> Optional[int]:
    if raw is None or raw == "" or raw == "None":
        return None
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


@almacen_router.get("", response_class=HTMLResponse)
async def listar_almacenes(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("TABLAS", "Almacenes")),
):
    result = await db.execute(select(SgcAlmacen).order_by(SgcAlmacen.id_almacen))
    almacenes = result.scalars().unique().all()
    return templates.TemplateResponse(
        "tablas/almacen/index.html",
        await build_context(request, db, current_user, almacenes=almacenes),
    )


@almacen_router.get("/nuevo", response_class=HTMLResponse)
async def form_nuevo(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("TABLAS", "Almacenes", "btn_nuevo")),
):
    grupos = await _cargar_grupos(db)
    return templates.TemplateResponse(
        "tablas/almacen/_modal_form.html",
        await build_context(request, db, current_user, almacen=None, grupos=grupos),
    )


@almacen_router.get("/{id_almacen}/editar", response_class=HTMLResponse)
async def form_editar(
    id_almacen: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("TABLAS", "Almacenes", "btn_editar")),
):
    almacen = await db.get(SgcAlmacen, id_almacen)
    if not almacen:
        raise HTTPException(status_code=404, detail="Almacén no encontrado")
    grupos = await _cargar_grupos(db)
    return templates.TemplateResponse(
        "tablas/almacen/_modal_form.html",
        await build_context(request, db, current_user, almacen=almacen, grupos=grupos),
    )


@almacen_router.post("", response_class=HTMLResponse)
async def crear_almacen(
    request: Request,
    nombre_almacen: str = Form(...),
    direccion: Optional[str] = Form(None),
    localidad: Optional[str] = Form(None),
    id_grupo: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("TABLAS", "Almacenes", "btn_nuevo")),
):
    almacen = SgcAlmacen(
        nombre_almacen=nombre_almacen.strip(),
        direccion=(direccion or None),
        localidad=(localidad or None),
        id_grupo=_parse_grupo(id_grupo),
        id_usuario=current_user.id_usuario,
        estacion=get_estacion(request),
    )
    db.add(almacen)
    await db.commit()
    result = await db.execute(
        select(SgcAlmacen).where(SgcAlmacen.id_almacen == almacen.id_almacen)
    )
    almacen = result.scalars().unique().one()
    return templates.TemplateResponse(
        "tablas/almacen/_row.html",
        await build_context(request, db, current_user, a=almacen),
    )


@almacen_router.put("/{id_almacen}", response_class=HTMLResponse)
async def actualizar_almacen(
    id_almacen: int,
    request: Request,
    nombre_almacen: str = Form(...),
    direccion: Optional[str] = Form(None),
    localidad: Optional[str] = Form(None),
    id_grupo: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("TABLAS", "Almacenes", "btn_editar")),
):
    almacen = await db.get(SgcAlmacen, id_almacen)
    if not almacen:
        raise HTTPException(status_code=404, detail="Almacén no encontrado")
    almacen.nombre_almacen = nombre_almacen.strip()
    almacen.direccion = direccion or None
    almacen.localidad = localidad or None
    almacen.id_grupo = _parse_grupo(id_grupo)
    almacen.id_usuario = current_user.id_usuario
    almacen.estacion = get_estacion(request)
    await db.commit()
    result = await db.execute(
        select(SgcAlmacen).where(SgcAlmacen.id_almacen == almacen.id_almacen)
    )
    almacen = result.scalars().unique().one()
    return templates.TemplateResponse(
        "tablas/almacen/_row.html",
        await build_context(request, db, current_user, a=almacen),
    )


@almacen_router.delete("/{id_almacen}")
async def eliminar_almacen(
    id_almacen: int,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("TABLAS", "Almacenes", "btn_eliminar")),
):
    almacen = await db.get(SgcAlmacen, id_almacen)
    if not almacen:
        raise HTTPException(status_code=404, detail="Almacén no encontrado")
    await db.delete(almacen)
    await db.commit()
    return Response(status_code=200, content="")


router.include_router(almacen_router)
