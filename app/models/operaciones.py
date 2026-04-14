from sqlalchemy import Column, String, Boolean
from app.database import Base

class Operacion(Base):
    __tablename__ = "sgc_operaciones"

    id_operacion = Column(String(2), index=True, nullable=False, primary_key=True) # SQLAlchemy requires a primary key, so we must define one or use a composite. Assuming this remains the logical identifier but physical PK is removed. Wait, if physical PK is removed, SQLAlchemy MUST still have a primary key mapped. I will leave it mapped in SQLAlchemy but remove it physically. Actually, if I just remove `primary_key=True`, SQLAlchemy will crash unless another PK is defined. Let me just keep it in SQLAlchemy but drop the constraint in DB.
    nombre_operacion = Column(String(100), default="", nullable=False)
    ope_ingreso = Column(Boolean, default=False, nullable=False)
    ope_salida = Column(Boolean, default=False, nullable=False)


