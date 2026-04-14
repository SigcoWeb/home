from sqlalchemy import Column, Integer, String
from app.database import Base

class SgcConfigRutas(Base):
    __tablename__ = "sgc_config_rutas"

    id_ruta = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(20), unique=True, nullable=False)
    ruta = Column(String(200))
    descripcion = Column(String(100))
