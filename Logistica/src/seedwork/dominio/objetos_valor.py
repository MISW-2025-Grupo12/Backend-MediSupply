from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Direccion:
    valor: str

@dataclass(frozen=True)
class FechaEntrega:
    valor: datetime

@dataclass(frozen=True)
class ProductoID:
    valor: str

@dataclass(frozen=True)
class ClienteID:
    valor: str
