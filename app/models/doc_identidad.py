from sqlalchemy import Column, Integer, String
from app.database import Base

class SgcDocIdentidad(Base):
    __tablename__ = "sgc_doc_identidad"

    id_doc_ide = Column(Integer, primary_key=True, index=True)
    nombre_doc_ide = Column(String(50))
    abreviado_doc_ide = Column(String(10))
    digitos = Column(Integer, nullable=True)
