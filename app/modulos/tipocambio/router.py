"""
Router del sub-modulo "Tipo de Cambio" del modulo UI Tablas (zWalter-08).

CRUD simple, sin sub-modal ni relaciones 1-a-N.
Constraint UNIQUE sobre fecha_tc: un registro por dia.
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.core.templating import templates, build_context
from app.core.auditoria import get_estacion
from app.core.permisos import require_permission
from app.models.tipocambio import SgcTipoCambio
from app.models.usuarios import SgcUsuario
from .schemas import TipoCambioPayload


router = APIRouter(prefix="/tablas/tipocambio", tags=["tablas"])


# ======================================================
# LISTADO
# ======================================================

@router.get("", response_class=HTMLResponse)
async def listar(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("TABLAS", "TipoCambio")),
):
    result = await db.execute(
        select(SgcTipoCambio).order_by(desc(SgcTipoCambio.fecha_tc))
    )
    tipos_cambio = result.scalars().all()

    return templates.TemplateResponse(
        "tablas/tipocambio/index.html",
        await build_context(request, db, current_user, tipos_cambio=tipos_cambio),
    )


# ======================================================
# FORMULARIO (nuevo o editar) -> devuelve modal
# ======================================================

@router.get("/nuevo", response_class=HTMLResponse)
async def form_nuevo(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "TipoCambio", "btn_nuevo")
    ),
):
    response = templates.TemplateResponse(
        "tablas/tipocambio/_modal_form.html",
        await build_context(request, db, current_user, tipocambio=None),
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response


@router.get("/{id_tc}/editar", response_class=HTMLResponse)
async def form_editar(
    id_tc: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "TipoCambio", "btn_editar")
    ),
):
    result = await db.execute(
        select(SgcTipoCambio).where(SgcTipoCambio.id_tc == id_tc)
    )
    tipocambio = result.scalar_one_or_none()
    if tipocambio is None:
        raise HTTPException(status_code=404, detail="Tipo de cambio no encontrado")

    # Forzar lectura fresca desde DB (patron aprendido en zW-07)
    await db.refresh(tipocambio)

    response = templates.TemplateResponse(
        "tablas/tipocambio/_modal_form.html",
        await build_context(request, db, current_user, tipocambio=tipocambio),
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response


# ======================================================
# GUARDAR (crear o actualizar)
# ======================================================

@router.post("")
async def guardar(
    payload: TipoCambioPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "TipoCambio", "btn_guardar")
    ),
):
    """
    Crea o actualiza un tipo de cambio.
    Valida UNIQUE por fecha a nivel DB.
    """
    estacion = get_estacion(request)
    try:
        if payload.id_tc is None:
            # Crear
            tc = SgcTipoCambio(
                fecha_tc=payload.fecha_tc,
                compra=payload.compra,
                venta=payload.venta,
                compra_sunat=payload.compra_sunat or 0,
                venta_sunat=payload.venta_sunat or 0,
                nota=payload.nota,
                id_usuario=current_user.id_usuario,
                estacion=estacion,
            )
            db.add(tc)
        else:
            # Actualizar
            result = await db.execute(
                select(SgcTipoCambio).where(SgcTipoCambio.id_tc == payload.id_tc)
            )
            tc = result.scalar_one_or_none()
            if tc is None:
                raise HTTPException(status_code=404, detail="Tipo de cambio no encontrado")
            tc.fecha_tc = payload.fecha_tc
            tc.compra = payload.compra
            tc.venta = payload.venta
            tc.compra_sunat = payload.compra_sunat or 0
            tc.venta_sunat = payload.venta_sunat or 0
            tc.nota = payload.nota
            tc.id_usuario = current_user.id_usuario
            tc.estacion = estacion

        await db.commit()
        await db.refresh(tc)

        return JSONResponse({
            "ok": True,
            "id_tc": tc.id_tc,
            "mensaje": "Guardado correctamente",
        })

    except IntegrityError:
        await db.rollback()
        return JSONResponse(
            {
                "ok": False,
                "error": f"Ya existe un tipo de cambio para la fecha {payload.fecha_tc.isoformat()}",
            },
            status_code=400,
        )
    except HTTPException:
        await db.rollback()
        raise
    except ValueError as e:
        await db.rollback()
        return JSONResponse({"ok": False, "error": str(e)}, status_code=400)
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"ok": False, "error": f"Error al guardar: {str(e)}"},
            status_code=500,
        )


# ======================================================
# ELIMINAR
# ======================================================

@router.delete("/{id_tc}")
async def eliminar(
    id_tc: int,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "TipoCambio", "btn_eliminar")
    ),
):
    result = await db.execute(
        select(SgcTipoCambio).where(SgcTipoCambio.id_tc == id_tc)
    )
    tc = result.scalar_one_or_none()
    if tc is None:
        raise HTTPException(status_code=404, detail="Tipo de cambio no encontrado")
    await db.delete(tc)
    await db.commit()
    return JSONResponse({"ok": True, "mensaje": "Tipo de cambio eliminado"})
