from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, Date, Numeric, func
from sqlalchemy.orm import relationship
from app.database import Base

from app.models.clasificador_clientes import SgcClasificadorCli
from app.models.almacen import SgcAlmacen

class SgcCatalogoGrupo(Base):
    __tablename__ = "sgc_catalogo_grupo"

    id_grupo = Column(Integer, primary_key=True, index=True)
    nombre_grupo = Column(String(50), nullable=False)

    id_usuario = Column(Integer, nullable=True)
    fhcontrol = Column(DateTime, default=func.now())
    estacion = Column(String(20), nullable=True)

class SgcCatalogoModelo(Base):
    __tablename__ = "sgc_catalogo_modelo"
    
    id_modelo = Column(Integer, primary_key=True, index=True)
    nombre_modelo = Column(String(20))

class SgcCatalogoColor(Base):
    __tablename__ = "sgc_catalogo_color"
    
    id_color = Column(Integer, primary_key=True, index=True)
    nombre_color = Column(String(20))

class SgcCatalogoTalla(Base):
    __tablename__ = "sgc_catalogo_talla"
    
    id_talla = Column(Integer, primary_key=True, index=True)
    nombre_talla = Column(String(20))

class SgcCatalogoProductos(Base):
    __tablename__ = "sgc_catalogo_productos"
    
    id_producto = Column(Integer, primary_key=True, index=True)
    codigo_producto = Column(String(20))
    nombre_producto = Column(String(100))
    
    id_clapro1 = Column(Integer, ForeignKey("sgc_clasificador_pro1.id_clapro1"), nullable=True)
    id_clapro2 = Column(Integer, ForeignKey("sgc_clasificador_pro2.id_clapro2"), nullable=True)
    id_clapro3 = Column(Integer, ForeignKey("sgc_clasificador_pro3.id_clapro3"), nullable=True)
    
    imagen = Column(String(20))
    
    id_unidad = Column(Integer, ForeignKey("sgc_unidades.id_unidad"), nullable=True)
    id_marca = Column(Integer, ForeignKey("sgc_marcas.id_marca"), nullable=True)
    id_modelo = Column(Integer)
    
    ubicacion = Column("ubicacion", String(20))
    cod_sunat = Column(String(12))
    
    estado = Column(Boolean, default=True)
    stock_min = Column(Integer)
    stock_max = Column(Integer)
    
    id_agenda_pro = Column(Integer, ForeignKey("sgc_agenda_proveedores.id_agenda_pro"), nullable=True)
    id_grupo = Column(Integer, ForeignKey("sgc_catalogo_grupo.id_grupo"), nullable=True)
    
    id_color = Column(Integer)
    id_talla = Column(Integer)
    
    precio_costo = Column(Numeric(18,2), default=0.00)
    precio_venta = Column(Numeric(18,2), default=0.00)
    nota = Column(Text)
    origen = Column(String(8), default='')
    
    inventariado = Column(Boolean, default=False)
    combo = Column(Boolean, default=False)
    
    cod_diremid = Column(String(12))
    reg_sanitario = Column(String(12))
    caracteristica = Column(Text)
    
    imprime_combo = Column(Boolean, default=False)
    
    id_usuario = Column(Integer)
    fhcontrol = Column(DateTime, default=func.now())
    estacion = Column(String(20))
    
    # Relationships
    grupo = relationship("SgcCatalogoGrupo")
    unidad = relationship("UnidadMedida", primaryjoin="SgcCatalogoProductos.id_unidad==UnidadMedida.id_unidad", uselist=False)
    marca = relationship("Marca", primaryjoin="SgcCatalogoProductos.id_marca==Marca.id_marca", uselist=False)

class SgcCatalogoPrecios(Base):
    __tablename__ = "sgc_catalogo_precios"
    
    id_precio = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("sgc_catalogo_productos.id_producto"))
    estado = Column(Boolean, default=True)
    nombre_precio = Column(String(100))
    unidad_precio = Column(String(12))
    equivalente = Column(Numeric(18,7))
    
    id_clacli = Column(Integer, ForeignKey("sgc_clasificador_cli.id_clacli"), nullable=True)
    id_almacen = Column(Integer, ForeignKey("sgc_almacen.id_almacen"), nullable=True)
    
    peso = Column(Numeric(18,3))
    vta_minima = Column(Integer)
    
    id_moneda = Column(Integer)
    tc = Column(Numeric(18,3))
    
    # precio_compra_me Removed
    precio_compra = Column(Numeric(18,7))
    flete = Column(Numeric(18,7))
    gastos = Column(Numeric(18,7))
    precio_costo = Column(Numeric(18,7))
    margen = Column(Numeric(18,2))
    precio_venta = Column(Numeric(18,7))
    
    redondeo = Column(Boolean, default=True)
    imprime_nombre = Column(Boolean, default=False)
    fraccionar = Column(Boolean, default=False)
    unidad_compra = Column(Boolean, default=False)
    unidad_venta = Column(Boolean, default=True)
    bonificacion = Column(Boolean, default=False)
    venta_importe = Column(Boolean, default=False)
    balanza = Column(Boolean, default=False)
    ibolsas = Column(Boolean, default=False)
    oferta = Column(Boolean, default=False)
    
    nota = Column(Text)
    
    id_usuario = Column(Integer)
    fhcontrol = Column(DateTime, default=func.now())
    estacion = Column(String(20))
    
    # Relationships
    producto = relationship("SgcCatalogoProductos")
    clasificador = relationship("SgcClasificadorCli", foreign_keys=[id_clacli])
    almacen = relationship("SgcAlmacen", foreign_keys=[id_almacen])

class SgcCatalogoCombo(Base):
    __tablename__ = "sgc_catalogo_combo"
    
    id_combo = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("sgc_catalogo_productos.id_producto"))
    id_precio = Column(Integer, ForeignKey("sgc_catalogo_precios.id_precio"))
    unidad_precio = Column(String(12))
    equivalente = Column(Numeric(18,7))
    cantidad = Column(Numeric(18,3))
    precio_costo = Column(Numeric(18,7))
    precio_venta = Column(Numeric(18,7))
    total_costo = Column(Numeric(18,2))
    total_venta = Column(Numeric(18,2))
    
    # Relationships
    # producto_padre = relationship("SgcCatalogoProductos", foreign_keys=[id_producto]) # Already implies backref usually
    precio_ref = relationship("SgcCatalogoPrecios")

    @property
    def id_producto_componente(self):
        return self.precio_ref.id_producto if self.precio_ref else None

    @property
    def nombre_producto(self):
        return self.precio_ref.producto.nombre_producto if self.precio_ref and self.precio_ref.producto else None
        
    @property
    def codigo_producto(self):
        return self.precio_ref.producto.codigo_producto if self.precio_ref and self.precio_ref.producto else None
    
    # @property
    # def unidad_precio(self):
    #    return self.precio_ref.unidad_precio if self.precio_ref else None

class SgcCatalogoBarras(Base):
    __tablename__ = "sgc_catalogo_barras"
    
    id_barra = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("sgc_catalogo_productos.id_producto"))
    id_precio = Column(Integer, ForeignKey("sgc_catalogo_precios.id_precio"))
    codigo_barra = Column(String(20))

