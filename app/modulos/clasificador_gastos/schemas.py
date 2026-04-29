"""Schemas Pydantic v2 para Clasificador de Gastos (zWalter-16)."""
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ClasificadorBase(BaseModel):
    """Base comun para Nivel 1 y Nivel 2 (solo nombre)."""
    nombre: str = Field(..., min_length=1, max_length=100)

    @field_validator("nombre")
    @classmethod
    def normalizar(cls, v: str) -> str:
        return v.strip()


class ClasGas1Payload(ClasificadorBase):
    """Payload para crear/actualizar Nivel 1."""
    pass


class ClasGas2Payload(ClasificadorBase):
    """Payload para crear/actualizar Nivel 2."""
    id_clagas1: int = Field(..., gt=0)
