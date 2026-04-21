"""
Router del sub-módulo "Permisos" del módulo UI Configuración.
Gestión end-to-end de la matriz de permisos por usuario.
"""
from typing import Optional

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.usuarios import (
    SgcUsuario,
    SgcModulo,
    SgcOpcion,
    SgcUsuarioModulo,
    SgcUsuarioOpcion,
)
from app.core.permisos import require_permission
from app.core.templating import templates, build_context


router = APIRouter(prefix="/config/permisos", tags=["configuracion"])


async def _cargar_estructura(db: AsyncSession):
    """Devuelve (usuarios, modulos_con_opciones) listos para el template."""
    usuarios = (
        await db.execute(select(SgcUsuario).order_by(SgcUsuario.usuario))
    ).scalars().all()

    modulos = (
        await db.execute(select(SgcModulo).order_by(SgcModulo.id_modulo))
    ).scalars().all()

    opciones = (
        await db.execute(select(SgcOpcion).order_by(SgcOpcion.id_modulo, SgcOpcion.nombre))
    ).scalars().all()

    # Solo incluir módulos que tienen al menos una opción seedeada — evita filas vacías.
    modulos_con_opciones = {}
    for m in modulos:
        ops_del_modulo = [o for o in opciones if o.id_modulo == m.id_modulo]
        if ops_del_modulo:
            modulos_con_opciones[m] = ops_del_modulo

    return usuarios, modulos_con_opciones


async def _cargar_permisos_actuales(db: AsyncSession, id_usuario: int) -> dict:
    """
    Devuelve {id_opcion: SgcUsuarioOpcion} con las filas actuales del usuario.
    Usado por el template para pre-marcar checkboxes.
    """
    rows = (
        await db.execute(
            select(SgcUsuarioOpcion).where(SgcUsuarioOpcion.id_usuario == id_usuario)
        )
    ).scalars().all()
    return {r.id_opcion: r for r in rows}


async def _render_pantalla(
    request: Request,
    db: AsyncSession,
    current_user: SgcUsuario,
    usuario_seleccionado: Optional[SgcUsuario],
):
    usuarios, modulos_con_opciones = await _cargar_estructura(db)
    permisos_actuales = (
        await _cargar_permisos_actuales(db, usuario_seleccionado.id_usuario)
        if usuario_seleccionado
        else {}
    )
    return templates.TemplateResponse(
        "configuracion/permisos/index.html",
        await build_context(
            request, db, current_user,
            usuarios=usuarios,
            usuario_seleccionado=usuario_seleccionado,
            modulos_con_opciones=modulos_con_opciones,
            permisos_actuales=permisos_actuales,
        ),
    )


@router.get("", response_class=HTMLResponse)
async def pantalla_permisos(
    request: Request,
    id_usuario: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("CONFIGURACIONES", "Permisos")),
):
    usuario_seleccionado = None
    if id_usuario:
        usuario_seleccionado = await db.get(SgcUsuario, id_usuario)
    return await _render_pantalla(request, db, current_user, usuario_seleccionado)


@router.get("/usuario-partial", response_class=HTMLResponse)
async def matriz_partial(
    request: Request,
    id_usuario: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("CONFIGURACIONES", "Permisos")),
):
    if not id_usuario:
        return HTMLResponse(
            '<p class="permisos-placeholder">Selecciona un usuario para gestionar sus permisos.</p>'
        )
    usuario_seleccionado = await db.get(SgcUsuario, id_usuario)
    if not usuario_seleccionado:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    _, modulos_con_opciones = await _cargar_estructura(db)
    permisos_actuales = await _cargar_permisos_actuales(db, id_usuario)
    return templates.TemplateResponse(
        "configuracion/permisos/_matriz.html",
        await build_context(
            request, db, current_user,
            usuario_seleccionado=usuario_seleccionado,
            modulos_con_opciones=modulos_con_opciones,
            permisos_actuales=permisos_actuales,
        ),
    )


@router.post("/usuario/{id_usuario}")
async def guardar_permisos(
    id_usuario: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("CONFIGURACIONES", "Permisos", "btn_guardar")),
):
    form = await request.form()
    target = await db.get(SgcUsuario, id_usuario)
    if not target:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    opciones = (
        await db.execute(select(SgcOpcion))
    ).scalars().all()
    modulos = (
        await db.execute(select(SgcModulo))
    ).scalars().all()
    modulos_por_id = {m.id_modulo: m for m in modulos}

    # Salvaguarda: admin no puede quitarse su propio CONFIGURACIONES.Permisos.
    if id_usuario == current_user.id_usuario:
        for op in opciones:
            modulo = modulos_por_id.get(op.id_modulo)
            if modulo and modulo.nombre == "CONFIGURACIONES" and op.nombre == "Permisos":
                if f"activo_{op.id_opcion}" not in form:
                    raise HTTPException(
                        status_code=400,
                        detail="No puedes quitarte tus propios permisos de gestión de permisos",
                    )

    # Estrategia simple: wipe + re-insert.
    await db.execute(delete(SgcUsuarioOpcion).where(SgcUsuarioOpcion.id_usuario == id_usuario))
    await db.execute(delete(SgcUsuarioModulo).where(SgcUsuarioModulo.id_usuario == id_usuario))

    modulos_activos = set()

    for op in opciones:
        if f"activo_{op.id_opcion}" not in form:
            continue
        modulos_activos.add(op.id_modulo)
        db.add(SgcUsuarioOpcion(
            id_usuario=id_usuario,
            id_modulo=op.id_modulo,
            id_opcion=op.id_opcion,
            nombre_opcion=op.nombre,
            descrip_opcion=op.descripcion,
            btn_nuevo=    f"btn_nuevo_{op.id_opcion}"    in form,
            btn_editar=   f"btn_editar_{op.id_opcion}"   in form,
            btn_eliminar= f"btn_eliminar_{op.id_opcion}" in form,
            btn_pdf=      f"btn_pdf_{op.id_opcion}"      in form,
            btn_excel=    f"btn_excel_{op.id_opcion}"    in form,
            btn_guardar=  f"btn_guardar_{op.id_opcion}"  in form,
            btn_otro=     f"btn_otro_{op.id_opcion}"     in form,
            activo=True,
        ))

    for id_modulo in modulos_activos:
        modulo = modulos_por_id.get(id_modulo)
        if not modulo:
            continue
        db.add(SgcUsuarioModulo(
            id_usuario=id_usuario,
            id_modulo=id_modulo,
            nombre_modulo=modulo.nombre,
            descrip_modulo=modulo.descripcion,
            activo=True,
        ))

    await db.commit()

    return RedirectResponse(
        url=f"/config/permisos?id_usuario={id_usuario}&ok=1",
        status_code=303,
    )
