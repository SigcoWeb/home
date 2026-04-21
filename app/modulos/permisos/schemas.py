from pydantic import BaseModel
from typing import List


class PermisoOpcionUpdate(BaseModel):
    """Una fila de la matriz a actualizar."""
    id_opcion: int
    btn_nuevo: bool = False
    btn_editar: bool = False
    btn_eliminar: bool = False
    btn_pdf: bool = False
    btn_excel: bool = False
    btn_guardar: bool = False
    btn_otro: bool = False
    activo: bool = False


class PermisosMatrizUpdate(BaseModel):
    """Payload completo al guardar la matriz."""
    id_usuario: int
    opciones: List[PermisoOpcionUpdate]
