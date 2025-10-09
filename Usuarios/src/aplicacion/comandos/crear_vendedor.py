from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando, ejecutar_comando
import uuid
import logging
from aplicacion.dto import VendedorDTO
from dominio.entidades import Vendedor
from dominio.objetos_valor import Nombre, Email, Telefono, Direccion
from infraestructura.repositorios import RepositorioVendedorSQLite

logger = logging.getLogger(__name__)

@dataclass
class CrearVendedor(Comando):
    nombre: str
    email: str
    telefono: str
    direccion: str

class CrearVendedorHandler:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or RepositorioVendedorSQLite()
    
    def handle(self, comando: CrearVendedor) -> VendedorDTO:
        try:
            # Crear el DTO del vendedor
            vendedor_dto = VendedorDTO(
                nombre=comando.nombre,
                email=comando.email,
                telefono=comando.telefono,
                direccion=comando.direccion
            )
            
            # Crear entidad de dominio
            vendedor = Vendedor(
                nombre=Nombre(comando.nombre),
                email=Email(comando.email),
                telefono=Telefono(comando.telefono),
                direccion=Direccion(comando.direccion)
            )
            
            # Disparar evento de creación
            vendedor.disparar_evento_creacion()
            
            # Guardar en SQLite
            vendedor_guardado = self.repositorio.crear(vendedor_dto)
            
            return vendedor_guardado
            
        except Exception as e:
            logger.error(f"Error creando vendedor: {e}")
            raise

@ejecutar_comando.register
def _(comando: CrearVendedor):
    handler = CrearVendedorHandler()
    return handler.handle(comando)
