"""
Modelo de Catalogo de Gastos (zWalter-17).
Tabla legacy de Walter: sgc_catalogo_gastos.
"""
from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class SgcCatalogoGastos(Base):
    __tablename__ = "sgc_catalogo_gastos"

    id_gasto = Column(Integer, primary_key=True, index=True)
    estado = Column(Boolean, default=True, nullable=False)
    codigo_gasto = Column(String(20), nullable=False)
    nombre_gasto = Column(String(100), nullable=False)

    id_unidad = Column(
        Integer,
        ForeignKey("sgc_unidades.id_unidad"),
        nullable=False,
    )
    id_clagas1 = Column(
        Integer,
        ForeignKey("sgc_clasificador_gas1.id_clagas1"),
        nullable=False,
    )
    id_clagas2 = Column(
        Integer,
        ForeignKey("sgc_clasificador_gas2.id_clagas2"),
        nullable=False,
    )

    precio_costo = Column(Numeric(18, 2), nullable=True)
    nota = Column(Text, nullable=True)

    # Audit
    id_usuario = Column(Integer, nullable=True)
    fhcontrol = Column(TIMESTAMP, default=datetime.now)
    estacion = Column(String(20), nullable=True)

    # Relationships (lazy joins; cargar con selectinload en el listado)
    unidad = relationship("UnidadMedida")
    clagas1 = relationship("ClasificadorGas1")
    clagas2 = relationship("ClasificadorGas2")
