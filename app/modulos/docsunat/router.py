"""
Router del sub-modulo "Documentos SUNAT" del modulo UI Tablas (zWalter-15).

CRUD simple sobre sgc_docsunat. Constraint UNIQUE sobre codigo_docsunat.
Audit fields (id_usuario, fhcontrol, estacion) se llenan en backend.
"""
from datetime import datetime

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.core.templating import templates, build_context
from app.core.auditoria import get_estacion
from app.core.permisos import require_permission
from app.models.docsunat import SgcDocSunat
from app.models.usuarios import SgcUsuario
from .schemas import DocSunatPayload


router = APIRouter(prefix="/tablas/docsunat", tags=["tablas"])


# ======================================================
# LISTADO
# ======================================================

@router.get("", response_class=HTMLResponse)
async def listar(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("TABLAS", "DocSunat")),
):
    result = await db.execute(
        select(SgcDocSunat).order_by(SgcDocSunat.codigo_docsunat)
    )
    documentos = result.scalars().all()

    return templates.TemplateResponse(
        "tablas/docsunat/index.html",
        await build_context(request, db, current_user, documentos=documentos),
    )


# ======================================================
# FORMULARIO (nuevo o editar) -> devuelve modal
# ======================================================

@router.get("/nuevo", response_class=HTMLResponse)
async def form_nuevo(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "DocSunat", "btn_nuevo")
    ),
):
    response = templates.TemplateResponse(
        "tablas/docsunat/_modal_form.html",
        await build_context(request, db, current_user, doc=None),
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response


@router.get("/{id_docsunat}/editar", response_class=HTMLResponse)
async def form_editar(
    id_docsunat: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "DocSunat", "btn_editar")
    ),
):
    result = await db.execute(
        select(SgcDocSunat).where(SgcDocSunat.id_docsunat == id_docsunat)
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    await db.refresh(doc)

    response = templates.TemplateResponse(
        "tablas/docsunat/_modal_form.html",
        await build_context(request, db, current_user, doc=doc),
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response


# ======================================================
# GUARDAR (crear o actualizar)
# ======================================================

@router.post("")
async def guardar(
    payload: DocSunatPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "DocSunat", "btn_guardar")
    ),
):
    """Crea o actualiza un documento SUNAT. UNIQUE por codigo_docsunat."""
    estacion = get_estacion(request)
    try:
        if payload.id_docsunat is None:
            doc = SgcDocSunat(
                codigo_docsunat=payload.codigo_docsunat,
                nombre_docsunat=payload.nombre_docsunat,
                abreviado_docsunat=payload.abreviado_docsunat,
                flag_compra=payload.flag_compra,
                flag_venta=payload.flag_venta,
                flag_gasto=payload.flag_gasto,
                flag_guia=payload.flag_guia,
                flag_percepcion=payload.flag_percepcion,
                flag_retencion=payload.flag_retencion,
                id_usuario=current_user.id_usuario,
                fhcontrol=datetime.now(),
                estacion=estacion,
            )
            db.add(doc)
        else:
            result = await db.execute(
                select(SgcDocSunat).where(SgcDocSunat.id_docsunat == payload.id_docsunat)
            )
            doc = result.scalar_one_or_none()
            if doc is None:
                raise HTTPException(status_code=404, detail="Documento no encontrado")
            doc.codigo_docsunat = payload.codigo_docsunat
            doc.nombre_docsunat = payload.nombre_docsunat
            doc.abreviado_docsunat = payload.abreviado_docsunat
            doc.flag_compra = payload.flag_compra
            doc.flag_venta = payload.flag_venta
            doc.flag_gasto = payload.flag_gasto
            doc.flag_guia = payload.flag_guia
            doc.flag_percepcion = payload.flag_percepcion
            doc.flag_retencion = payload.flag_retencion
            doc.id_usuario = current_user.id_usuario
            doc.fhcontrol = datetime.now()
            doc.estacion = estacion

        await db.commit()
        await db.refresh(doc)

        return JSONResponse({
            "ok": True,
            "id_docsunat": doc.id_docsunat,
            "mensaje": "Guardado correctamente",
        })

    except IntegrityError:
        await db.rollback()
        return JSONResponse(
            {
                "ok": False,
                "error": f"Ya existe un documento con codigo '{payload.codigo_docsunat}'",
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

@router.delete("/{id_docsunat}")
async def eliminar(
    id_docsunat: int,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "DocSunat", "btn_eliminar")
    ),
):
    result = await db.execute(
        select(SgcDocSunat).where(SgcDocSunat.id_docsunat == id_docsunat)
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    try:
        await db.delete(doc)
        await db.commit()
        return JSONResponse({"ok": True, "mensaje": "Documento eliminado"})
    except IntegrityError:
        await db.rollback()
        return JSONResponse(
            {
                "ok": False,
                "error": "No se puede eliminar: tiene registros relacionados (guias, comprobantes u otros)",
            },
            status_code=400,
        )
    except Exception as e:
        await db.rollback()
        return JSONResponse(
            {"ok": False, "error": f"Error al eliminar: {str(e)}"},
            status_code=500,
        )
