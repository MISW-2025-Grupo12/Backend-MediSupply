from dataclasses import dataclass
from datetime import date, time
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

@dataclass
class FechaRealizadaNoPuedeEstarVacia(ReglaNegocio):
    fecha_realizada: date
    
    def es_valido(self) -> bool:
        return self.fecha_realizada is not None

@dataclass
class FechaRealizadaFormatoISO(ReglaNegocio):
    fecha_realizada_str: str
    
    def es_valido(self) -> bool:
        try:
            date.fromisoformat(self.fecha_realizada_str)
            return True
        except ValueError:
            return False

@dataclass
class FechaRealizadaNoPuedeSerFutura(ReglaNegocio):
    fecha_realizada: date
    
    def es_valido(self) -> bool:
        from datetime import date
        return self.fecha_realizada <= date.today()

@dataclass
class HoraRealizadaNoPuedeEstarVacia(ReglaNegocio):
    hora_realizada: time
    
    def es_valido(self) -> bool:
        return self.hora_realizada is not None

@dataclass
class HoraRealizadaFormatoISO(ReglaNegocio):
    hora_realizada_str: str
    
    def es_valido(self) -> bool:
        try:
            time.fromisoformat(self.hora_realizada_str)
            return True
        except ValueError:
            return False

@dataclass
class NovedadesMaximo500Caracteres(ReglaNegocio):
    novedades: str
    
    def es_valido(self) -> bool:
        return self.novedades is None or len(self.novedades) <= 500

@dataclass
class ClienteDebeEstarSeleccionado(ReglaNegocio):
    cliente_id: str
    
    def es_valido(self) -> bool:
        return self.cliente_id is not None and self.cliente_id.strip() != ""
