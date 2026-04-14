from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Text, Numeric, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class SgcAgendaProveedores(Base):
    __tablename__ = "sgc_agenda_proveedores"

    id_agenda_pro = Column(Integer, primary_key=True, index=True)
    nombre_pro = Column(String(100))
    direccion_pro = Column(String(100))
    ubigeo_nombre = Column(String(100))
    ubigeo = Column(String(6))
    referencia = Column(Text)
    celular = Column(String(10))
    celular2 = Column(String(10))
    email = Column(String(100))
    
    id_doc_ide = Column(Integer, ForeignKey("sgc_doc_identidad.id_doc_ide"))
    num_doc_ide = Column(String(12))
    
    id_forpag = Column(Integer, ForeignKey("sgc_forma_pago.id_forpag"))
    
    deuda_actual = Column(Numeric(18, 2), default=0)
    saldo_disponible = Column(Numeric(18, 2), default=0)
    
    nota = Column(Text)
    estado = Column(Boolean, default=True)
    fecha_inicio = Column(Date)
    
    id_usuario = Column(Integer)
    fhcontrol = Column(DateTime, default=func.now())
    estacion = Column(String(20))

    # Relationships
    doc_identidad = relationship("SgcDocIdentidad")
    forma_pago = relationship("SgcFormaPago")
