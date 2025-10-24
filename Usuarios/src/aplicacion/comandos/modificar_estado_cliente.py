from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando, ejecutar_comando
import uuid
import logging
from aplicacion.dto import ClienteDTO
from dominio.objetos_valor import Estado
from infraestructura.repositorios import RepositorioClienteSQLite
from infraestructura.modelos import ClienteModel
from config.db import db

logger = logging.getLogger(__name__)

@dataclass
class ModificarEstadoCliente(Comando):
    cliente_id: str
    nuevo_estado: str

class ModificarEstadoClienteHandler:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or RepositorioClienteSQLite()
    
    def handle(self, comando: ModificarEstadoCliente) -> ClienteDTO:
        try:
            # Validar el nuevo estado usando el objeto valor
            estado_obj = Estado(comando.nuevo_estado)
            
            # Obtener el cliente existente
            cliente_existente = self.repositorio.obtener_por_id(comando.cliente_id)
            if not cliente_existente:
                raise ValueError(f"Cliente con ID {comando.cliente_id} no encontrado")
            
            # Actualizar el estado en la base de datos
            cliente_model = ClienteModel.query.get(comando.cliente_id)
            if not cliente_model:
                raise ValueError(f"Cliente con ID {comando.cliente_id} no encontrado en la base de datos")
            
            # Actualizar el estado
            cliente_model.estado = comando.nuevo_estado
            db.session.commit()
            
            # Crear el DTO actualizado
            cliente_actualizado = ClienteDTO(
                id=cliente_existente.id,
                nombre=cliente_existente.nombre,
                email=cliente_existente.email,
                identificacion=cliente_existente.identificacion,
                telefono=cliente_existente.telefono,
                direccion=cliente_existente.direccion,
                estado=comando.nuevo_estado
            )
            
            logger.info(f"Estado del cliente {comando.cliente_id} actualizado a {comando.nuevo_estado}")
            
            return cliente_actualizado
            
        except Exception as e:
            logger.error(f"Error modificando estado del cliente: {e}")
            raise

@ejecutar_comando.register
def _(comando: ModificarEstadoCliente):
    handler = ModificarEstadoClienteHandler()
    return handler.handle(comando)
