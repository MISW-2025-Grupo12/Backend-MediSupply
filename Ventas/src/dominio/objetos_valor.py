from dataclasses import dataclass
from datetime import datetime
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
