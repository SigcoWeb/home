from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Numeric, Text, CHAR, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class GuiaIngreso(Base):
    __tablename__ = "sgc_guia_ingreso"

    id_guia_ingreso = Column(Integer, primary_key=True, index=True)
    ruc = Column(String(12), nullable=True)
    id_agenda_pro = Column(Integer, default=0)
    id_docsunat = Column(Integer, default=0)
    serie = Column(CHAR(4), default="")
    numero = Column(String(8), default="")
    fecha_emision = Column(Date, default=datetime.utcnow)
    fecha_ingreso = Column(Date, default=datetime.utcnow)
    id_almacen = Column(Integer, default=0)
    id_operacion = Column(CHAR(2), default="")
    id_inventario = Column(Integer, default=0)
    glosa = Column(String(100), default="")
    id_almacen_sal = Column(Integer, default=0)
    serie_gr_salida = Column(CHAR(4), default="")
    numero_gr_salida = Column(String(8), default="")
    id_guia_salida = Column(Integer, default=0)
    serie_compra = Column(CHAR(4), default="")
    numero_compra = Column(String(8), default="")
    id_compra = Column(Integer, default=0)
    tc = Column(Numeric(18, 3), default=0)
    id_moneda = Column(Integer, default=0)
    mueve_costo_ = Column(Boolean, default=False)
    mueve_stock_ = Column(Boolean, default=False)
    igv_ = Column(Boolean, default=False)
    total_bruto = Column(Numeric(18, 2), default=0)
    descuento = Column(Numeric(18, 2), default=0)
    sub_total = Column(Numeric(18, 2), default=0)
    igv = Column(Numeric(18, 2), default=0)
    total = Column(Numeric(18, 2), default=0)
    id_empleado = Column(Integer, default=0)
    nota = Column(Text, default="")
    id_usuario = Column(Integer, default=0)
    fhcontrol = Column(DateTime, default=datetime.now)
    estacion = Column(String(20), default="")
    cerrado = Column(Boolean, default=False)

    # Relación Padre -> Hijo (Cascade delete)
    detalles = relationship("GuiaIngresoDetalle", back_populates="guia_ingreso", cascade="all, delete-orphan")

class GuiaIngresoDetalle(Base):
    __tablename__ = "sgc_guia_ingreso_det"

    id_guia_ingreso_det = Column(Integer, primary_key=True, index=True)
    id_guia_ingreso = Column(Integer, ForeignKey("sgc_guia_ingreso.id_guia_ingreso", ondelete="CASCADE"), default=0)
    origen = Column(String(8), default="")
    id_producto = Column(Integer, default=0)
    codigo_producto = Column(String(20), default="")
    nombre_producto = Column(String(100), default="")
    unidad_precio = Column(String(12), default="")
    equivalente = Column(Numeric(18, 7), default=0)
    cantidad = Column(Numeric(18, 3), default=0)
    precio_compra = Column(Numeric(18, 2), default=0)
    precio_bruto = Column(Numeric(18, 2), default=0)
    descuento = Column(Numeric(18, 2), default=0)
    sub_total = Column(Numeric(18, 2), default=0)
    igv = Column(Numeric(18, 2), default=0)
    total = Column(Numeric(18, 2), default=0)
    bonificacion_ = Column(Boolean, default=False)
    fecha_vencimiento = Column(Date, default=datetime.utcnow)
    lote = Column(String(12), default="")
    id_usuario = Column(Integer, default=0)
    fhcontrol = Column(DateTime, default=datetime.now)
    estacion = Column(String(20), default="")
    nota = Column(Text, default="")

    # Relación Hijo -> Padre
    guia_ingreso = relationship("GuiaIngreso", back_populates="detalles")

