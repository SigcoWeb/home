"""
Configuración central de Jinja2Templates con soporte de permisos.

Todos los routers importan `templates` desde aquí (en vez de crear un
`Jinja2Templates` local). El filtro `puede` y el helper `build_context`
permiten condicionar botones en los templates según los permisos del
usuario actual.
"""
from typing import Optional

from fastapi import Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permisos import permisos_del_usuario
from app.models.usuarios import SgcUsuario


templates = Jinja2Templates(directory="templates")


def puede(
    permisos: dict,
    modulo: str,
    opcion: str,
    accion: Optional[str] = None,
) -> bool:
    """
    Chequeo booleano. Usable en templates como filtro Jinja:
        {% if permisos | puede("TABLAS", "Almacenes", "btn_nuevo") %}...
    """
    mod = permisos.get(modulo, {})
    op = mod.get(opcion)
    if op is None:
        return False
    if accion is None:
        return True
    return bool(op.get(accion, False))


templates.env.filters["puede"] = puede


async def build_context(
    request: Request,
    db: AsyncSession,
    current_user: SgcUsuario,
    **extras,
) -> dict:
    """
    Empaqueta el contexto estándar para renders con permisos.

    Uso:
        return templates.TemplateResponse(
            "tablas/almacen/index.html",
            await build_context(request, db, current_user, almacenes=almacenes),
        )
    """
    permisos = await permisos_del_usuario(db, current_user)
    return {
        "request": request,
        "current_user": current_user,
        "permisos": permisos,
        **extras,
    }
