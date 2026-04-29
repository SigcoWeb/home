"""
Router del sub-modulo "Catalogo de Gastos" del modulo UI Tablas (zWalter-17).

CRUD sobre sgc_catalogo_gastos. Depende de sgc_unidades,
sgc_clasificador_gas1 y sgc_clasificador_gas2.

Provee endpoint JSON para cargar dinamicamente el dropdown de Clasificador 2
filtrado por Clasificador 1 seleccionado.
"""
from datetime import datetime

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.core.templating import templates, build_context
from app.core.auditoria import get_estacion
from app.core.permisos import require_permission
from app.models.catalogo_gastos import SgcCatalogoGastos
from app.models.clasificador_gastos import ClasificadorGas1, ClasificadorGas2
from app.models.unidades import UnidadMedida
from app.models.usuarios import SgcUsuario
from .schemas import CatalogoGastosPayload


router = APIRouter(prefix="/tablas/catalogo_gastos", tags=["tablas"])


# ============================================================
# LISTADO
# ============================================================

@router.get("", response_class=HTMLResponse)
async def listar(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "CatalogoGastos")
    ),
):
    result = await db.execute(
        select(SgcCatalogoGastos)
        .options(
            selectinload(SgcCatalogoGastos.unidad),
            selectinload(SgcCatalogoGastos.clagas1),
            selectinload(SgcCatalogoGastos.clagas2),
        )
        .order_by(SgcCatalogoGastos.codigo_gasto)
    )
    gastos = result.scalars().all()

    return templates.TemplateResponse(
        "tablas/catalogo_gastos/index.html",
        await build_context(request, db, current_user, gastos=gastos),
    )


# ============================================================
# MODAL: nuevo / editar
# ============================================================

@router.get("/nuevo", response_class=HTMLResponse)
async def form_nuevo(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "CatalogoGastos", "btn_nuevo")
    ),
):
    unidades = (await db.execute(
        select(UnidadMedida).order_by(UnidadMedida.nombre_unidad)
    )).scalars().all()
    clagas1s = (await db.execute(
        select(ClasificadorGas1).order_by(ClasificadorGas1.nombre_clagas1)
    )).scalars().all()

    response = templates.TemplateResponse(
        "tablas/catalogo_gastos/_modal_form.html",
        await build_context(
            request, db, current_user,
            gasto=None,
            unidades=unidades,
            clagas1s=clagas1s,
            clagas2s=[],
        ),
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response


@router.get("/{id_gasto}/editar", response_class=HTMLResponse)
async def form_editar(
    id_gasto: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "CatalogoGastos", "btn_editar")
    ),
):
    gasto = await db.get(SgcCatalogoGastos, id_gasto)
    if gasto is None:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    await db.refresh(gasto)

    unidades = (await db.execute(
        select(UnidadMedida).order_by(UnidadMedida.nombre_unidad)
    )).scalars().all()
    clagas1s = (await db.execute(
        select(ClasificadorGas1).order_by(ClasificadorGas1.nombre_clagas1)
    )).scalars().all()
    clagas2s = (await db.execute(
        select(ClasificadorGas2)
        .where(ClasificadorGas2.id_clagas1 == gasto.id_clagas1)
        .order_by(ClasificadorGas2.nombre_clagas2)
    )).scalars().all()

    response = templates.TemplateResponse(
        "tablas/catalogo_gastos/_modal_form.html",
        await build_context(
            request, db, current_user,
            gasto=gasto,
            unidades=unidades,
            clagas1s=clagas1s,
            clagas2s=clagas2s,
        ),
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response


# ============================================================
# JSON: opciones de Clasificador 2 filtradas por Clasificador 1
# ============================================================

@router.get("/clagas2_options/{id_clagas1}")
async def clagas2_options(
    id_clagas1: int,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "CatalogoGastos")
    ),
):
    result = await db.execute(
        select(ClasificadorGas2)
        .where(ClasificadorGas2.id_clagas1 == id_clagas1)
        .order_by(ClasificadorGas2.nombre_clagas2)
    )
    rows = result.scalars().all()
    return JSONResponse({
        "ok": True,
        "options": [
            {"id_clagas2": r.id_clagas2, "nombre_clagas2": r.nombre_clagas2}
            for r in rows
        ],
    })


