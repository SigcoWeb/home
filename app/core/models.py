"""
Tablas del sistema sigcoweb (schema public).
Control de empresas, licencias y usuarios master.
Walter administra estas tablas desde su panel.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Empresa(Base):
    __tablename__ = "sgc_sys_empresas"

    id = Column(Integer, primary_key=True, index=True)
    ruc = Column(String(11), unique=True, index=True, nullable=False)
    razon_social = Column(String(200), nullable=False)
    nombre_comercial = Column(String(200), nullable=True)
    schema_db = Column(String(50), unique=True, nullable=False)

    plan = Column(String(20), default="basico")
    modulos_activos = Column(JSON, default=list)
    activo = Column(Boolean, default=True)

    fecha_inicio = Column(Date, nullable=True)
    fecha_vencimiento = Column(Date, nullable=True)
    max_usuarios = Column(Integer, default=3)

    ips_permitidas = Column(JSON, default=list)
    gps_lat_min = Column(String(20), nullable=True)
    gps_lat_max = Column(String(20), nullable=True)
    gps_lon_min = Column(String(20), nullable=True)
    gps_lon_max = Column(String(20), nullable=True)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    licencia = relationship("Licencia", back_populates="empresa", uselist=False)
    usuarios_master = relationship("UsuarioMaster", back_populates="empresa")


class Licencia(Base):
    __tablename__ = "sgc_sys_licencias"

    id = Column(Integer, primary_key=True, index=True)
    id_empresa = Column(Integer, ForeignKey("sgc_sys_empresas.id"), unique=True)
    clave_licencia = Column(String(64), unique=True, index=True)
    modo = Column(String(10), default="cloud")      # cloud | local
    trial = Column(Boolean, default=False)
    activa = Column(Boolean, default=True)
    fecha_activacion = Column(DateTime, default=datetime.now)
    fecha_vencimiento = Column(Date, nullable=True)
    ultimo_ping = Column(DateTime, nullable=True)

    empresa = relationship("Empresa", back_populates="licencia")


class UsuarioMaster(Base):
    """Usuario administrador de la empresa (schema public)."""
    __tablename__ = "sgc_sys_usuarios_master"

    id = Column(Integer, primary_key=True, index=True)
    id_empresa = Column(Integer, ForeignKey("sgc_sys_empresas.id"))
    email = Column(String(200), unique=True, index=True)
    clave_hash = Column(String(200))
    nombre = Column(String(100))
    activo = Column(Boolean, default=True)
    es_superadmin = Column(Boolean, default=False)  # solo para Walter
    created_at = Column(DateTime, default=datetime.now)

    empresa = relationship("Empresa", back_populates="usuarios_master")


class LogSistema(Base):
    __tablename__ = "sgc_sys_log"

    id = Column(Integer, primary_key=True, index=True)
    id_empresa = Column(Integer, ForeignKey("sgc_sys_empresas.id"), nullable=True)
    tipo = Column(String(30))
    descripcion = Column(Text)
    ip = Column(String(50), nullable=True)
    datos = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
