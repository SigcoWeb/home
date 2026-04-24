from typing import Optional
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from app.utils.validators import validar_dni_peru


class PersonalPayload(BaseModel):
    """Payload de crear/editar empleado."""
    id_personal: Optional[int] = None
    dni: str = Field(..., min_length=8, max_length=8)
    nombre: str = Field(..., min_length=1, max_length=200)
    direccion: Optional[str] = Field(None, max_length=200)
    celular: Optional[str] = Field(None, max_length=20)
    fecha_ingreso: date
    fecha_cese: Optional[date] = None   # NULL = vigente
    cargo: Optional[str] = Field(None, max_length=100)
    comision_factura: Optional[Decimal] = Field(default=Decimal("0"), ge=0)
    comision_producto: bool = False
    comision_familia: bool = False
    repartidor: bool = False
    mesero: bool = False
    observacion: Optional[str] = None
    estado: bool = True

    @field_validator("dni")
    @classmethod
    def dni_valido(cls, v):
        ok, err = validar_dni_peru(v)
        if not ok:
            raise ValueError(err)
        return v

    @field_validator("nombre", "direccion", "cargo", "observacion")
    @classmethod
    def uppercase(cls, v):
        return v.strip().upper() if v else v

    @field_validator("celular")
    @classmethod
    def limpiar_celular(cls, v):
        return v.strip() if v else v

    @field_validator("comision_factura", mode="before")
    @classmethod
    def parse_decimal(cls, v):
        if v is None or v == "":
            return Decimal("0")
        if isinstance(v, str):
            return Decimal(v.replace(",", "."))
        return Decimal(str(v))
