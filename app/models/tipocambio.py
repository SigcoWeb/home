from sqlalchemy import Column, Integer, String, DateTime, Date, Numeric
from datetime import datetime
from app.database import Base

class TipoCambio(Base):
    __tablename__ = "sgc_tipocambio"

    id_tc = Column(Integer, primary_key=True, index=True)
    fecha_tc = Column(Date, nullable=False, unique=True)
    compra = Column(Numeric(18, 3), nullable=True)
    venta = Column(Numeric(18, 3), nullable=True)
    compra_sunat = Column(Numeric(18, 3), nullable=True)
    venta_sunat = Column(Numeric(18, 3), nullable=True)
    nota = Column(String(100), nullable=True)
    
    # Audit
    id_usuario = Column(Integer, nullable=True)
    fhcontrol = Column(DateTime, default=datetime.now)
    estacion = Column(String(20), nullable=True)
