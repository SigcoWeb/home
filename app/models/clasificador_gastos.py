from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class ClasificadorGas1(Base):
    __tablename__ = "sgc_clasificador_gas1"

    id_clagas1 = Column(Integer, primary_key=True, index=True)
    nombre_clagas1 = Column(String(50))
    cta_compra = Column(String(12))
    cta_venta = Column(String(12))
    cta_nc_compra = Column(String(12))
    cta_nc_venta = Column(String(12))
    cta_nd_compra = Column(String(12))
    cta_nd_venta = Column(String(12))
    id_usuario = Column(Integer, nullable=True)
    fhcontrol = Column(TIMESTAMP, default=datetime.now)
    estacion = Column(String(20), nullable=True)

    # Relationship to Level 2
    nivel2 = relationship("ClasificadorGas2", back_populates="nivel1")

class ClasificadorGas2(Base):
    __tablename__ = "sgc_clasificador_gas2"

    id_clagas2 = Column(Integer, primary_key=True, index=True)
    nombre_clagas2 = Column(String(50))
    id_clagas1 = Column(Integer, ForeignKey("sgc_clasificador_gas1.id_clagas1"))
    cta_compra = Column(String(12))
    cta_venta = Column(String(12))
    cta_nc_compra = Column(String(12))
    cta_nc_venta = Column(String(12))
    cta_nd_compra = Column(String(12))
    cta_nd_venta = Column(String(12))
    id_usuario = Column(Integer, nullable=True)
    fhcontrol = Column(TIMESTAMP, default=datetime.now)
    estacion = Column(String(20), nullable=True)

    # Relationship to Level 1
    nivel1 = relationship("ClasificadorGas1", back_populates="nivel2")
