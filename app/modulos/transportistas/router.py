"""
Router del sub-modulo "Transportistas" del modulo UI Tablas (zWalter-07).

CRUD con guardado atomico de transportista + vehiculos (relacion 1-a-N).
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.core.templating import templates, build_context
from app.core.auditoria import get_estacion
from app.core.permisos import require_permission
from app.models.transportistas import SgcTransportista, SgcTransportistaVehiculo
from app.models.usuarios import SgcUsuario
from .schemas import TransportistaPayload


router = APIRouter(prefix="/tablas/transportistas", tags=["tablas"])


# ======================================================
# LISTADO
# ======================================================

@router.get("", response_class=HTMLResponse)
async def listar(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("TABLAS", "Transportistas")),
):
    result = await db.execute(
        select(SgcTransportista).order_by(SgcTransportista.nombre)
    )
    transportistas = result.scalars().all()
    return templates.TemplateResponse(
        "tablas/transportistas/index.html",
        await build_context(request, db, current_user, transportistas=transportistas),
    )


# ======================================================
# FORMULARIO (nuevo o editar) -> devuelve modal
# ======================================================

@router.get("/nuevo", response_class=HTMLResponse)
async def form_nuevo(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "Transportistas", "btn_nuevo")
    ),
):
    return templates.TemplateResponse(
        "tablas/transportistas/_modal_form.html",
        await build_context(
            request, db, current_user,
            transportista=None,
            vehiculos=[],
        ),
    )


@router.get("/{id_transportista}/editar", response_class=HTMLResponse)
async def form_editar(
    id_transportista: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "Transportistas", "btn_editar")
    ),
):
    result = await db.execute(
        select(SgcTransportista)
        .options(selectinload(SgcTransportista.vehiculos))
        .where(SgcTransportista.id_transportista == id_transportista)
    )
    transportista = result.scalar_one_or_none()
    if transportista is None:
        raise HTTPException(status_code=404, detail="Transportista no encontrado")

    # Forzar lectura fresca desde DB (evita cache de sesion SQLAlchemy)
    await db.refresh(transportista, attribute_names=["vehiculos"])

    response = templates.TemplateResponse(
        "tablas/transportistas/_modal_form.html",
        await build_context(
            request, db, current_user,
            transportista=transportista,
            vehiculos=transportista.vehiculos,
        ),
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response

# ======================================================
# GUARDAR TODO -> endpoint atomico
# ======================================================

@router.post("")
async def guardar_todo(
    payload: TransportistaPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "Transportistas", "btn_guardar")
    ),
):
    """
    Upsert atomico de transportista + sus vehiculos.
    Si id_transportista es None, crea nuevo. Si tiene valor, actualiza.
    Vehiculos: diff contra DB segun id_vehiculo y flag _eliminado.
    Toda la operacion en una sola transaccion.
    """
    estacion = get_estacion(request)
    try:
        # --- transportista ---
        if payload.id_transportista is None:
            tp = SgcTransportista(
                ruc=payload.ruc,
                nombre=payload.nombre,
                direccion=payload.direccion,
                localidad=payload.localidad,
                celular=payload.celular,
                correo=payload.correo,
                estado=payload.estado,
                id_usuario=current_user.id_usuario,
                estacion=estacion,
            )
            db.add(tp)
            await db.flush()
            existentes = {}
        else:
            result = await db.execute(
                select(SgcTransportista)
                .options(selectinload(SgcTransportista.vehiculos))
                .where(SgcTransportista.id_transportista == payload.id_transportista)
            )
            tp = result.scalar_one_or_none()
            if tp is None:
                raise HTTPException(status_code=404, detail="Transportista no encontrado")
            tp.ruc = payload.ruc
            tp.nombre = payload.nombre
            tp.direccion = payload.direccion
            tp.localidad = payload.localidad
            tp.celular = payload.celular
            tp.correo = payload.correo
            tp.estado = payload.estado
            tp.id_usuario = current_user.id_usuario
            tp.estacion = estacion
            existentes = {v.id_vehiculo: v for v in tp.vehiculos}

        # --- vehiculos: diff ---
        ids_payload = {
            v.id_vehiculo for v in payload.vehiculos
            if v.id_vehiculo is not None and not v.eliminado
        }

        # Eliminar: en DB pero no en payload (o con _eliminado=True)
        for id_v, v_db in list(existentes.items()):
            marcado_eliminado = any(
                vp.id_vehiculo == id_v and vp.eliminado
                for vp in payload.vehiculos
            )
            if id_v not in ids_payload or marcado_eliminado:
                await db.delete(v_db)

        # Insertar / actualizar
        for vp in payload.vehiculos:
            if vp.eliminado:
                continue
            if vp.id_vehiculo is None:
                nuevo = SgcTransportistaVehiculo(
                    id_transportista=tp.id_transportista,
                    vehiculo=vp.vehiculo,
                    placa=vp.placa,
                    dni_chofer=vp.dni_chofer,
                    nombre_chofer=vp.nombre_chofer,
                    apellidos_chofer=vp.apellidos_chofer,
                    licencia=vp.licencia,
                    nota=vp.nota,
                    estado=vp.estado,
                    id_usuario=current_user.id_usuario,
                    estacion=estacion,
                )
                db.add(nuevo)
            else:
                v_db = existentes.get(vp.id_vehiculo)
                if v_db is None:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Vehiculo {vp.id_vehiculo} no pertenece a este transportista",
                    )
                v_db.vehiculo = vp.vehiculo
                v_db.placa = vp.placa
                v_db.dni_chofer = vp.dni_chofer
                v_db.nombre_chofer = vp.nombre_chofer
                v_db.apellidos_chofer = vp.apellidos_chofer
                v_db.licencia = vp.licencia
                v_db.nota = vp.nota
                v_db.estado = vp.estado
                v_db.id_usuario = current_user.id_usuario
                v_db.estacion = estacion

        await db.commit()
        await db.refresh(tp)

        return JSONResponse({
            "ok": True,
            "id_transportista": tp.id_transportista,
            "mensaje": "Guardado correctamente",
        })

    except IntegrityError as e:
        await db.rollback()
        # UNIQUE violation por RUC duplicado (o cualquier otra UNIQUE)
        mensaje = str(e.orig) if hasattr(e, "orig") else str(e)
        if "sgc_transportista_ruc" in mensaje or "ruc" in mensaje.lower():
            return JSONResponse(
                {"ok": False, "error": f"Ya existe un transportista con el RUC {payload.ruc}"},
                status_code=400,
            )
        return JSONResponse(
            {"ok": False, "error": "Error de integridad al guardar. Verifica los datos."},
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
# ELIMINAR TRANSPORTISTA (cascada a vehiculos)
# ======================================================

@router.delete("/{id_transportista}")
async def eliminar(
    id_transportista: int,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "Transportistas", "btn_eliminar")
    ),
):
    result = await db.execute(
        select(SgcTransportista).where(SgcTransportista.id_transportista == id_transportista)
    )
    tp = result.scalar_one_or_none()
    if tp is None:
        raise HTTPException(status_code=404, detail="Transportista no encontrado")
    await db.delete(tp)
    await db.commit()
    return JSONResponse({"ok": True, "mensaje": "Transportista eliminado"})
