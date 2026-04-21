from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UsuarioBase(BaseModel):
    usuario: str = Field(..., min_length=3, max_length=15)
    nombre_completo: Optional[str] = Field(None, max_length=100)
    activo: bool = True


class UsuarioCreate(UsuarioBase):
    clave: str = Field(..., min_length=4, max_length=100)
    id_sys_master: Optional[int] = None


class UsuarioUpdate(UsuarioBase):
    clave: Optional[str] = Field(None, min_length=4, max_length=100)
    id_sys_master: Optional[int] = None


class UsuarioOut(UsuarioBase):
    id_usuario: int
    id_sys_master: Optional[int] = None
    fecha_registro: datetime

    class Config:
        from_attributes = True
