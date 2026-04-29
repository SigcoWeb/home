"""
Router del sub-modulo "Clasificador de Gastos" del modulo UI Tablas (zWalter-16).

Panel doble (Nivel 1 + Nivel 2) con HTMX para filtrado del Nivel 2 al
seleccionar una fila del Nivel 1.

Eliminacion de Nivel 1 con sub-categorias se bloquea con mensaje amigable.
"""
from datetime import datetime

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.core.templating import templates, build_context
from app.core.auditoria import get_estacion
from app.core.permisos import require_permission
from app.models.clasificador_gastos import ClasificadorGas1, ClasificadorGas2
from app.models.usuarios import SgcUsuario
from .schemas import ClasGas1Payload, ClasGas2Payload


router = APIRouter(prefix="/tablas/clasificador_gastos", tags=["tablas"])


# ============================================================
# LISTADO PRINCIPAL (panel doble)
# ============================================================

@router.get("", response_class=HTMLResponse)
async def listar(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "ClasificadorGastos")
    ),
):
    nivel1_result = await db.execute(
        select(ClasificadorGas1).order_by(ClasificadorGas1.nombre_clagas1)
    )
    nivel1 = nivel1_result.scalars().all()

    nivel2 = []
    primer_id_clagas1 = nivel1[0].id_clagas1 if nivel1 else None
    if primer_id_clagas1:
        nivel2_result = await db.execute(
            select(ClasificadorGas2)
            .where(ClasificadorGas2.id_clagas1 == primer_id_clagas1)
            .order_by(ClasificadorGas2.nombre_clagas2)
        )
        nivel2 = nivel2_result.scalars().all()

    return templates.TemplateResponse(
        "tablas/clasificador_gastos/index.html",
        await build_context(
            request, db, current_user,
            nivel1=nivel1,
            nivel2=nivel2,
            selected_clagas1=primer_id_clagas1,
        ),
    )


# ============================================================
# FRAGMENTO HTMX: panel Nivel 2 filtrado por Nivel 1
# ============================================================

@router.get("/nivel2/lista/{id_clagas1}", response_class=HTMLResponse)
async def listar_nivel2(
    id_clagas1: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "ClasificadorGastos")
    ),
):
    nivel2_result = await db.execute(
        select(ClasificadorGas2)
        .where(ClasificadorGas2.id_clagas1 == id_clagas1)
        .order_by(ClasificadorGas2.nombre_clagas2)
    )
    nivel2 = nivel2_result.scalars().all()

    return templates.TemplateResponse(
        "tablas/clasificador_gastos/_panel_nivel2.html",
        await build_context(
            request, db, current_user,
            nivel2=nivel2,
            selected_clagas1=id_clagas1,
        ),
    )


# ============================================================
# NIVEL 1 - CRUD
# ============================================================

@router.get("/nivel1/nuevo", response_class=HTMLResponse)
async def modal_nuevo_n1(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "ClasificadorGastos", "btn_nuevo")
    ),
):
    response = templates.TemplateResponse(
        "tablas/clasificador_gastos/_modal_form.html",
        await build_context(
            request, db, current_user,
            nivel=1, registro=None, modo="nuevo",
            id_padre=None, nombre_padre=None,
        ),
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response


@router.get("/nivel1/{id_clagas1}/editar", response_class=HTMLResponse)
async def modal_editar_n1(
    id_clagas1: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "ClasificadorGastos", "btn_editar")
    ),
):
    reg = await db.get(ClasificadorGas1, id_clagas1)
    if reg is None:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    await db.refresh(reg)
    response = templates.TemplateResponse(
        "tablas/clasificador_gastos/_modal_form.html",
        await build_context(
            request, db, current_user,
            nivel=1, registro=reg, modo="editar",
            id_padre=None, nombre_padre=None,
        ),
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response


@router.post("/nivel1")
async def crear_n1(
    payload: ClasGas1Payload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "ClasificadorGastos", "btn_guardar")
    ),
):
    estacion = get_estacion(request)
    try:
        reg = ClasificadorGas1(
            nombre_clagas1=payload.nombre,
            id_usuario=current_user.id_usuario,
            fhcontrol=datetime.now(),
            estacion=estacion,
        )
        db.add(reg)
        await db.commit()
        await db.refresh(reg)
        return JSONResponse({
            "ok": True,
            "id_clagas1": reg.id_clagas1,
            "mensaje": "Guardado correctamente",
        }, status_code=201)
    except IntegrityError:
        await db.rollback()
        return JSONResponse(
            {"ok": False, "error": f"Ya existe una categoria con el nombre '{payload.nombre}'"},
            status_code=400,
        )
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"ok": False, "error": f"Error al guardar: {str(e)}"},
            status_code=500,
        )


