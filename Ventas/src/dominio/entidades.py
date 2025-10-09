from dataclasses import dataclass, field
from datetime import datetime
from seedwork.dominio.entidades import Entidad, AgregacionRaiz
from .objetos_valor import EstadoVisita, FechaProgramada, Direccion, Telefono, Descripcion
from .eventos import VisitaCreada

@dataclass
class Visita(AgregacionRaiz):
    vendedor_id: str = field(default_factory=lambda: "")
    cliente_id: str = field(default_factory=lambda: "")
    fecha_programada: FechaProgramada = field(default_factory=lambda: FechaProgramada(datetime.now()))
    direccion: Direccion = field(default_factory=lambda: Direccion(""))
    telefono: Telefono = field(default_factory=lambda: Telefono(""))
    estado: EstadoVisita = field(default_factory=lambda: EstadoVisita("pendiente"))
    descripcion: Descripcion = field(default_factory=lambda: Descripcion(""))
    
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
