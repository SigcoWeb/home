"""
Sistema de permisos granulares de Walter.

Uso recomendado (dependency-factory):

    @router.post("")
    async def crear_almacen(
        ...,
        current_user: SgcUsuario = Depends(require_permission("TABLAS", "Almacenes", "btn_nuevo")),
        ...
    ):
        ...

`require_permission` valida y retorna el SgcUsuario autenticado, o lanza HTTP 403.
Si el endpoint también necesita current_user para auditoría, NO dupliques el Depends:
usa el current_user que ya devuelve require_permission.
"""
from typing import Optional, Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.usuarios import SgcUsuario, SgcUsuarioOpcion, SgcOpcion, SgcModulo
from app.core.auditoria import get_current_user_walter


ACCIONES_VALIDAS = {
    "btn_nuevo", "btn_editar", "btn_eliminar",
    "btn_pdf", "btn_excel", "btn_guardar", "btn_otro",
}


async def tiene_permiso(
    db: AsyncSession,
    usuario: SgcUsuario,
    modulo_nombre: str,
    opcion_nombre: str,
    accion: Optional[str] = None,
) -> bool:
    """
    Verifica si `usuario` tiene acceso a `modulo.opcion`, opcionalmente filtrado por `accion`.
    `accion` debe estar en ACCIONES_VALIDAS o ser None.
    """
    if accion is not None and accion not in ACCIONES_VALIDAS:
        raise ValueError(f"Acción inválida: {accion}")

    stmt = (
        select(SgcUsuarioOpcion)
        .join(SgcOpcion, SgcUsuarioOpcion.id_opcion == SgcOpcion.id_opcion)
        .join(SgcModulo, SgcUsuarioOpcion.id_modulo == SgcModulo.id_modulo)
        .where(
            SgcUsuarioOpcion.id_usuario == usuario.id_usuario,
            SgcUsuarioOpcion.activo.is_(True),
            SgcModulo.nombre == modulo_nombre,
            SgcOpcion.nombre == opcion_nombre,
        )
    )
    result = await db.execute(stmt)
    perm = result.scalars().first()

    if perm is None:
        return False
    if accion is None:
        return True
    return bool(getattr(perm, accion, False))


def require_permission(
    modulo: str,
    opcion: str,
    accion: Optional[str] = None,
) -> Callable:
    """
    Dependency-factory. Retorna una dependency que:
    1. Obtiene el SgcUsuario actual vía get_current_user_walter.
    2. Verifica el permiso; si falla, lanza HTTP 403.
    3. Si pasa, retorna el SgcUsuario.
    """
    if accion is not None and accion not in ACCIONES_VALIDAS:
        raise ValueError(f"Acción inválida: {accion}")

    async def _dep(
        current_user: SgcUsuario = Depends(get_current_user_walter),
        db: AsyncSession = Depends(get_db),
    ) -> SgcUsuario:
        ok = await tiene_permiso(db, current_user, modulo, opcion, accion)
        if not ok:
            detalle = f"{modulo}.{opcion}" + (f".{accion}" if accion else "")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Sin permiso: {detalle}",
            )
        return current_user

    return _dep


async def permisos_del_usuario(
    db: AsyncSession,
    usuario: SgcUsuario,
) -> dict:
    """
    Devuelve los permisos del usuario en forma de diccionario anidado:

        {
          "TABLAS": {
            "Almacenes": {"btn_nuevo": True, "btn_editar": True, ...},
            "Grupos":    {"btn_nuevo": True, ...},
          },
          "CONFIGURACIONES": {...},
        }

    Una sola query por request — usado desde el build_context del templating.
    """
    stmt = (
        select(
            SgcModulo.nombre.label("modulo"),
            SgcOpcion.nombre.label("opcion"),
            SgcUsuarioOpcion.btn_nuevo,
            SgcUsuarioOpcion.btn_editar,
            SgcUsuarioOpcion.btn_eliminar,
            SgcUsuarioOpcion.btn_pdf,
            SgcUsuarioOpcion.btn_excel,
            SgcUsuarioOpcion.btn_guardar,
            SgcUsuarioOpcion.btn_otro,
        )
        .join(SgcOpcion, SgcUsuarioOpcion.id_opcion == SgcOpcion.id_opcion)
        .join(SgcModulo, SgcUsuarioOpcion.id_modulo == SgcModulo.id_modulo)
        .where(
            SgcUsuarioOpcion.id_usuario == usuario.id_usuario,
            SgcUsuarioOpcion.activo.is_(True),
        )
    )
    result = await db.execute(stmt)
    rows = result.all()

    permisos: dict = {}
    for row in rows:
        permisos.setdefault(row.modulo, {})[row.opcion] = {
            "btn_nuevo":    bool(row.btn_nuevo),
            "btn_editar":   bool(row.btn_editar),
            "btn_eliminar": bool(row.btn_eliminar),
            "btn_pdf":      bool(row.btn_pdf),
            "btn_excel":    bool(row.btn_excel),
            "btn_guardar":  bool(row.btn_guardar),
            "btn_otro":     bool(row.btn_otro),
        }
    return permisos
