from sqlalchemy import Column, Integer, String, CHAR, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base

class SgcMoneda(Base):
    __tablename__ = "sgc_moneda"

    id_moneda = Column(Integer, primary_key=True, index=True)
    codigo_moneda = Column(CHAR(3))
    simbolo_moneda = Column(String(6))
    nombre_moneda = Column(String(30))
    pais_moneda = Column(String(50))

class SgcEmpresa(Base):
    __tablename__ = "sgc_empresa"

    ruc_empresa = Column(String(12), primary_key=True, index=True)
    nombre_empresa = Column(String(100))
    direc_empresa = Column(String(100))
    localidad_empresa = Column(String(100))
    ubigeo = Column(CHAR(6), ForeignKey("sgc_ubigeo.ubigeo"))
    correo_empresa = Column(String(100))
    telefono_empresa = Column(String(50))
    codigo_estab = Column(CHAR(4))
    id_moneda = Column(Integer, ForeignKey("sgc_moneda.id_moneda"))
    id_rubro = Column(Integer, ForeignKey("sgc_rubros.id_rubro"))
    fecha_inicio = Column(Date)

    moneda = relationship("SgcMoneda")
    rubro = relationship("SgcRubro")

class SgcRubro(Base):
    __tablename__ = "sgc_rubros"

    id_rubro = Column(Integer, primary_key=True)
    nombre_rubro = Column(String(20))