@router.put("/nivel1/{id_clagas1}")
async def actualizar_n1(
    id_clagas1: int,
    payload: ClasGas1Payload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "ClasificadorGastos", "btn_guardar")
    ),
):
    reg = await db.get(ClasificadorGas1, id_clagas1)
    if reg is None:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    estacion = get_estacion(request)
    try:
        reg.nombre_clagas1 = payload.nombre
        reg.id_usuario = current_user.id_usuario
        reg.fhcontrol = datetime.now()
        reg.estacion = estacion
        await db.commit()
        await db.refresh(reg)
        return JSONResponse({"ok": True, "id_clagas1": reg.id_clagas1})
    except IntegrityError:
        await db.rollback()
        return JSONResponse(
            {"ok": False, "error": f"Ya existe una categoria con el nombre '{payload.nombre}'"},
            status_code=400,
        )
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"ok": False, "error": f"Error al actualizar: {str(e)}"},
            status_code=500,
        )


@router.delete("/nivel1/{id_clagas1}")
async def eliminar_n1(
    id_clagas1: int,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "ClasificadorGastos", "btn_eliminar")
    ),
):
    cuenta = await db.execute(
        select(func.count(ClasificadorGas2.id_clagas2))
        .where(ClasificadorGas2.id_clagas1 == id_clagas1)
    )
    n_hijas = cuenta.scalar() or 0
    if n_hijas > 0:
        sufijo = "s" if n_hijas != 1 else ""
        return JSONResponse(
            {
                "ok": False,
                "error": f"Tiene {n_hijas} sub-categoria{sufijo}, eliminalas primero",
            },
            status_code=400,
        )

    reg = await db.get(ClasificadorGas1, id_clagas1)
    if reg is None:
        raise HTTPException(status_code=404, detail="Categoria no encontrada")
    try:
        await db.delete(reg)
        await db.commit()
        return JSONResponse({"ok": True, "mensaje": "Categoria eliminada"})
    except IntegrityError:
        await db.rollback()
        return JSONResponse(
            {
                "ok": False,
                "error": "No se puede eliminar: la categoria esta siendo usada en otro modulo (ej: Catalogo de Gastos).",
            },
            status_code=400,
        )
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"ok": False, "error": f"Error al eliminar: {str(e)}"},
            status_code=500,
        )


# ============================================================
# NIVEL 2 - CRUD
# ============================================================

