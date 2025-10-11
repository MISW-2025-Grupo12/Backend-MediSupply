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
        if self.fecha <= datetime.now():
            raise ValueError("La fecha programada debe ser futura")

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
        if self.estado not in ['borrador', 'confirmado', 'cancelado']:
            raise ValueError("Estado debe ser 'borrador', 'confirmado' o 'cancelado'")

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