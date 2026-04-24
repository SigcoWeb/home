from typing import Optional
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class TipoCambioPayload(BaseModel):
    """Payload de crear/editar tipo de cambio."""
    id_tc: Optional[int] = None
    fecha_tc: date
    compra: Decimal = Field(..., ge=0)
    venta: Decimal = Field(..., ge=0)
    compra_sunat: Optional[Decimal] = Field(default=Decimal("0"), ge=0)
    venta_sunat: Optional[Decimal] = Field(default=Decimal("0"), ge=0)
    nota: Optional[str] = None

    @field_validator("nota")
    @classmethod
    def nota_uppercase(cls, v):
        return v.strip().upper() if v else None

    @field_validator("compra", "venta", "compra_sunat", "venta_sunat", mode="before")
    @classmethod
    def parse_decimal(cls, v):
        """Acepta string o numero. Convierte a Decimal. Vacio -> 0."""
        if v is None or v == "":
            return Decimal("0")
        if isinstance(v, str):
            return Decimal(v.replace(",", "."))
        return Decimal(str(v))
