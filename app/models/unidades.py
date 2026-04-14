from sqlalchemy import Column, Integer, String, DateTime, CHAR
from app.database import Base
from datetime import datetime

class UnidadMedida(Base):
    __tablename__ = "sgc_unidades"

    id_unidad = Column(Integer, primary_key=True, index=True)
    nombre_unidad = Column(String(25), index=True)
    abreviado_unidad = Column(String(10))
    codigo_sunat = Column(CHAR(3))
    id_usuario = Column(Integer, nullable=True)
    fhcontrol = Column(DateTime, default=datetime.now)
    estacion = Column(String(20))
