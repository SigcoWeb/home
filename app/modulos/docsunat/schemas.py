"""Schemas Pydantic v2 para Documentos SUNAT (zWalter-15)."""
import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class DocSunatPayload(BaseModel):
    """Payload de crear/editar documento SUNAT.

    id_docsunat = None => crear; id_docsunat = N => actualizar.
    """
    id_docsunat: Optional[int] = None
    codigo_docsunat: str = Field(..., min_length=2, max_length=2)
    nombre_docsunat: str = Field(..., min_length=1, max_length=200)
    abreviado_docsunat: Optional[str] = Field(default=None, max_length=10)

    flag_compra: int = Field(default=0, ge=0, le=1)
    flag_venta: int = Field(default=0, ge=0, le=1)
    flag_gasto: int = Field(default=0, ge=0, le=1)
    flag_guia: int = Field(default=0, ge=0, le=1)
    flag_percepcion: int = Field(default=0, ge=0, le=1)
    flag_retencion: int = Field(default=0, ge=0, le=1)

    @field_validator("codigo_docsunat")
    @classmethod
    def validar_codigo(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r"^\d{2}$", v):
            raise ValueError("El codigo debe ser exactamente 2 digitos numericos")
        return v

    @field_validator("nombre_docsunat")
    @classmethod
    def normalizar_nombre(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("abreviado_docsunat")
    @classmethod
    def normalizar_abreviado(cls, v):
        if v is None:
            return None
        v = v.strip().upper()
        return v if v else None