@router.get("/nivel2/nuevo/{id_clagas1}", response_class=HTMLResponse)
async def modal_nuevo_n2(
    id_clagas1: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "ClasificadorGastos", "btn_nuevo")
    ),
):
    padre = await db.get(ClasificadorGas1, id_clagas1)
    if padre is None:
        raise HTTPException(status_code=404, detail="Categoria padre no encontrada")
    response = templates.TemplateResponse(
        "tablas/clasificador_gastos/_modal_form.html",
        await build_context(
            request, db, current_user,
            nivel=2, registro=None, modo="nuevo",
            id_padre=id_clagas1, nombre_padre=padre.nombre_clagas1,
        ),
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response


@router.get("/nivel2/{id_clagas2}/editar", response_class=HTMLResponse)
async def modal_editar_n2(
    id_clagas2: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "ClasificadorGastos", "btn_editar")
    ),
):
    reg = await db.get(ClasificadorGas2, id_clagas2)
    if reg is None:
        raise HTTPException(status_code=404, detail="Sub-categoria no encontrada")
    await db.refresh(reg)
    padre = await db.get(ClasificadorGas1, reg.id_clagas1)
    response = templates.TemplateResponse(
        "tablas/clasificador_gastos/_modal_form.html",
        await build_context(
            request, db, current_user,
            nivel=2, registro=reg, modo="editar",
            id_padre=reg.id_clagas1,
            nombre_padre=padre.nombre_clagas1 if padre else "",
        ),
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response


@router.post("/nivel2")
async def crear_n2(
    payload: ClasGas2Payload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "ClasificadorGastos", "btn_guardar")
    ),
):
    padre = await db.get(ClasificadorGas1, payload.id_clagas1)
    if padre is None:
        return JSONResponse(
            {"ok": False, "error": "Categoria padre no existe"},
            status_code=400,
        )
    estacion = get_estacion(request)
    try:
        reg = ClasificadorGas2(
            id_clagas1=payload.id_clagas1,
            nombre_clagas2=payload.nombre,
            id_usuario=current_user.id_usuario,
            fhcontrol=datetime.now(),
            estacion=estacion,
        )
        db.add(reg)
        await db.commit()
        await db.refresh(reg)
        return JSONResponse({
            "ok": True,
            "id_clagas2": reg.id_clagas2,
            "id_clagas1": reg.id_clagas1,
        }, status_code=201)
    except IntegrityError:
        await db.rollback()
        return JSONResponse(
            {"ok": False, "error": f"Ya existe una sub-categoria con el nombre '{payload.nombre}' en esta categoria"},
            status_code=400,
        )
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"ok": False, "error": f"Error al guardar: {str(e)}"},
            status_code=500,
        )


@router.put("/nivel2/{id_clagas2}")
async def actualizar_n2(
    id_clagas2: int,
    payload: ClasGas2Payload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "ClasificadorGastos", "btn_guardar")
    ),
):
    reg = await db.get(ClasificadorGas2, id_clagas2)
    if reg is None:
        raise HTTPException(status_code=404, detail="Sub-categoria no encontrada")
    estacion = get_estacion(request)
    try:
        reg.nombre_clagas2 = payload.nombre
        reg.id_clagas1 = payload.id_clagas1
        reg.id_usuario = current_user.id_usuario
        reg.fhcontrol = datetime.now()
        reg.estacion = estacion
        await db.commit()
        await db.refresh(reg)
        return JSONResponse({
            "ok": True,
            "id_clagas2": reg.id_clagas2,
            "id_clagas1": reg.id_clagas1,
        })
    except IntegrityError:
        await db.rollback()
        return JSONResponse(
            {"ok": False, "error": f"Ya existe una sub-categoria con el nombre '{payload.nombre}' en esta categoria"},
            status_code=400,
        )
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"ok": False, "error": f"Error al actualizar: {str(e)}"},
            status_code=500,
        )


@router.delete("/nivel2/{id_clagas2}")
async def eliminar_n2(
    id_clagas2: int,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "ClasificadorGastos", "btn_eliminar")
    ),
):
    reg = await db.get(ClasificadorGas2, id_clagas2)
    if reg is None:
        raise HTTPException(status_code=404, detail="Sub-categoria no encontrada")
    try:
        await db.delete(reg)
        await db.commit()
        return JSONResponse({"ok": True, "mensaje": "Sub-categoria eliminada"})
    except IntegrityError:
        await db.rollback()
        return JSONResponse(
            {
                "ok": False,
                "error": "No se puede eliminar: la sub-categoria esta siendo usada en otro modulo (ej: Catalogo de Gastos).",
            },
            status_code=400,
        )
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"ok": False, "error": f"Error al eliminar: {str(e)}"},
            status_code=500,
        )
