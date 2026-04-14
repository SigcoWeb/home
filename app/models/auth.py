from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from app.models.empleados import Empleado # Import Empleado model

class SgcModulo(Base):
    __tablename__ = "sgc_modulos"

    id_modulo = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, index=True)
    descripcion = Column(String(200))
    activo = Column(Boolean, default=True)

class SgcOpcion(Base):
    __tablename__ = "sgc_opciones"

    id_opcion = Column(Integer, primary_key=True, index=True)
    id_modulo = Column(Integer, ForeignKey("sgc_modulos.id_modulo"))
    nombre = Column(String(100))
    descripcion = Column(String(200))
    activo = Column(Boolean, default=True)

    modulo = relationship("SgcModulo")

class SgcUsuario(Base):
    __tablename__ = "sgc_usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    usuario = Column(String(15), unique=True, index=True)
    clave = Column(String(100)) # Store hashed password
    nombre_completo = Column(String(100))
    activo = Column(Boolean, default=True)
    tema = Column(String(10), default="claro")
    fecha_registro = Column(DateTime, default=datetime.now)

    # Relationships to access privileges
    accesos_modulos = relationship("SgcUsuarioModulo", back_populates="usuario")
    accesos_opciones = relationship("SgcUsuarioOpcion", back_populates="usuario")
    
    # Relationship to Personal
    id_personal = Column(Integer, ForeignKey("sgc_empleados.id_empleado"), nullable=True)
    personal = relationship("Empleado")

class SgcUsuarioModulo(Base):
    __tablename__ = "sgc_usuarios_modulos"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("sgc_usuarios.id_usuario"))
    id_modulo = Column(Integer, ForeignKey("sgc_modulos.id_modulo"))
    nombre_modulo = Column(String(100)) # Redundant but requested
    descrip_modulo = Column(String(100)) # Redundant but requested
    activo = Column(Boolean, default=True)

    usuario = relationship("SgcUsuario", back_populates="accesos_modulos")
    modulo = relationship("SgcModulo")

class SgcUsuarioOpcion(Base):
    __tablename__ = "sgc_usuarios_opciones"

    id = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("sgc_usuarios.id_usuario"))
    id_modulo = Column(Integer, ForeignKey("sgc_modulos.id_modulo"))
    id_opcion = Column(Integer, ForeignKey("sgc_opciones.id_opcion"))
    
    # Redundant fields as requested
    nombre_opcion = Column(String(100))
    descrip_opcion = Column(String(100))
    
    # Permissions
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
