"""
Router del sub-modulo "Personal" del modulo UI Tablas (zWalter-09).

CRUD simple sobre sgc_empleados, tabla plana (sin relaciones 1-a-N).
Constraint UNIQUE sobre dni. fecha_cese NULL => vigente.
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.core.templating import templates, build_context
from app.core.auditoria import get_estacion
from app.core.permisos import require_permission
from app.models.personal import SgcEmpleado
from app.models.usuarios import SgcUsuario
from .schemas import PersonalPayload


router = APIRouter(prefix="/tablas/personal", tags=["tablas"])


# ======================================================
# LISTADO
# ======================================================

@router.get("", response_class=HTMLResponse)
async def listar(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(require_permission("TABLAS", "Personal")),
):
    result = await db.execute(
        select(SgcEmpleado).order_by(SgcEmpleado.nombre)
    )
    empleados = result.scalars().all()

    return templates.TemplateResponse(
        "tablas/personal/index.html",
        await build_context(request, db, current_user, empleados=empleados),
    )


# ======================================================
# FORMULARIO (nuevo o editar) -> devuelve modal
# ======================================================

@router.get("/nuevo", response_class=HTMLResponse)
async def form_nuevo(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "Personal", "btn_nuevo")
    ),
):
    response = templates.TemplateResponse(
        "tablas/personal/_modal_form.html",
        await build_context(request, db, current_user, empleado=None),
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response


@router.get("/{id_personal}/editar", response_class=HTMLResponse)
async def form_editar(
    id_personal: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "Personal", "btn_editar")
    ),
):
    result = await db.execute(
        select(SgcEmpleado).where(SgcEmpleado.id_personal == id_personal)
    )
    empleado = result.scalar_one_or_none()
    if empleado is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    # Forzar lectura fresca desde DB (patron aprendido en zW-07)
    await db.refresh(empleado)

    response = templates.TemplateResponse(
        "tablas/personal/_modal_form.html",
        await build_context(request, db, current_user, empleado=empleado),
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    return response


# ======================================================
# GUARDAR (crear o actualizar)
# ======================================================

@router.post("")
async def guardar(
    payload: PersonalPayload,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "Personal", "btn_guardar")
    ),
):
    """Crea o actualiza un empleado. Valida UNIQUE por DNI a nivel DB."""
    estacion = get_estacion(request)
    try:
        if payload.id_personal is None:
            # Crear
            emp = SgcEmpleado(
                dni=payload.dni,
                nombre=payload.nombre,
                direccion=payload.direccion,
                celular=payload.celular,
                fecha_ingreso=payload.fecha_ingreso,
                fecha_cese=payload.fecha_cese,
                cargo=payload.cargo,
                comision_factura=payload.comision_factura or 0,
                comision_producto=payload.comision_producto,
                comision_familia=payload.comision_familia,
                repartidor=payload.repartidor,
                mesero=payload.mesero,
                observacion=payload.observacion,
                estado=payload.estado,
                id_usuario=current_user.id_usuario,
                estacion=estacion,
            )
            db.add(emp)
        else:
            # Actualizar
            result = await db.execute(
                select(SgcEmpleado).where(SgcEmpleado.id_personal == payload.id_personal)
            )
            emp = result.scalar_one_or_none()
            if emp is None:
                raise HTTPException(status_code=404, detail="Empleado no encontrado")
            emp.dni = payload.dni
            emp.nombre = payload.nombre
            emp.direccion = payload.direccion
            emp.celular = payload.celular
            emp.fecha_ingreso = payload.fecha_ingreso
            emp.fecha_cese = payload.fecha_cese
            emp.cargo = payload.cargo
            emp.comision_factura = payload.comision_factura or 0
            emp.comision_producto = payload.comision_producto
            emp.comision_familia = payload.comision_familia
            emp.repartidor = payload.repartidor
            emp.mesero = payload.mesero
            emp.observacion = payload.observacion
            emp.estado = payload.estado
            emp.id_usuario = current_user.id_usuario
            emp.estacion = estacion

        await db.commit()
        await db.refresh(emp)

        return JSONResponse({
            "ok": True,
            "id_personal": emp.id_personal,
            "mensaje": "Guardado correctamente",
        })

    except IntegrityError:
        await db.rollback()
        return JSONResponse(
            {"ok": False, "error": f"Ya existe un empleado con el DNI {payload.dni}"},
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

@router.delete("/{id_personal}")
async def eliminar(
    id_personal: int,
    db: AsyncSession = Depends(get_db),
    current_user: SgcUsuario = Depends(
        require_permission("TABLAS", "Personal", "btn_eliminar")
    ),
):
    result = await db.execute(
        select(SgcEmpleado).where(SgcEmpleado.id_personal == id_personal)
    )
    emp = result.scalar_one_or_none()
    if emp is None:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    await db.delete(emp)
    await db.commit()
    return JSONResponse({"ok": True, "mensaje": "Empleado eliminado"})
