from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class SgcTransportista(Base):
    __tablename__ = "sgc_transportista"

    id_transportista = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ruc = Column(String(12), unique=True, index=True)
    nombre = Column(String(100))
    direccion = Column(String(100))
    localidad = Column(String(50))
    celular = Column(String(25))
    correo = Column(String(100))
    id_usuario = Column(Integer)
    fhcontrol = Column(DateTime, default=func.now())
    estado = Column(Boolean, default=True)

    # Relationship
    vehiculos = relationship("SgcTransportistaVehiculo", back_populates="transportista", cascade="all, delete-orphan")

class SgcTransportistaVehiculo(Base):
    __tablename__ = "sgc_transportista_vehiculo"

    id_vehiculo = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_transportista = Column(Integer, ForeignKey("sgc_transportista.id_transportista"))
    vehiculo = Column(String(50))
    placa = Column(String(12))
    dni_chofer = Column(String(9))
    nombre_chofer = Column(String(50))
    apellidos_chofer = Column(String(80))
    licencia = Column(String(12))
    nota = Column(Text)
    estado = Column(Boolean, default=True)

    # Relationship
    transportista = relationship("SgcTransportista", back_populates="vehiculos")
