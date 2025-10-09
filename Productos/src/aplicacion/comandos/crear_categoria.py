from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando, ejecutar_comando
import uuid
import logging
from aplicacion.dto import CategoriaDTO
from infraestructura.repositorios import RepositorioCategoriaSQLite

logger = logging.getLogger(__name__)

@dataclass
class CrearCategoria(Comando):
    nombre: str
    descripcion: str

class CrearCategoriaHandler:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or RepositorioCategoriaSQLite()
    
    def handle(self, comando: CrearCategoria) -> CategoriaDTO:
        try:
            # 1. Crear el DTO de la categoría
            categoria_dto = CategoriaDTO(
                nombre=comando.nombre,
                descripcion=comando.descripcion
            )
            
            # 2. Guardar en SQLite
            categoria_guardada = self.repositorio.crear(categoria_dto)
            
            # 3. Retornar el DTO de la categoría creada
            return categoria_guardada
            
        except Exception as e:
            logger.error(f"Error creando categoría: {e}")
            raise

@ejecutar_comando.register
def _(comando: CrearCategoria):
    handler = CrearCategoriaHandler()
    return handler.handle(comando)
