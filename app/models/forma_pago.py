"""
Modelo de Formas de Pago (zWalter-14).
Tabla legacy de Walter: sgc_forma_pago.
"""
from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base


class SgcFormaPago(Base):
    __tablename__ = "sgc_forma_pago"

    id_forpag = Column(Integer, primary_key=True, index=True)
    nombre_forpag = Column(String(50), nullable=False)
    tipo_forpag = Column(String(20), nullable=False)
    compra = Column(Boolean, default=False, nullable=False)
    venta = Column(Boolean, default=False, nullable=False)
    pv = Column(Boolean, default=False, nullable=False)
    agenda = Column(Boolean, default=False, nullable=False)
    dias = Column(Integer, default=0, nullable=False)
