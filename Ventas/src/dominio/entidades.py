from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from seedwork.dominio.entidades import Entidad, AgregacionRaiz
from .objetos_valor import EstadoVisita, FechaProgramada, Direccion, Telefono, Descripcion, FechaRealizada, HoraRealizada, Novedades, PedidoGenerado, EstadoPedido, Cantidad, Precio
from .eventos import VisitaCreada, PedidoCreado, PedidoConfirmado, ItemAgregado, ItemQuitado

@dataclass
class Visita(AgregacionRaiz):
    vendedor_id: str = field(default_factory=lambda: "")
    cliente_id: str = field(default_factory=lambda: "")
    fecha_programada: FechaProgramada = field(default_factory=lambda: FechaProgramada(datetime.now()))
    direccion: Direccion = field(default_factory=lambda: Direccion(""))
    telefono: Telefono = field(default_factory=lambda: Telefono(""))
    estado: EstadoVisita = field(default_factory=lambda: EstadoVisita("pendiente"))
    descripcion: Descripcion = field(default_factory=lambda: Descripcion(""))
    fecha_realizada: FechaRealizada = None
    hora_realizada: HoraRealizada = None
    novedades: Novedades = None
    pedido_generado: PedidoGenerado = None
    
    def __post_init__(self):
        super().__post_init__()
    
    def disparar_evento_creacion(self):
        """Dispara el evento de creación de la visita"""
        evento = VisitaCreada(
            visita_id=self.id,
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=self.fecha_programada.fecha,
            direccion=self.direccion.direccion,
            telefono=self.telefono.telefono,
            estado=self.estado.estado,
            descripcion=self.descripcion.descripcion
        )
        return evento
    
    def registrar_visita(self, fecha_realizada, hora_realizada, novedades, pedido_generado):
        """Registra los detalles de una visita realizada"""
        self.fecha_realizada = fecha_realizada
        self.hora_realizada = hora_realizada
        self.novedades = novedades
        self.pedido_generado = pedido_generado
        self.estado = EstadoVisita("completada")

@dataclass
class ItemPedido(Entidad):
    producto_id: str = field(default_factory=lambda: "")
    nombre_producto: str = field(default_factory=lambda: "")
    cantidad: Cantidad = field(default_factory=lambda: Cantidad(0))
    precio_unitario: Precio = field(default_factory=lambda: Precio(0.0))
    
    def __post_init__(self):
        super().__post_init__()
    
    def calcular_subtotal(self) -> float:
        """Calcula el subtotal del item"""
        return self.cantidad.valor * self.precio_unitario.valor
    
    def actualizar_cantidad(self, nueva_cantidad: int) -> bool:
        """Actualiza la cantidad del item"""
        if nueva_cantidad < 0:
            return False
        self.cantidad = Cantidad(nueva_cantidad)
        return True

@dataclass
class Pedido(AgregacionRaiz):
    vendedor_id: str = field(default_factory=lambda: "")
    cliente_id: str = field(default_factory=lambda: "")
    items: List[ItemPedido] = field(default_factory=lambda: [])
    estado: EstadoPedido = field(default_factory=lambda: EstadoPedido("borrador"))
    total: Precio = field(default_factory=lambda: Precio(0.0))
    
    def __post_init__(self):
        super().__post_init__()
    
    def agregar_item(self, item: ItemPedido) -> bool:
        """Agrega un item al pedido"""
        if self.estado.estado != "borrador":
            return False
        
        # Verificar si el producto ya existe en el pedido
        for i, existing_item in enumerate(self.items):
            if existing_item.producto_id == item.producto_id:
                # Actualizar cantidad del item existente
                nueva_cantidad = existing_item.cantidad.valor + item.cantidad.valor
                self.items[i].actualizar_cantidad(nueva_cantidad)
                self.calcular_total()
                return True
        
        # Agregar nuevo item
        self.items.append(item)
        self.calcular_total()
        return True
    
    def quitar_item(self, item_id: str) -> bool:
        """Quita un item del pedido"""
        if self.estado.estado != "borrador":
            return False
        
        for i, item in enumerate(self.items):
            if item.id == item_id:
                del self.items[i]
                self.calcular_total()
                return True
        return False
    
    def actualizar_cantidad_item(self, item_id: str, cantidad: int) -> bool:
        """Actualiza la cantidad de un item específico"""
        if self.estado.estado != "borrador":
            return False
        
        if cantidad <= 0:
            # Si cantidad es 0 o negativa, quitar el item
            return self.quitar_item(item_id)
        
        for item in self.items:
            if item.id == item_id:
                if item.actualizar_cantidad(cantidad):
                    self.calcular_total()
                    return True
        return False
    
    def calcular_total(self) -> float:
        """Calcula el total del pedido"""
        total = sum(item.calcular_subtotal() for item in self.items)
        self.total = Precio(total)
        return total
    
    def confirmar(self) -> bool:
        """Confirma el pedido"""
        if self.estado.estado != "borrador":
            return False
        
        if not self.items:
            return False
        
        if not self.cliente_id:
            return False
        
        self.estado = EstadoPedido("confirmado")
        return True
    
    def disparar_evento_creacion(self):
        """Dispara el evento de creación del pedido"""
        evento = PedidoCreado(
            pedido_id=self.id,
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            total=self.total.valor
        )
        return evento
    
    def disparar_evento_confirmacion(self):
        """Dispara el evento de confirmación del pedido"""
        items_data = []
        for item in self.items:
            items_data.append({
                'producto_id': item.producto_id,
                'cantidad': item.cantidad.valor
            })
        
        evento = PedidoConfirmado(
            pedido_id=self.id,
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            items=items_data,
            total=self.total.valor
        )
        return evento
