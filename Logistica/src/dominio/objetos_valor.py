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

@dataclass(frozen=True)
class Cantidad:
    valor: int
    
    def __post_init__(self):
        if self.valor < 0:
            raise ValueError("La cantidad no puede ser negativa")

@dataclass(frozen=True)
class FechaVencimiento:
    valor: datetime
    
    def __post_init__(self):
        if self.valor < datetime.now():
            raise ValueError("La fecha de vencimiento no puede ser en el pasado")

@dataclass(frozen=True)
class BodegaID:
    valor: str

@dataclass(frozen=True)
class UbicacionFisica:
    bodega_id: str
    pasillo: str
    estante: str
    
    @property
    def descripcion(self) -> str:
        return f"Bodega #{self.bodega_id} - Pasillo {self.pasillo} - Estante {self.estante}"