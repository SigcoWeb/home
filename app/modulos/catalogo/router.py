"""
Router del sub-módulo "Grupos" del módulo UI Tablas.
CRUD sobre sgc_catalogo_grupo con respuestas HTMX (partials) y permisos granulares.
"""
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.catalogo_productos import SgcCatalogoGrupo
from app.models.usuarios import SgcUsuario
from app.core.auditoria import get_estacion
from app.core.permisos import require_permission
from app.core.templating import templates, build_context


router = APIRouter(prefix="/tablas/grupos", tags=["tablas"])


@router.get("", response_class=HTMLResponse)
async def listar_grupos(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("TABLAS", "Grupos")),
):
    result = await db.execute(select(SgcCatalogoGrupo).order_by(SgcCatalogoGrupo.id_grupo))
    grupos = result.scalars().all()
    return templates.TemplateResponse(
        "tablas/grupos/index.html",
        await build_context(request, db, current_user, grupos=grupos),
    )


@router.get("/nuevo", response_class=HTMLResponse)
async def form_nuevo(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("TABLAS", "Grupos", "btn_nuevo")),
):
    return templates.TemplateResponse(
        "tablas/grupos/_modal_form.html",
        await build_context(request, db, current_user, grupo=None),
    )


@router.get("/{id_grupo}/editar", response_class=HTMLResponse)
async def form_editar(
    id_grupo: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("TABLAS", "Grupos", "btn_editar")),
):
    grupo = await db.get(SgcCatalogoGrupo, id_grupo)
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    return templates.TemplateResponse(
        "tablas/grupos/_modal_form.html",
        await build_context(request, db, current_user, grupo=grupo),
    )


@router.post("", response_class=HTMLResponse)
async def crear_grupo(
    request: Request,
    nombre_grupo: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("TABLAS", "Grupos", "btn_nuevo")),
):
    grupo = SgcCatalogoGrupo(
        nombre_grupo=nombre_grupo.strip(),
        id_usuario=current_user.id_usuario,
        estacion=get_estacion(request),
    )
    db.add(grupo)
    await db.commit()
    await db.refresh(grupo)
    return templates.TemplateResponse(
        "tablas/grupos/_row.html",
        await build_context(request, db, current_user, g=grupo),
    )


@router.put("/{id_grupo}", response_class=HTMLResponse)
async def actualizar_grupo(
    id_grupo: int,
    request: Request,
    nombre_grupo: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("TABLAS", "Grupos", "btn_editar")),
):
    grupo = await db.get(SgcCatalogoGrupo, id_grupo)
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    grupo.nombre_grupo = nombre_grupo.strip()
    grupo.id_usuario = current_user.id_usuario
    grupo.estacion = get_estacion(request)
    await db.commit()
    await db.refresh(grupo)
    return templates.TemplateResponse(
        "tablas/grupos/_row.html",
        await build_context(request, db, current_user, g=grupo),
    )


@router.delete("/{id_grupo}")
async def eliminar_grupo(
    id_grupo: int,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("TABLAS", "Grupos", "btn_eliminar")),
):
    grupo = await db.get(SgcCatalogoGrupo, id_grupo)
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    await db.delete(grupo)
    await db.commit()
    return Response(status_code=200, content="")
