from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando, ejecutar_comando
import uuid
import logging
from aplicacion.dto import ClienteDTO
from dominio.entidades import Cliente
from dominio.objetos_valor import Nombre, Email, Telefono, Direccion, Identificacion, Estado
from infraestructura.repositorios import RepositorioClienteSQLite

logger = logging.getLogger(__name__)

@dataclass
class CrearCliente(Comando):
    nombre: str
    email: str
    identificacion: str
    telefono: str
    direccion: str

class CrearClienteHandler:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or RepositorioClienteSQLite()
    
    def handle(self, comando: CrearCliente) -> ClienteDTO:
        try:
            # Crear el DTO del cliente
            cliente_dto = ClienteDTO(
                nombre=comando.nombre,
                email=comando.email,
                identificacion=comando.identificacion,
                telefono=comando.telefono,
                direccion=comando.direccion,
                estado="ACTIVO"  # Estado por defecto para clientes nuevos
            )
            
            # Crear entidad de dominio
            cliente = Cliente(
                nombre=Nombre(comando.nombre),
                email=Email(comando.email),
                identificacion=Identificacion(comando.identificacion),
                telefono=Telefono(comando.telefono),
                direccion=Direccion(comando.direccion),
                estado=Estado("ACTIVO")  # Estado por defecto para clientes nuevos
            )
            
            # Disparar evento de creación
            cliente.disparar_evento_creacion()
            
            # Guardar en SQLite
            cliente_guardado = self.repositorio.crear(cliente_dto)
            
            return cliente_guardado
            
        except Exception as e:
            logger.error(f"Error creando cliente: {e}")
            raise

@ejecutar_comando.register
def _(comando: CrearCliente):
    handler = CrearClienteHandler()
    return handler.handle(comando)
