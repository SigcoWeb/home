"""
Router del sub-modulo "Formas de Pago" del modulo UI Tablas (zWalter-14).

CRUD simple sobre sgc_forma_pago, tabla plana legacy de Walter.
Constraint UNIQUE sobre nombre_forpag.
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.core.templating import templates, build_context
from app.core.permisos import require_permission
from app.models.forma_pago import SgcFormaPago
from app.models.usuarios import SgcUsuario
from .schemas import FormaPagoPayload


router = APIRouter(prefix="/tablas/forma_pago", tags=["tablas"])


# ======================================================
# LISTADO
# ======================================================

@router.get("", response_class=HTMLResponse)
async def listar(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("TABLAS", "FormasPago")),
):
    result = await db.execute(
        select(SgcFormaPago).order_by(SgcFormaPago.nombre_forpag)
    )
    formas = result.scalars().all()

    return templates.TemplateResponse(
        "tablas/forma_pago/index.html",
        await build_context(request, db, current_user, formas=formas),
    )


# ======================================================
# FORMULARIO (nuevo o editar) -> devuelve modal
# ======================================================

@router.get("/nuevo", response_class=HTMLResponse)
async def form_nuevo(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "FormasPago", "btn_nuevo")
    ),
):
    response = templates.TemplateResponse(
        "tablas/forma_pago/_modal_form.html",
        await build_context(request, db, current_user, forma=None),
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response


@router.get("/{id_forpag}/editar", response_class=HTMLResponse)
async def form_editar(
    id_forpag: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "FormasPago", "btn_editar")
    ),
):
    result = await db.execute(
        select(SgcFormaPago).where(SgcFormaPago.id_forpag == id_forpag)
    )
    forma = result.scalar_one_or_none()
    if forma is None:
        raise HTTPException(status_code=404, detail="Forma de pago no encontrada")

    await db.refresh(forma)

    response = templates.TemplateResponse(
        "tablas/forma_pago/_modal_form.html",
        await build_context(request, db, current_user, forma=forma),
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response


# ======================================================
# GUARDAR (crear o actualizar)
# ======================================================

@router.post("")
async def guardar(
    payload: FormaPagoPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "FormasPago", "btn_guardar")
    ),
):
    """Crea o actualiza una forma de pago. Valida UNIQUE por nombre a nivel DB."""
    try:
        if payload.id_forpag is None:
            forma = SgcFormaPago(
                nombre_forpag=payload.nombre_forpag,
                tipo_forpag=payload.tipo_forpag,
                compra=payload.compra,
                venta=payload.venta,
                pv=payload.pv,
                agenda=payload.agenda,
                dias=payload.dias,
            )
            db.add(forma)
        else:
            result = await db.execute(
                select(SgcFormaPago).where(SgcFormaPago.id_forpag == payload.id_forpag)
            )
            forma = result.scalar_one_or_none()
            if forma is None:
                raise HTTPException(status_code=404, detail="Forma de pago no encontrada")
            forma.nombre_forpag = payload.nombre_forpag
            forma.tipo_forpag = payload.tipo_forpag
            forma.compra = payload.compra
            forma.venta = payload.venta
            forma.pv = payload.pv
            forma.agenda = payload.agenda
            forma.dias = payload.dias

        await db.commit()
        await db.refresh(forma)

        return JSONResponse({
            "ok": True,
            "id_forpag": forma.id_forpag,
            "mensaje": "Guardado correctamente",
        })

    except IntegrityError:
        await db.rollback()
        return JSONResponse(
            {
                "ok": False,
                "error": f"Ya existe una forma de pago con el nombre '{payload.nombre_forpag}'",
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

@router.delete("/{id_forpag}")
async def eliminar(
    id_forpag: int,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "FormasPago", "btn_eliminar")
    ),
):
    result = await db.execute(
        select(SgcFormaPago).where(SgcFormaPago.id_forpag == id_forpag)
    )
    forma = result.scalar_one_or_none()
    if forma is None:
        raise HTTPException(status_code=404, detail="Forma de pago no encontrada")
    try:
        await db.delete(forma)
        await db.commit()
        return JSONResponse({"ok": True, "mensaje": "Forma de pago eliminada"})
    except IntegrityError:
        await db.rollback()
        return JSONResponse(
            {
                "ok": False,
                "error": "No se puede eliminar: tiene registros relacionados (clientes, proveedores u otros)",
            },
            status_code=400,
        )
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"ok": False, "error": f"Error al eliminar: {str(e)}"},
            status_code=500,
        )
