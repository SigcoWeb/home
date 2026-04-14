from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class SgcCatalogoGastos(Base):
    __tablename__ = "sgc_catalogo_gastos"

    id_gasto = Column(Integer, primary_key=True, index=True)
    estado = Column(Boolean, default=True)
    codigo_gasto = Column(String(20))
    nombre_gasto = Column(String(100))
    
    id_unidad = Column(Integer, ForeignKey("sgc_unidades.id_unidad"))
    id_clagas1 = Column(Integer, ForeignKey("sgc_clasificador_gas1.id_clagas1"))
    id_clagas2 = Column(Integer, ForeignKey("sgc_clasificador_gas2.id_clagas2"))
    
    precio_costo = Column(Numeric(18, 2))
    nota = Column(Text)
    
    # Audit fields
    id_usuario = Column(Integer, nullable=True)
    fhcontrol = Column(TIMESTAMP, default=datetime.now)
    estacion = Column(String(20), nullable=True)

    # Relationships
    unidad = relationship("UnidadMedida")
    clagas1 = relationship("ClasificadorGas1")
    clagas2 = relationship("ClasificadorGas2")
