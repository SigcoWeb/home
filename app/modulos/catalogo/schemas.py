from pydantic import BaseModel, Field


class GrupoBase(BaseModel):
    nombre_grupo: str = Field(..., min_length=1, max_length=50)


class GrupoCreate(GrupoBase):
    pass


class GrupoUpdate(GrupoBase):
    pass


class GrupoOut(GrupoBase):
    id_grupo: int

    class Config:
        from_attributes = True
