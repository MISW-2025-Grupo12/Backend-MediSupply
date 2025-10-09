from dataclasses import dataclass
from seedwork.dominio.reglas import ReglaNegocio

@dataclass
class VendedorIdNoPuedeSerVacio(ReglaNegocio):
    vendedor_id: str
    
    def es_valido(self) -> bool:
        return self.vendedor_id is not None and self.vendedor_id.strip() != ""

@dataclass
class ClienteIdNoPuedeSerVacio(ReglaNegocio):
    cliente_id: str
    
    def es_valido(self) -> bool:
        return self.cliente_id is not None and self.cliente_id.strip() != ""

@dataclass
class FechaProgramadaDebeSerFutura(ReglaNegocio):
    fecha_programada: str
    
    def es_valido(self) -> bool:
        from datetime import datetime
        try:
            fecha = datetime.fromisoformat(self.fecha_programada.replace('Z', '+00:00'))
            return fecha > datetime.now()
        except:
            return False

@dataclass
class EstadoVisitaDebeSerValido(ReglaNegocio):
    estado: str
    
    def es_valido(self) -> bool:
        return self.estado in ['pendiente', 'completada']

@dataclass
class DireccionNoPuedeSerVacia(ReglaNegocio):
    direccion: str
    
    def es_valido(self) -> bool:
        return self.direccion is not None and self.direccion.strip() != ""

@dataclass
class TelefonoNoPuedeSerVacio(ReglaNegocio):
    telefono: str
    
    def es_valido(self) -> bool:
        return self.telefono is not None and self.telefono.strip() != ""
