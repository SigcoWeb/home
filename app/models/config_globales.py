from sqlalchemy import Column, Integer, Numeric
from app.database import Base

class SgcConfigGlobales(Base):
    __tablename__ = "sgc_config_globales"

    id = Column(Integer, primary_key=True, index=True)
    tope_venta = Column(Numeric(18, 2), default=700.00)
    igv = Column(Numeric(18, 2), default=18.00)
    icbper = Column(Numeric(18, 2), default=0.50)
    uit = Column(Numeric(18, 2), default=0.00)
    percepcion = Column(Numeric(18, 2), default=2.00)
    retencion = Column(Numeric(18, 2), default=3.00)
    renta_4ta = Column(Numeric(18, 2), default=8.00)
    renta_liqcom = Column(Numeric(18, 2), default=1.50)