# ============================================================
# GUARDAR (crear o actualizar)
# ============================================================

@router.post("")
async def guardar(
    payload: CatalogoGastosPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "CatalogoGastos", "btn_guardar")
    ),
):
    # Consistencia FK: id_clagas2 debe pertenecer a id_clagas1
    clagas2 = await db.get(ClasificadorGas2, payload.id_clagas2)
    if clagas2 is None or clagas2.id_clagas1 != payload.id_clagas1:
        return JSONResponse(
            {"ok": False, "error": "La sub-categoria no pertenece a la categoria seleccionada"},
            status_code=400,
        )

    estacion = get_estacion(request)
    try:
        if payload.id_gasto is None:
            gasto = SgcCatalogoGastos(
                estado=payload.estado,
                codigo_gasto=payload.codigo_gasto,
                nombre_gasto=payload.nombre_gasto,
                id_unidad=payload.id_unidad,
                id_clagas1=payload.id_clagas1,
                id_clagas2=payload.id_clagas2,
                precio_costo=payload.precio_costo,
                nota=payload.nota,
                id_usuario=current_user.id_usuario,
                fhcontrol=datetime.now(),
                estacion=estacion,
            )
            db.add(gasto)
        else:
            gasto = await db.get(SgcCatalogoGastos, payload.id_gasto)
            if gasto is None:
                raise HTTPException(status_code=404, detail="Gasto no encontrado")
            gasto.estado = payload.estado
            gasto.codigo_gasto = payload.codigo_gasto
            gasto.nombre_gasto = payload.nombre_gasto
            gasto.id_unidad = payload.id_unidad
            gasto.id_clagas1 = payload.id_clagas1
            gasto.id_clagas2 = payload.id_clagas2
            gasto.precio_costo = payload.precio_costo
            gasto.nota = payload.nota
            gasto.id_usuario = current_user.id_usuario
            gasto.fhcontrol = datetime.now()
            gasto.estacion = estacion

        await db.commit()
        await db.refresh(gasto)

        return JSONResponse({
            "ok": True,
            "id_gasto": gasto.id_gasto,
            "mensaje": "Guardado correctamente",
        })

    except IntegrityError as e:
        await db.rollback()
        msg = str(e.orig) if hasattr(e, "orig") else str(e)
        if "codigo_gasto" in msg.lower() or "unique" in msg.lower():
            return JSONResponse(
                {"ok": False, "error": f"Ya existe un gasto con el codigo '{payload.codigo_gasto}'"},
                status_code=400,
            )
        return JSONResponse(
            {"ok": False, "error": "Error de integridad al guardar"},
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


# ============================================================
# ELIMINAR
# ============================================================

@router.delete("/{id_gasto}")
async def eliminar(
    id_gasto: int,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "CatalogoGastos", "btn_eliminar")
    ),
):
    gasto = await db.get(SgcCatalogoGastos, id_gasto)
    if gasto is None:
        raise HTTPException(status_code=404, detail="Gasto no encontrado")
    try:
        await db.delete(gasto)
        await db.commit()
        return JSONResponse({"ok": True, "mensaje": "Gasto eliminado"})
    except IntegrityError:
        await db.rollback()
        return JSONResponse(
            {
                "ok": False,
                "error": "No se puede eliminar: el gasto esta siendo usado en otro modulo (ej: compras, asientos contables).",
            },
            status_code=400,
        )
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"ok": False, "error": f"Error al eliminar: {str(e)}"},
            status_code=500,
        )
