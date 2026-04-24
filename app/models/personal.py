from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Numeric, Text
from datetime import datetime
from app.database import Base


class SgcEmpleado(Base):
    __tablename__ = "sgc_empleados"

    id_personal = Column(Integer, primary_key=True, index=True)
    dni = Column(String(8), nullable=False, unique=True, index=True)
    nombre = Column(String(200), nullable=False, index=True)
    direccion = Column(String(200), nullable=True)
    celular = Column(String(20), nullable=True)
    fecha_ingreso = Column(Date, nullable=False)
    fecha_cese = Column(Date, nullable=True)   # NULL = vigente
    cargo = Column(String(100), nullable=True)
    comision_factura = Column(Numeric(10, 3), default=0)
    comision_producto = Column(Boolean, default=False)
    comision_familia = Column(Boolean, default=False)
    repartidor = Column(Boolean, default=False)
    mesero = Column(Boolean, default=False)
    observacion = Column(Text, nullable=True)
    estado = Column(Boolean, default=True, index=True)

    # Auditoria
    id_usuario = Column(Integer, nullable=True)
    fhcontrol = Column(DateTime, default=datetime.now)
    estacion = Column(String(20), nullable=True)
