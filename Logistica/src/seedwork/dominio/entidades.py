from dataclasses import dataclass, field
from datetime import datetime
from seedwork.dominio.entidades import Entidad, AgregacionRaiz
from .objetos_valor import Direccion, FechaEntrega, ProductoID, ClienteID
from .eventos import EntregaCreada

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
