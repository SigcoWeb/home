"""
Modelo de Documentos SUNAT (zWalter-15).
Tabla legacy de Walter: sgc_docsunat.

Nota: el typo legacy `flag_persepcion` se corrige a `flag_percepcion` en la
migracion v012; el modelo Python ya usa el nombre correcto.
"""
from sqlalchemy import Column, Integer, String, DateTime, CHAR
from datetime import datetime
from app.database import Base


class SgcDocSunat(Base):
    __tablename__ = "sgc_docsunat"

    id_docsunat = Column(Integer, primary_key=True, index=True)
    codigo_docsunat = Column(CHAR(2), nullable=False)
    nombre_docsunat = Column(String(200), nullable=False)
    abreviado_docsunat = Column(String(10), nullable=True)

    # Flags Integer 1/0 (convencion de Walter, no Boolean)
    flag_compra = Column(Integer, default=0, nullable=False)
    flag_venta = Column(Integer, default=0, nullable=False)
    flag_gasto = Column(Integer, default=0, nullable=False)
    flag_guia = Column(Integer, default=0, nullable=False)
    flag_percepcion = Column(Integer, default=0, nullable=False)
    flag_retencion = Column(Integer, default=0, nullable=False)

    # Audit
    id_usuario = Column(Integer, nullable=True)
    fhcontrol = Column(DateTime, default=datetime.now)
    estacion = Column(String(20), nullable=True)
