from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class SgcAlmacen(Base):
    __tablename__ = "sgc_almacen"

    id_almacen = Column(Integer, primary_key=True, index=True)
    nombre_almacen = Column(String(50), nullable=False)
    direccion = Column(String(100), nullable=True)
    localidad = Column(String(100), nullable=True)
    id_grupo = Column(Integer, ForeignKey("sgc_catalogo_grupo.id_grupo"), nullable=True)

    id_usuario = Column(Integer, nullable=True)
    fhcontrol = Column(DateTime, default=datetime.now)
    estacion = Column(String(20), nullable=True)

    grupo = relationship("SgcCatalogoGrupo", lazy="joined")
