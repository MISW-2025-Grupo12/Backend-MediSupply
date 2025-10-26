from dataclasses import dataclass
from datetime import date, time
from seedwork.dominio.reglas import ReglaNegocio

@dataclass
class VendedorIdNoPuedeSerVacio(ReglaNegocio):
    vendedor_id: str
    
    def es_valido(self) -> bool:
        return self.vendedor_id is not None and self.vendedor_id.strip() != ""

@dataclass
class ClienteIdNoPuedeSerVacio(ReglaNegocio):
    cliente_id: str
    
    def es_valido(self) -> bool:
        return self.cliente_id is not None and self.cliente_id.strip() != ""

@dataclass
class FechaProgramadaDebeSerFutura(ReglaNegocio):
    fecha_programada: str
    
    def es_valido(self) -> bool:
        from datetime import datetime
        try:
            fecha = datetime.fromisoformat(self.fecha_programada.replace('Z', '+00:00'))
            fecha_solo_dia = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
            hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            return fecha_solo_dia >= hoy
        except:
            return False

@dataclass
class EstadoVisitaDebeSerValido(ReglaNegocio):
    estado: str
    
    def es_valido(self) -> bool:
        return self.estado in ['pendiente', 'completada']

@dataclass
class DireccionNoPuedeSerVacia(ReglaNegocio):
    direccion: str
    
    def es_valido(self) -> bool:
        return self.direccion is not None and self.direccion.strip() != ""

@dataclass
class TelefonoNoPuedeSerVacio(ReglaNegocio):
    telefono: str
    
    def es_valido(self) -> bool:
        return self.telefono is not None and self.telefono.strip() != ""

@dataclass
class FechaRealizadaNoPuedeEstarVacia(ReglaNegocio):
    fecha_realizada: date
    
    def es_valido(self) -> bool:
        return self.fecha_realizada is not None

@dataclass
class FechaRealizadaFormatoISO(ReglaNegocio):
    fecha_realizada_str: str
    
    def es_valido(self) -> bool:
        try:
            date.fromisoformat(self.fecha_realizada_str)
            return True
        except ValueError:
            return False

@dataclass
class FechaRealizadaNoPuedeSerFutura(ReglaNegocio):
    fecha_realizada: date
    
    def es_valido(self) -> bool:
        from datetime import date
        return self.fecha_realizada <= date.today()

@dataclass
class HoraRealizadaNoPuedeEstarVacia(ReglaNegocio):
    hora_realizada: time
    
    def es_valido(self) -> bool:
        return self.hora_realizada is not None

@dataclass
class HoraRealizadaFormatoISO(ReglaNegocio):
    hora_realizada_str: str
    
    def es_valido(self) -> bool:
        try:
            time.fromisoformat(self.hora_realizada_str)
            return True
        except ValueError:
            return False

@dataclass
class NovedadesMaximo500Caracteres(ReglaNegocio):
    novedades: str
    
    def es_valido(self) -> bool:
        return self.novedades is None or len(self.novedades) <= 500

@dataclass
class ClienteDebeEstarSeleccionado(ReglaNegocio):
    cliente_id: str
    
    def es_valido(self) -> bool:
        return self.cliente_id is not None and self.cliente_id.strip() != ""

# Reglas de negocio para pedidos
@dataclass
class PedidoDebeTenerItems(ReglaNegocio):
    items: list
    
    def es_valido(self) -> bool:
        return self.items is not None and len(self.items) > 0

@dataclass
class ItemPedidoDebeTenerProductoId(ReglaNegocio):
    producto_id: str
    
    def es_valido(self) -> bool:
        return self.producto_id is not None and self.producto_id.strip() != ""

@dataclass
class ItemPedidoDebeTenerCantidadPositiva(ReglaNegocio):
    cantidad: int
    
    def es_valido(self) -> bool:
        return self.cantidad is not None and self.cantidad > 0

@dataclass
class PedidoDebeEstarEnEstadoBorrador(ReglaNegocio):
    estado: str
    
    def es_valido(self) -> bool:
        return self.estado == "borrador"

@dataclass
class PedidoDebeTenerCliente(ReglaNegocio):
    cliente_id: str
    
    def es_valido(self) -> bool:
        return self.cliente_id is not None and self.cliente_id.strip() != ""

@dataclass
class PedidoDebeTenerVendedor(ReglaNegocio):
    vendedor_id: str
    
    def es_valido(self) -> bool:
        return self.vendedor_id is not None and self.vendedor_id.strip() != ""

@dataclass
class ItemsDebenSerLista(ReglaNegocio):
    items: any
    
    def es_valido(self) -> bool:
        return isinstance(self.items, list)

@dataclass
class ItemDebeSerDiccionario(ReglaNegocio):
    item: any
    
    def es_valido(self) -> bool:
        return isinstance(self.item, dict)