from sqlalchemy import Column, String
from app.database import Base

class SgcUbigeo(Base):
    __tablename__ = "sgc_ubigeo"

    ubigeo = Column(String(6), primary_key=True, index=True)
    departamento = Column(String(50), nullable=True)
    provincia = Column(String(50), nullable=True)
    distrito = Column(String(50), nullable=True)
