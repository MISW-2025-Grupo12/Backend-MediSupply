from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from seedwork.dominio.entidades import Entidad, AgregacionRaiz
from .objetos_valor import Direccion, FechaEntrega, ProductoID, ClienteID, Cantidad, FechaVencimiento, BodegaID, FechaRuta, RepartidorID, EstadoRuta, EntregaAsignada
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
            pedido={  # ✅ reemplazo de producto_id y cliente_id
                "producto_id": self.producto_id.valor,
                "cliente_id": self.cliente_id.valor
            }
        )
        print(f"Entrega creada: {evento.entrega_id} → {evento.direccion}")

@dataclass
class Inventario(AgregacionRaiz):
    producto_id: ProductoID = field(default_factory=lambda: ProductoID(""))
    cantidad_disponible: Cantidad = field(default_factory=lambda: Cantidad(0))
    cantidad_reservada: Cantidad = field(default_factory=lambda: Cantidad(0))
    fecha_vencimiento: FechaVencimiento = field(default_factory=lambda: FechaVencimiento(datetime.now()))
    bodega_id: str = "" 
    pasillo: str = ""
    estante: str = "" 
    
    @property
    def ubicacion_fisica(self) -> str:
        if self.bodega_id and self.pasillo and self.estante:
            return f"Bodega #{self.bodega_id} - Pasillo {self.pasillo} - Estante {self.estante}"
        return "Sin ubicación asignada"
    
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

@dataclass
class Bodega(AgregacionRaiz):
    nombre: str = ""
    direccion: str = ""
    
    def __post_init__(self):
        super().__post_init__()


@dataclass
class Ruta(AgregacionRaiz):
    repartidor_id: Optional[RepartidorID] = None
    fecha_ruta: FechaRuta = field(default_factory=lambda: FechaRuta(datetime.now().date()))
    estado: EstadoRuta = field(default_factory=lambda: EstadoRuta("Pendiente"))
    entregas: List[EntregaAsignada] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.repartidor_id, RepartidorID):
            raise ValueError("La ruta debe tener un repartidor asignado")

    def agregar_entrega(self, entrega: EntregaAsignada):
        if any(e.entrega_id == entrega.entrega_id for e in self.entregas):
            raise ValueError("La entrega ya está asociada a esta ruta")

        if entrega.fecha_entrega.date() != self.fecha_ruta.valor:
            raise ValueError("La fecha de la entrega no coincide con la fecha de la ruta")

        self.entregas.append(entrega)

    def establecer_en_proceso(self):
        self.estado = EstadoRuta("EnProceso")

    def establecer_completada(self):
        self.estado = EstadoRuta("Completada")

    def puede_iniciar(self) -> bool:
        return self.estado.valor == "Pendiente" and len(self.entregas) > 0

    def puede_completar(self) -> bool:
        return self.estado.valor == "EnProceso" and len(self.entregas) > 0
