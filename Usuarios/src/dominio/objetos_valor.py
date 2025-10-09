from dataclasses import dataclass
from seedwork.dominio.objetos_valor import ObjetoValor

@dataclass(frozen=True)
class Nombre(ObjetoValor):
    nombre: str

@dataclass(frozen=True)
class Email(ObjetoValor):
    email: str

@dataclass(frozen=True)
class Direccion(ObjetoValor):
    direccion: str

@dataclass(frozen=True)
class Telefono(ObjetoValor):
    telefono: str