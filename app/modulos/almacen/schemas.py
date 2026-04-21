from pydantic import BaseModel, Field
from typing import Optional


class AlmacenBase(BaseModel):
    nombre_almacen: str = Field(..., min_length=1, max_length=50)
    direccion: Optional[str] = Field(None, max_length=100)
    localidad: Optional[str] = Field(None, max_length=100)
    id_grupo: Optional[int] = None


class AlmacenCreate(AlmacenBase):
    pass


class AlmacenUpdate(AlmacenBase):
    pass


class AlmacenOut(AlmacenBase):
    id_almacen: int
    nombre_grupo: Optional[str] = None

    class Config:
        from_attributes = True
