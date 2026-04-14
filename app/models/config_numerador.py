from sqlalchemy import Column, Integer, String, CHAR, Boolean, UniqueConstraint
from app.database import Base

class ConfigNumerador(Base):
    __tablename__ = "sgc_config_numerador"

    id_numerador = Column(Integer, primary_key=True, index=True)
    codigo_doc = Column(CHAR(2), default="")
    nombre_doc = Column(String(25), default="")
    serie = Column(CHAR(4), default="")
    numero = Column(Integer, default=0)
    caja = Column(String(7), default="")
    id_almacen = Column(Integer, default=0) # Should be FK to sgc_almacen if exists, but keeping as Integer for now based on prompt
    cpe = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint('codigo_doc', 'serie', name='_codigo_doc_serie_uc'),
    )
