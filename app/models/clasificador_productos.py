from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ClasificadorPro1(Base):
    __tablename__ = "sgc_clasificador_pro1"

    id_clapro1 = Column(Integer, primary_key=True, index=True)
    nombre_clapro1 = Column(String(50))
    cta_compra = Column(String(12))
    cta_venta = Column(String(12))
    cta_nc_compra = Column(String(12))
    cta_nc_venta = Column(String(12))
    cta_nd_compra = Column(String(12))
    cta_nd_venta = Column(String(12))
    imagen = Column(String(20)) # Added image column
    origen = Column(String(8), default='')

    id_usuario = Column(Integer)
    fhcontrol = Column(TIMESTAMP)
    estacion = Column(String(20))

    # Relationship to Level 2
    nivel2 = relationship("ClasificadorPro2", back_populates="nivel1")


class ClasificadorPro2(Base):
    __tablename__ = "sgc_clasificador_pro2"

    id_clapro1 = Column(Integer, ForeignKey("sgc_clasificador_pro1.id_clapro1"))
    id_clapro2 = Column(Integer, primary_key=True, index=True)
    nombre_clapro2 = Column(String(50))
    cta_compra = Column(String(12))
    cta_venta = Column(String(12))
    cta_nc_compra = Column(String(12))
    cta_nc_venta = Column(String(12))
    cta_nd_compra = Column(String(12))
    cta_nd_venta = Column(String(12))
    origen = Column(String(8), default='')

    id_usuario = Column(Integer)
    fhcontrol = Column(TIMESTAMP)
    estacion = Column(String(20))

    # Relationships
    nivel1 = relationship("ClasificadorPro1", back_populates="nivel2")
    nivel3 = relationship("ClasificadorPro3", back_populates="nivel2")


class ClasificadorPro3(Base):
    __tablename__ = "sgc_clasificador_pro3"

    id_clapro1 = Column(Integer) # Keeping as simple column if not strictly enforcing composite FK for now, assuming logic handling
    id_clapro2 = Column(Integer, ForeignKey("sgc_clasificador_pro2.id_clapro2"))
    id_clapro3 = Column(Integer, primary_key=True, index=True)
    nombre_clapro3 = Column(String(50))
    id_usuario = Column(Integer)
    fhcontrol = Column(TIMESTAMP)
    estacion = Column(String(20))

    # Relationships
    nivel2 = relationship("ClasificadorPro2", back_populates="nivel3")
