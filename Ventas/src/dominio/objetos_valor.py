from dataclasses import dataclass
from datetime import datetime, date, time
from seedwork.dominio.objetos_valor import ObjetoValor

@dataclass(frozen=True)
class EstadoVisita(ObjetoValor):
    estado: str
    
    def __post_init__(self):
        if self.estado not in ['pendiente', 'completada']:
            raise ValueError("Estado debe ser 'pendiente' o 'completada'")

@dataclass(frozen=True)
class FechaProgramada(ObjetoValor):
    fecha: datetime
    
    def __post_init__(self):
        # Permitir fechas de hoy o futuras (comparar solo el día)
        fecha_solo_dia = self.fecha.replace(hour=0, minute=0, second=0, microsecond=0)
        hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if fecha_solo_dia < hoy:
            raise ValueError("La fecha programada no puede ser en el pasado")

@dataclass(frozen=True)
class Direccion(ObjetoValor):
    direccion: str

@dataclass(frozen=True)
class Telefono(ObjetoValor):
    telefono: str

@dataclass(frozen=True)
class Descripcion(ObjetoValor):
    descripcion: str

@dataclass(frozen=True)
class FechaRealizada(ObjetoValor):
    fecha: date

@dataclass(frozen=True)
class HoraRealizada(ObjetoValor):
    hora: time

@dataclass(frozen=True)
class Novedades(ObjetoValor):
    novedades: str
    
    def __post_init__(self):
        if self.novedades and len(self.novedades) > 500:
            raise ValueError("Las novedades no pueden exceder 500 caracteres")

@dataclass(frozen=True)
class PedidoGenerado(ObjetoValor):
    pedido_generado: bool

@dataclass(frozen=True)
class EstadoPedido(ObjetoValor):
    estado: str
    
    def __post_init__(self):
        if self.estado not in ['borrador', 'confirmado', 'en_transito', 'entregado', 'cancelado']:
            raise ValueError("Estado debe ser 'borrador', 'confirmado', 'en_transito', 'entregado' o 'cancelado'")

@dataclass(frozen=True)
class Cantidad(ObjetoValor):
    valor: int
    
    def __post_init__(self):
        if self.valor < 0:
            raise ValueError("La cantidad no puede ser negativa")

@dataclass(frozen=True)
class Precio(ObjetoValor):
    valor: float
    
    def __post_init__(self):
        if self.valor < 0:
            raise ValueError("El precio no puede ser negativo")