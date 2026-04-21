"""
Endpoint puente /ir-a-modulo/{id}.

- Si el módulo no está implementado → pantalla "Próximamente" (upsell).
- Si está implementado pero el usuario no tiene acceso → pantalla "Sin acceso" (upsell).
- Si todo OK → redirect 302 al url_destino del módulo.

La grilla del dashboard siempre muestra los 12 módulos — el filtrado es
intencional aquí (ver zWalter-05, decisión "Opción B refinada").
"""
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.usuarios import SgcModulo, SgcUsuario, SgcUsuarioModulo
from app.core.auditoria import get_current_user_walter
from app.core.templating import templates, build_context


router = APIRouter()


@router.get("/ir-a-modulo/{id_modulo}", response_class=HTMLResponse)
async def ir_a_modulo(
    id_modulo: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(get_current_user_walter),
):
    modulo = await db.get(SgcModulo, id_modulo)
    if modulo is None:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")

    nombre = current_user.nombre_completo or current_user.usuario

    if not modulo.implementado:
        return templates.TemplateResponse(
            "_proximamente.html",
            await build_context(request, db, current_user, modulo=modulo, nombre=nombre),
        )

    result = await db.execute(
        select(SgcUsuarioModulo).where(
            SgcUsuarioModulo.id_usuario == current_user.id_usuario,
            SgcUsuarioModulo.id_modulo == id_modulo,
            SgcUsuarioModulo.activo.is_(True),
        )
    )
    acceso = result.scalars().first()
    if acceso is None:
        return templates.TemplateResponse(
            "_sin_acceso.html",
            await build_context(request, db, current_user, modulo=modulo, nombre=nombre),
        )

    return RedirectResponse(url=modulo.url_destino, status_code=302)
