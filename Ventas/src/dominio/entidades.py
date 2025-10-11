from dataclasses import dataclass, field
from datetime import datetime
from seedwork.dominio.entidades import Entidad, AgregacionRaiz
from .objetos_valor import EstadoVisita, FechaProgramada, Direccion, Telefono, Descripcion, FechaRealizada, HoraRealizada, Novedades, PedidoGenerado
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
