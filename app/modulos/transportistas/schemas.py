from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from app.utils.validators import validar_ruc_peru, validar_dni_peru


class VehiculoPayload(BaseModel):
    """Vehiculo en el payload de Guardar Todo."""
    id_vehiculo: Optional[int] = None          # None = nuevo
    vehiculo: str = Field(..., min_length=1, max_length=100)
    placa: str = Field(..., min_length=1, max_length=20)
    dni_chofer: Optional[str] = Field(None, max_length=8)
    nombre_chofer: Optional[str] = Field(None, max_length=100)
    apellidos_chofer: Optional[str] = Field(None, max_length=100)
    licencia: Optional[str] = Field(None, max_length=20)
    nota: Optional[str] = None
    estado: bool = True
    eliminado: bool = Field(False, alias="_eliminado")

    model_config = {"populate_by_name": True}

    @field_validator("vehiculo", "placa", "nombre_chofer", "apellidos_chofer", "licencia")
    @classmethod
    def uppercase(cls, v):
        return v.strip().upper() if v else v

    @field_validator("dni_chofer")
    @classmethod
    def dni_valido(cls, v):
        if v is None or v == "":
            return None
        ok, err = validar_dni_peru(v)
        if not ok:
            raise ValueError(err)
        return v

    @model_validator(mode="after")
    def licencia_requerida_si_hay_chofer(self):
        tiene_chofer = bool(
            (self.dni_chofer and self.dni_chofer.strip())
            or (self.nombre_chofer and self.nombre_chofer.strip())
            or (self.apellidos_chofer and self.apellidos_chofer.strip())
        )
        if tiene_chofer and not (self.licencia and self.licencia.strip()):
            raise ValueError("Si hay chofer, la licencia es obligatoria")
        return self


class TransportistaPayload(BaseModel):
    """Payload completo de Guardar Todo."""
    id_transportista: Optional[int] = None     # None = nuevo
    ruc: str = Field(..., min_length=11, max_length=11)
    nombre: str = Field(..., min_length=1, max_length=200)
    direccion: Optional[str] = Field(None, max_length=200)
    localidad: Optional[str] = Field(None, max_length=100)
    celular: Optional[str] = Field(None, max_length=20)
    correo: Optional[str] = Field(None, max_length=100)
    estado: bool = True
    vehiculos: list[VehiculoPayload] = []

    @field_validator("nombre", "direccion", "localidad")
    @classmethod
    def uppercase(cls, v):
        return v.strip().upper() if v else v

    @field_validator("correo")
    @classmethod
    def email_lowercase(cls, v):
        return v.strip().lower() if v else v

    @field_validator("ruc")
    @classmethod
    def ruc_valido(cls, v):
        ok, err = validar_ruc_peru(v)
        if not ok:
            raise ValueError(err)
        return v
