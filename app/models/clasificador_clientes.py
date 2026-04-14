from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey
from app.database import Base

class SgcClasificadorCli(Base):
    __tablename__ = "sgc_clasificador_cli"

    id_clacli = Column(Integer, primary_key=True, index=True)
    nombre_clacli = Column(String(50))
    id_usuario = Column(Integer)
    # fhcontrol = Column(DateTime, default=func.now(), onupdate=func.now()) # Standard auto
    # Per user request in previous sessions, fhcontrol might be handled manually or just default.
    # The requirement said "fhcontrol timestamp". I will use default=func.now().
    fhcontrol = Column(DateTime, default=func.now())
    estacion = Column(String(20))
