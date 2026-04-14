from sqlalchemy import Column, Integer, String, DateTime, CHAR
from datetime import datetime
from app.database import Base

class DocSunat(Base):
    __tablename__ = "sgc_docsunat"

    id_docsunat = Column(Integer, primary_key=True, index=True)
    codigo_docsunat = Column(CHAR(2), nullable=True)
    nombre_docsunat = Column(String(200), nullable=True)
    abreviado_docsunat = Column(String(10), nullable=True)
    
    # Flags as Integer (1/0)
    flag_compra = Column(Integer, default=0)
    flag_venta = Column(Integer, default=0)
    flag_gasto = Column(Integer, default=0)
    flag_guia = Column(Integer, default=0)
    flag_persepcion = Column(Integer, default=0)
    flag_retencion = Column(Integer, default=0)
    
    # Audit
    id_usuario = Column(Integer, nullable=True)
    fhcontrol = Column(DateTime, default=datetime.now)
    estacion = Column(String(20), nullable=True)
