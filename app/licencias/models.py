"""
Modelos extendidos de licencias para el panel de Walter.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Plan(Base):
    """Planes disponibles que Walter puede vender."""
    __tablename__ = "sgc_sys_planes"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True)        # basico | pro | enterprise
    nombre = Column(String(100))
    precio_mensual = Column(Numeric(10, 2))
    precio_anual = Column(Numeric(10, 2))
    max_usuarios = Column(Integer)
    modulos = Column(String)                        # JSON list de módulos incluidos
    activo = Column(Boolean, default=True)


class PagoLicencia(Base):
    """Registro de pagos de licencias."""
    __tablename__ = "sgc_sys_pagos_licencia"

    id = Column(Integer, primary_key=True, index=True)
    id_empresa = Column(Integer, ForeignKey("sgc_sys_empresas.id"))
    id_plan = Column(Integer, ForeignKey("sgc_sys_planes.id"))
    monto = Column(Numeric(10, 2))
    moneda = Column(String(3), default="PEN")
    periodo_inicio = Column(Date)
    periodo_fin = Column(Date)
    referencia_pago = Column(String(100))           # Nro operación banco, Yape, etc.
    nota = Column(Text, nullable=True)
    registrado_por = Column(String(100))            # usuario de Walter que registró
    created_at = Column(DateTime, default=datetime.now)
