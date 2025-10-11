from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando, ejecutar_comando
import logging
from datetime import date, time
from aplicacion.dto import VisitaDTO
from infraestructura.repositorios import RepositorioVisitaSQLite
from dominio.reglas import (
    FechaRealizadaNoPuedeEstarVacia,
    FechaRealizadaFormatoISO,
    FechaRealizadaNoPuedeSerFutura,
    HoraRealizadaNoPuedeEstarVacia,
    HoraRealizadaFormatoISO,
    NovedadesMaximo500Caracteres,
    ClienteDebeEstarSeleccionado
)

logger = logging.getLogger(__name__)

@dataclass
class RegistrarVisita(Comando):
    visita_id: str
    fecha_realizada: str
    hora_realizada: str
    cliente_id: str
    novedades: str = None
    pedido_generado: bool = False

class RegistrarVisitaHandler:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or RepositorioVisitaSQLite()
    
    def handle(self, comando: RegistrarVisita) -> VisitaDTO:
        try:
            # Validar formato de fecha
            regla_fecha_formato = FechaRealizadaFormatoISO(comando.fecha_realizada)
            if not regla_fecha_formato.es_valido():
                raise ValueError("Formato de fecha inválido. Use formato YYYY-MM-DD")
            
            # Validar formato de hora
            regla_hora_formato = HoraRealizadaFormatoISO(comando.hora_realizada)
            if not regla_hora_formato.es_valido():
                raise ValueError("Formato de hora inválido. Use formato HH:MM:SS o HH:MM")
            
            # Parsear fecha y hora
            fecha_realizada = date.fromisoformat(comando.fecha_realizada)
            hora_realizada = time.fromisoformat(comando.hora_realizada)
            
            # Validar reglas de negocio
            regla_fecha_vacia = FechaRealizadaNoPuedeEstarVacia(fecha_realizada)
            if not regla_fecha_vacia.es_valido():
                raise ValueError("La fecha realizada no puede estar vacía")
            
            regla_fecha_futura = FechaRealizadaNoPuedeSerFutura(fecha_realizada)
            if not regla_fecha_futura.es_valido():
                raise ValueError("La fecha realizada no puede ser futura")
            
            regla_hora_vacia = HoraRealizadaNoPuedeEstarVacia(hora_realizada)
            if not regla_hora_vacia.es_valido():
                raise ValueError("La hora realizada no puede estar vacía")
            
            regla_cliente = ClienteDebeEstarSeleccionado(comando.cliente_id)
            if not regla_cliente.es_valido():
                raise ValueError("Debe seleccionar un cliente")
            
            regla_novedades = NovedadesMaximo500Caracteres(comando.novedades)
            if not regla_novedades.es_valido():
                raise ValueError("Las novedades no pueden exceder 500 caracteres")
            
            # Obtener visita existente
            visita_existente = self.repositorio.obtener_por_id(comando.visita_id)
            if not visita_existente:
                raise ValueError(f"Visita {comando.visita_id} no encontrada")
            
            # Crear DTO actualizado
            visita_actualizada = VisitaDTO(
                id=visita_existente.id,
                vendedor_id=visita_existente.vendedor_id,
                cliente_id=comando.cliente_id,
                fecha_programada=visita_existente.fecha_programada,
                direccion=visita_existente.direccion,
                telefono=visita_existente.telefono,
                estado="completada",
                descripcion=visita_existente.descripcion,
                fecha_realizada=fecha_realizada,
                hora_realizada=hora_realizada,
                novedades=comando.novedades,
                pedido_generado=comando.pedido_generado
            )
            
            # Actualizar en repositorio
            visita_guardada = self.repositorio.actualizar(visita_actualizada)
            
            return visita_guardada
            
        except ValueError as e:
            logger.error(f"Error de validación en registrar visita: {e}")
            raise
        except Exception as e:
            logger.error(f"Error registrando visita: {e}")
            raise

@ejecutar_comando.register
def _(comando: RegistrarVisita):
    handler = RegistrarVisitaHandler()
    return handler.handle(comando)
