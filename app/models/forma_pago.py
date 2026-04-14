from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class SgcFormaPago(Base):
    __tablename__ = "sgc_forma_pago"

    id_forpag = Column(Integer, primary_key=True, index=True)
    nombre_forpag = Column(String(50))
    tipo_forpag = Column(String(20))
    compra = Column(Boolean, default=False)
    venta = Column(Boolean, default=False)
    pv = Column(Boolean, default=False)
    agenda = Column(Boolean, default=False)
    dias = Column(Integer)
