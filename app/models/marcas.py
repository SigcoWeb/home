from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class Marca(Base):
    __tablename__ = "sgc_marcas"

    id_marca = Column(Integer, primary_key=True, index=True)
    nombre_marca = Column(String(20), index=True)
    nota_marca = Column(String(20))
    id_usuario = Column(Integer, nullable=True)
    fhcontrol = Column(DateTime, default=datetime.now)
    estacion = Column(String(20))
