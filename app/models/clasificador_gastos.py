"""
Modelos de Clasificador de Gastos Nivel 1 y Nivel 2 (zWalter-16).
Tablas legacy de Walter: sgc_clasificador_gas1, sgc_clasificador_gas2.

Nota sobre nombres de clase: se mantienen como `ClasificadorGas1` / `ClasificadorGas2`
(sin prefijo Sgc) porque otros modelos las referencian por nombre via
`relationship("ClasificadorGas1")` (ver catalogo_gastos.py, tesoreria.py).
"""
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ClasificadorGas1(Base):
    """Nivel 1: Categoria General de gastos."""
    __tablename__ = "sgc_clasificador_gas1"

    id_clagas1 = Column(Integer, primary_key=True, index=True)
    nombre_clagas1 = Column(String(100), nullable=False)

    # Codigos contables (NULL en datos de Walter, opcional para futuro)
    cta_compra = Column(String(20), nullable=True)
    cta_venta = Column(String(20), nullable=True)
    cta_nc_compra = Column(String(20), nullable=True)
    cta_nc_venta = Column(String(20), nullable=True)
    cta_nd_compra = Column(String(20), nullable=True)
    cta_nd_venta = Column(String(20), nullable=True)

    # Audit
    id_usuario = Column(Integer, nullable=True)
    fhcontrol = Column(TIMESTAMP, default=datetime.now)
    estacion = Column(String(20), nullable=True)

    # Relacion (NO cascade delete: bloqueamos delete si hay hijos en el router)
    nivel2 = relationship("ClasificadorGas2", back_populates="nivel1")


class ClasificadorGas2(Base):
    """Nivel 2: Sub-Categoria de gastos (depende de Nivel 1)."""
    __tablename__ = "sgc_clasificador_gas2"

    id_clagas2 = Column(Integer, primary_key=True, index=True)
    id_clagas1 = Column(
        Integer,
        ForeignKey("sgc_clasificador_gas1.id_clagas1"),
        nullable=False,
    )
    nombre_clagas2 = Column(String(100), nullable=False)

    # Codigos contables (NULL en datos de Walter)
    cta_compra = Column(String(20), nullable=True)
    cta_venta = Column(String(20), nullable=True)
    cta_nc_compra = Column(String(20), nullable=True)
    cta_nc_venta = Column(String(20), nullable=True)
    cta_nd_compra = Column(String(20), nullable=True)
    cta_nd_venta = Column(String(20), nullable=True)

    # Audit
    id_usuario = Column(Integer, nullable=True)
    fhcontrol = Column(TIMESTAMP, default=datetime.now)
    estacion = Column(String(20), nullable=True)

    nivel1 = relationship("ClasificadorGas1", back_populates="nivel2")
