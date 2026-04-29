"""Schemas Pydantic v2 para Catalogo de Gastos (zWalter-17)."""
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CatalogoGastosPayload(BaseModel):
    """Payload de crear/editar gasto.

    id_gasto = None => crear; id_gasto = N => actualizar.
    """
    id_gasto: Optional[int] = None
    codigo_gasto: str = Field(..., min_length=1, max_length=20)
    nombre_gasto: str = Field(..., min_length=1, max_length=100)
    id_unidad: int = Field(..., gt=0)
    id_clagas1: int = Field(..., gt=0)
    id_clagas2: int = Field(..., gt=0)
    precio_costo: Optional[Decimal] = Field(default=None, ge=0)
    nota: Optional[str] = None
    estado: bool = True

    @field_validator("codigo_gasto")
    @classmethod
    def normalizar_codigo(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("nombre_gasto")
    @classmethod
    def normalizar_nombre(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("nota")
    @classmethod
    def normalizar_nota(cls, v):
        if v is None:
            return None
        v = v.strip()
        return v if v else None

    @field_validator("precio_costo", mode="before")
    @classmethod
    def parse_decimal(cls, v):
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return Decimal(v.replace(",", "."))
        return Decimal(str(v))
