from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando, ejecutar_comando
import logging
from aplicacion.dto import ProveedorDTO
from dominio.fabricas import FabricaProveedor
from dominio.entidades import Proveedor
from dominio.objetos_valor import Nombre, Email, Direccion
from infraestructura.repositorios import RepositorioProveedorSQLite

logger = logging.getLogger(__name__)

@dataclass
class CrearProveedor(Comando):
    nombre: str
    email: str
    direccion: str

class CrearProveedorHandler:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or RepositorioProveedorSQLite()
    
    def handle(self, comando: CrearProveedor) -> ProveedorDTO:
        try:
            proveedor_dto = ProveedorDTO(
                nombre=comando.nombre,
                email=comando.email,
                direccion=comando.direccion
            )
            
            proveedor_temp = Proveedor(
                nombre=Nombre(comando.nombre),
                email=Email(comando.email),
                direccion=Direccion(comando.direccion)
            )
            
            fabrica = FabricaProveedor()
            fabrica.crear_objeto(proveedor_temp)
            
            proveedor_temp.disparar_evento_creacion()
            proveedor_guardado = self.repositorio.crear(proveedor_dto)
            
            return proveedor_guardado
        except Exception as e:
            logger.error(f"Error creando proveedor: {e}")
            raise

@ejecutar_comando.register
def _(comando: CrearProveedor):
    handler = CrearProveedorHandler()
    return handler.handle(comando)
