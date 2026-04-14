from sqlalchemy import Column, String
from app.database import Base

class OperacionGre(Base):
    __tablename__ = "sgc_operaciones_gre"

    id_operacion = Column(String(2), primary_key=True, index=True, nullable=False)
    nombre_operacion = Column(String(100), default="", server_default="", nullable=False)
