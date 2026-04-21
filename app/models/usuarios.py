from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.models.empleados import Empleado  # noqa  (asegura orden de registro)


class SgcModulo(Base):
    """Módulo del sistema (ej: TABLAS, ALMACEN, VENTAS)."""
    __tablename__ = "sgc_modulos"

    id_modulo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, index=True, nullable=False)
    descripcion = Column(String(200))
    activo = Column(Boolean, default=True)

    # Metadatos UI (zW-05).
    orden = Column(Integer)
    icono = Column(String(50))
    url_destino = Column(String(200))
    implementado = Column(Boolean, default=False)


class SgcOpcion(Base):
    """Opción dentro de un módulo (ej: Almacenes, Grupos, Usuarios)."""
    __tablename__ = "sgc_opciones"

    id_opcion = Column(Integer, primary_key=True, index=True)
    id_modulo = Column(Integer, ForeignKey("sgc_modulos.id_modulo"), nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(200))
    activo = Column(Boolean, default=True)

    modulo = relationship("SgcModulo")


class SgcUsuario(Base):
    """Usuario del tenant (los empleados que entran al sistema)."""
    __tablename__ = "sgc_usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    usuario = Column(String(15), unique=True, index=True, nullable=False)
    clave = Column(String(255), nullable=False)
    nombre_completo = Column(String(100))
    activo = Column(Boolean, default=True)
    tema = Column(String(10), default="oscuro")
    fecha_registro = Column(DateTime, default=datetime.now)

    # FK lógica a sgc_sys_usuarios_master.id. Nullable: si no hay mapping,
    # el usuario no puede autenticarse por el flujo de plataforma.
    id_sys_master = Column(Integer, nullable=True)

    # FK a empleados (RRHH). Nullable porque no todo usuario es empleado.
    id_empleado = Column(Integer, ForeignKey("sgc_empleados.id_empleado"), nullable=True)

    id_usuario_creador = Column(Integer, nullable=True)
    fhcontrol = Column(DateTime, default=datetime.now)
    estacion = Column(String(20), nullable=True)

    accesos_modulos = relationship("SgcUsuarioModulo", back_populates="usuario", cascade="all, delete-orphan")
    accesos_opciones = relationship("SgcUsuarioOpcion", back_populates="usuario", cascade="all, delete-orphan")
    empleado = relationship("Empleado")


class SgcUsuarioModulo(Base):
    """Acceso de un usuario a un módulo completo."""
    __tablename__ = "sgc_usuarios_modulos"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("sgc_usuarios.id_usuario"), nullable=False)
    id_modulo = Column(Integer, ForeignKey("sgc_modulos.id_modulo"), nullable=False)

    nombre_modulo = Column(String(100))
    descrip_modulo = Column(String(200))

    activo = Column(Boolean, default=True)

    usuario = relationship("SgcUsuario", back_populates="accesos_modulos")
    modulo = relationship("SgcModulo")


class SgcUsuarioOpcion(Base):
    """Acceso granular de un usuario a una opción, con permisos por botón."""
    __tablename__ = "sgc_usuarios_opciones"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("sgc_usuarios.id_usuario"), nullable=False)
    id_modulo = Column(Integer, ForeignKey("sgc_modulos.id_modulo"), nullable=False)
    id_opcion = Column(Integer, ForeignKey("sgc_opciones.id_opcion"), nullable=False)

    nombre_opcion = Column(String(100))
    descrip_opcion = Column(String(200))

    btn_nuevo = Column(Boolean, default=True)
    btn_editar = Column(Boolean, default=True)
    btn_eliminar = Column(Boolean, default=True)
    btn_pdf = Column(Boolean, default=True)
    btn_excel = Column(Boolean, default=True)
    btn_guardar = Column(Boolean, default=True)
    btn_otro = Column(Boolean, default=True)

    activo = Column(Boolean, default=True)

    usuario = relationship("SgcUsuario", back_populates="accesos_opciones")
    modulo = relationship("SgcModulo")
    opcion = relationship("SgcOpcion")
