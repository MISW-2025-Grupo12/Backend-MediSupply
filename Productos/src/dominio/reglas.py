from seedwork.dominio.reglas import ReglaNegocio
from .objetos_valor import Nombre, Descripcion, Precio, Stock, FechaVencimiento, Categoria, Proveedor
from datetime import datetime


class NombreProductoNoPuedeSerVacio(ReglaNegocio):
    nombre: Nombre
    def __init__(self, nombre, mensaje='El nombre del producto no puede ser vacio'):
        super().__init__(mensaje)
        self.nombre = nombre

    def es_valido(self) -> bool:
        return self.nombre is not None and self.nombre.nombre.strip() != ''


class DescripcionProductoNoPuedeSerVacio(ReglaNegocio):
    descripcion: Descripcion
    def __init__(self, descripcion, mensaje='La descripcion del producto no puede ser vacio'):
        super().__init__(mensaje)
        self.descripcion = descripcion

    def es_valido(self) -> bool:
        return self.descripcion is not None and self.descripcion.descripcion.strip() != ''


class PrecioProductoNoPuedeSerVacio(ReglaNegocio):
    precio: Precio
    def __init__(self, precio, mensaje='El precio del producto no puede ser vacio'):
        super().__init__(mensaje)
        self.precio = precio
    
    def es_valido(self) -> bool:
        return self.precio is not None and self.precio.precio > 0


class PrecioProductoNoPuedeSerMenorACero(ReglaNegocio):
    precio: Precio
    def __init__(self, precio, mensaje='El precio del producto no puede ser menor a cero'):
        super().__init__(mensaje)
        self.precio = precio

    def es_valido(self) -> bool:
        return self.precio is not None and self.precio.precio > 0

class PrecioProductoDebeSerNumerico(ReglaNegocio):
    precio: Precio
    def __init__(self, precio, mensaje='El precio del producto debe ser numerico'):
        super().__init__(mensaje)
        self.precio = precio

    def es_valido(self) -> bool:
        return isinstance(self.precio.precio, float)



class StockProductoDebeSerPositivo(ReglaNegocio):
    stock: Stock
    def __init__(self, stock, mensaje='El stock del producto debe ser mayor a cero'):
        super().__init__(mensaje)
        self.stock = stock

    def es_valido(self) -> bool:
        return self.stock is not None and self.stock.stock >= 0

class FechaVencimientoDebeSerFutura(ReglaNegocio):
    fecha_vencimiento: FechaVencimiento
    def __init__(self, fecha_vencimiento, mensaje='La fecha de vencimiento debe ser futura'):
        super().__init__(mensaje)
        self.fecha_vencimiento = fecha_vencimiento

    def es_valido(self) -> bool:
        if self.fecha_vencimiento is None:
            return False
        
        fecha_vencimiento = self.fecha_vencimiento.fecha
        fecha_actual = datetime.now()
        
        # Normalizar ambas fechas para evitar problemas de zona horaria
        if fecha_vencimiento.tzinfo is not None:
            fecha_vencimiento = fecha_vencimiento.replace(tzinfo=None)
        if fecha_actual.tzinfo is not None:
            fecha_actual = fecha_actual.replace(tzinfo=None)
            
        return fecha_vencimiento > fecha_actual

class CategoriaProductoNoPuedeSerVacia(ReglaNegocio):
    categoria: Categoria
    def __init__(self, categoria, mensaje='La categoría del producto no puede ser vacía'):
        super().__init__(mensaje)
        self.categoria = categoria

    def es_valido(self) -> bool:
        return self.categoria is not None and self.categoria.nombre.strip() != ''

class ProveedorProductoNoPuedeSerVacio(ReglaNegocio):
    proveedor: Proveedor
    def __init__(self, proveedor, mensaje='El proveedor del producto no puede ser vacío'):
        super().__init__(mensaje)
        self.proveedor = proveedor

    def es_valido(self) -> bool:
        return self.proveedor is not None and self.proveedor.nombre.strip() != ''

class CategoriaIdNoPuedeSerVacio(ReglaNegocio):
    categoria_id: str
    def __init__(self, categoria_id, mensaje='El ID de categoría no puede ser vacío'):
        super().__init__(mensaje)
        self.categoria_id = categoria_id

    def es_valido(self) -> bool:
        return self.categoria_id is not None and self.categoria_id.strip() != ''