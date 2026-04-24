from sqlalchemy import Column, Integer, Date, Numeric, Text, String, DateTime
from datetime import datetime
from app.database import Base


class SgcTipoCambio(Base):
    __tablename__ = "sgc_tipocambio"

    id_tc = Column(Integer, primary_key=True, index=True)
    fecha_tc = Column(Date, nullable=False, unique=True, index=True)
    compra = Column(Numeric(10, 3), nullable=False)
    venta = Column(Numeric(10, 3), nullable=False)
    compra_sunat = Column(Numeric(10, 3), default=0)
    venta_sunat = Column(Numeric(10, 3), default=0)
    nota = Column(Text, nullable=True)

    # Auditoria
    id_usuario = Column(Integer, nullable=True)
    fhcontrol = Column(DateTime, default=datetime.now)
    estacion = Column(String(20), nullable=True)
