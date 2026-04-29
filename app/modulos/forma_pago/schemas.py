"""Schemas Pydantic v2 para Formas de Pago (zWalter-14)."""
from typing import Optional
from pydantic import BaseModel, Field, field_validator


TIPOS_VALIDOS = {
    "Contado", "Credito", "Tarjeta",
    "Transferencia", "Depósito", "Cheque", "Billetero",
}


class FormaPagoPayload(BaseModel):
    """Payload de crear/editar forma de pago.

    id_forpag = None => crear; id_forpag = N => actualizar.
    """
    id_forpag: Optional[int] = None
    nombre_forpag: str = Field(..., min_length=1, max_length=50)
    tipo_forpag: str = Field(..., min_length=1, max_length=20)
    compra: bool = False
    venta: bool = False
    pv: bool = False
    agenda: bool = False
    dias: int = Field(default=0, ge=0, le=365)

    @field_validator("nombre_forpag")
    @classmethod
    def normalizar_nombre(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("tipo_forpag")
    @classmethod
    def validar_tipo(cls, v: str) -> str:
        v = v.strip()
        if v not in TIPOS_VALIDOS:
            raise ValueError(
                f"Tipo invalido. Debe ser uno de: {', '.join(sorted(TIPOS_VALIDOS))}"
            )
        return v
