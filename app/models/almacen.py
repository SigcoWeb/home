from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class SgcAlmacen(Base):
    __tablename__ = "sgc_almacen"
    
    id_almacen = Column(Integer, primary_key=True, index=True)
    nombre_almacen = Column(String(50))
    direccion = Column(String(100))
    localidad = Column(String(100))
    id_grupo = Column(Integer, ForeignKey("sgc_catalogo_grupo.id_grupo"))
