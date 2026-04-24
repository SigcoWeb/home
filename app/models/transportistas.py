from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class SgcTransportista(Base):
    __tablename__ = "sgc_transportista"

    id_transportista = Column(Integer, primary_key=True, index=True)
    ruc = Column(String(11), unique=True, nullable=False, index=True)
    nombre = Column(String(200), nullable=False, index=True)
    direccion = Column(String(200), nullable=True)
    localidad = Column(String(100), nullable=True)
    celular = Column(String(20), nullable=True)
    correo = Column(String(100), nullable=True)
    estado = Column(Boolean, default=True)

    # Scaffolding para zW-07b (SUNAT API response)
    metadatos_api = Column(JSONB, nullable=True)

    # Auditoria
    id_usuario = Column(Integer, nullable=True)
    fhcontrol = Column(DateTime, default=datetime.now)
    estacion = Column(String(20), nullable=True)

    vehiculos = relationship(
        "SgcTransportistaVehiculo",
        back_populates="transportista",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class SgcTransportistaVehiculo(Base):
    __tablename__ = "sgc_transportista_vehiculo"

    id_vehiculo = Column(Integer, primary_key=True, index=True)
    id_transportista = Column(
        Integer,
        ForeignKey("sgc_transportista.id_transportista", ondelete="CASCADE"),
        nullable=False,
    )
    vehiculo = Column(String(100), nullable=False)
    placa = Column(String(20), nullable=False)
    dni_chofer = Column(String(8), nullable=True)
    nombre_chofer = Column(String(100), nullable=True)
    apellidos_chofer = Column(String(100), nullable=True)
    licencia = Column(String(20), nullable=True)
    nota = Column(Text, nullable=True)
    estado = Column(Boolean, default=True)

    # Auditoria
    id_usuario = Column(Integer, nullable=True)
    fhcontrol = Column(DateTime, default=datetime.now)
    estacion = Column(String(20), nullable=True)

    transportista = relationship("SgcTransportista", back_populates="vehiculos")
