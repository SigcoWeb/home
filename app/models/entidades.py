from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

# (Tablas eliminadas a solicitud del usuario: sgc_proveedores, sgc_clientes)
# class SgcProveedor(Base):
#     __tablename__ = "sgc_proveedores" ...

# class SgcCliente(Base):
#     __tablename__ = "sgc_clientes" ...
