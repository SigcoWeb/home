"""
Helpers de auditoría. Reemplazan el fallback id_usuario=1 de zWalter-01.
Adaptado a AsyncSession.

`estacion` es paridad con el desktop de Walter (hostname en LAN);
en web usamos la IP del cliente.
"""
from fastapi import Request, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.usuarios import SgcUsuario


def get_estacion(request: Request) -> str:
    if request.client and request.client.host:
        return request.client.host[:20]
    return "WEB"


async def get_current_user_walter(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> SgcUsuario:
    """
    Dependency principal: resuelve el SgcUsuario del tenant a partir del
    sys_master id que dejó `auth_middleware` en request.state.user_id.

    - 401 si no hay sesión.
    - 403 si la sesión existe pero no hay mapping activo.
    """
    sys_user_id_raw = getattr(request.state, "user_id", None)
    if sys_user_id_raw is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
        )

    try:
        sys_user_id = int(sys_user_id_raw)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inválida",
        )

    result = await db.execute(
        select(SgcUsuario).where(
            SgcUsuario.id_sys_master == sys_user_id,
            SgcUsuario.activo.is_(True),
        )
    )
    user = result.scalars().first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta de plataforma no está vinculada a un usuario del tenant. Contacta al administrador.",
        )
    return user


async def get_id_usuario(
    current_user: SgcUsuario = Depends(get_current_user_walter),
) -> int:
    """Conveniencia: sólo el id para auditoría."""
    return current_user.id_usuario
