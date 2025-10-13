from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando, ejecutar_comando
import uuid
import logging
from datetime import datetime
from aplicacion.dto import VisitaDTO
from aplicacion.dto_agregacion import VisitaAgregacionDTO
from dominio.entidades import Visita
from dominio.objetos_valor import EstadoVisita, FechaProgramada, Direccion, Telefono, Descripcion
from dominio.reglas import (
    VendedorIdNoPuedeSerVacio, ClienteIdNoPuedeSerVacio, FechaProgramadaDebeSerFutura,
    EstadoVisitaDebeSerValido, DireccionNoPuedeSerVacia, TelefonoNoPuedeSerVacio
)
from infraestructura.repositorios import RepositorioVisitaSQLite
from infraestructura.servicio_usuarios import ServicioUsuarios

logger = logging.getLogger(__name__)

@dataclass
class CrearVisita(Comando):
    vendedor_id: str
    cliente_id: str
    fecha_programada: datetime
    direccion: str
    telefono: str
    estado: str
    descripcion: str

class CrearVisitaHandler:
    def __init__(self, repositorio=None, servicio_usuarios=None):
        self.repositorio = repositorio or RepositorioVisitaSQLite()
        self.servicio_usuarios = servicio_usuarios or ServicioUsuarios()
    
    def handle(self, comando: CrearVisita) -> VisitaAgregacionDTO:
        try:
            # 1. Obtener y validar vendedor
            vendedor = self.servicio_usuarios.obtener_vendedor_por_id(comando.vendedor_id)
            if not vendedor:
                raise ValueError(f"Vendedor {comando.vendedor_id} no existe")
            
            # 2. Obtener y validar cliente
            cliente = self.servicio_usuarios.obtener_cliente_por_id(comando.cliente_id)
            if not cliente:
                raise ValueError(f"Cliente {comando.cliente_id} no existe")
            
            # 3. Crear el DTO de la visita
            visita_dto = VisitaDTO(
                vendedor_id=comando.vendedor_id,
                cliente_id=comando.cliente_id,
                fecha_programada=comando.fecha_programada,
                direccion=comando.direccion,
                telefono=comando.telefono,
                estado=comando.estado,
                descripcion=comando.descripcion
            )
            
            # 4. Crear entidad de dominio con validaciones
            visita_temp = Visita(
                vendedor_id=comando.vendedor_id,
                cliente_id=comando.cliente_id,
                fecha_programada=FechaProgramada(comando.fecha_programada),
                direccion=Direccion(comando.direccion),
                telefono=Telefono(comando.telefono),
                estado=EstadoVisita(comando.estado),
                descripcion=Descripcion(comando.descripcion)
            )
            
            # 5. Validar reglas de negocio
            from dominio.fabricas import FabricaVisita
            fabrica = FabricaVisita()
            
            fabrica.validar_regla(VendedorIdNoPuedeSerVacio(comando.vendedor_id))
            fabrica.validar_regla(ClienteIdNoPuedeSerVacio(comando.cliente_id))
            fabrica.validar_regla(FechaProgramadaDebeSerFutura(comando.fecha_programada.isoformat()))
            fabrica.validar_regla(EstadoVisitaDebeSerValido(comando.estado))
            fabrica.validar_regla(DireccionNoPuedeSerVacia(comando.direccion))
            fabrica.validar_regla(TelefonoNoPuedeSerVacio(comando.telefono))
            
            # 6. Disparar evento de creación
            visita_temp.disparar_evento_creacion()
            
            # 7. Guardar en SQLite
            visita_guardada = self.repositorio.crear(visita_dto)
            
            # 8. Construir agregación completa
            agregacion = VisitaAgregacionDTO(
                id=visita_guardada.id,
                fecha_programada=visita_guardada.fecha_programada,
                direccion=visita_guardada.direccion,
                telefono=visita_guardada.telefono,
                estado=visita_guardada.estado,
                descripcion=visita_guardada.descripcion,
                vendedor_id=vendedor['id'],
                vendedor_nombre=vendedor['nombre'],
                vendedor_email=vendedor['email'],
                vendedor_telefono=vendedor['telefono'],
                vendedor_direccion=vendedor['direccion'],
                cliente_id=cliente['id'],
                cliente_nombre=cliente['nombre'],
                cliente_email=cliente['email'],
                cliente_telefono=cliente['telefono'],
                cliente_direccion=cliente['direccion']
            )
            
            return agregacion
            
        except Exception as e:
            logger.error(f"Error creando visita: {e}")
            raise

@ejecutar_comando.register
def _(comando: CrearVisita):
    handler = CrearVisitaHandler()
    return handler.handle(comando)
