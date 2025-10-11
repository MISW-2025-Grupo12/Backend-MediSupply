from dataclasses import dataclass, field
from datetime import datetime
from seedwork.dominio.entidades import Entidad, AgregacionRaiz
from .objetos_valor import Direccion, FechaEntrega, ProductoID, ClienteID, Cantidad, FechaVencimiento
from .eventos import EntregaCreada, InventarioReservado, InventarioDescontado

@dataclass
class Entrega(AgregacionRaiz):
    direccion: Direccion = field(default_factory=lambda: Direccion(""))
    fecha_entrega: FechaEntrega = field(default_factory=lambda: FechaEntrega(datetime.now()))
    producto_id: ProductoID = field(default_factory=lambda: ProductoID(""))
    cliente_id: ClienteID = field(default_factory=lambda: ClienteID(""))

    def __post_init__(self):
        super().__post_init__()

    def disparar_evento_creacion(self):
        """Dispara el evento de creación de una entrega"""
        evento = EntregaCreada(
            entrega_id=self.id,
            direccion=self.direccion.valor,
            fecha_entrega=self.fecha_entrega.valor,
            producto_id=self.producto_id.valor,
            cliente_id=self.cliente_id.valor
        )
        print(f"Entrega creada: {evento.entrega_id} → {evento.direccion}")

@dataclass
class Inventario(AgregacionRaiz):
    producto_id: ProductoID = field(default_factory=lambda: ProductoID(""))
    cantidad_disponible: Cantidad = field(default_factory=lambda: Cantidad(0))
    cantidad_reservada: Cantidad = field(default_factory=lambda: Cantidad(0))
    fecha_vencimiento: FechaVencimiento = field(default_factory=lambda: FechaVencimiento(datetime.now()))
    
    def __post_init__(self):
        super().__post_init__()
    
    def reservar_cantidad(self, cantidad: int) -> bool:
        """Reserva una cantidad del inventario (mueve de disponible a reservada)"""
        if cantidad <= 0:
            return False
        
        if cantidad > self.cantidad_disponible.valor:
            return False
        
        self.cantidad_disponible = Cantidad(self.cantidad_disponible.valor - cantidad)
        self.cantidad_reservada = Cantidad(self.cantidad_reservada.valor + cantidad)
        
        # Disparar evento
        evento = InventarioReservado(
            producto_id=self.producto_id.valor,
            cantidad_reservada=cantidad,
            cantidad_disponible_restante=self.cantidad_disponible.valor
        )
        return True
    
    def descontar_cantidad(self, cantidad: int) -> bool:
        """Descuenta una cantidad del inventario reservado (sale del sistema)"""
        if cantidad <= 0:
            return False
        
        if cantidad > self.cantidad_reservada.valor:
            return False
        
        self.cantidad_reservada = Cantidad(self.cantidad_reservada.valor - cantidad)
        
        # Disparar evento
        evento = InventarioDescontado(
            producto_id=self.producto_id.valor,
            cantidad_descontada=cantidad,
            cantidad_reservada_restante=self.cantidad_reservada.valor
        )
        return True
