from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando, ejecutar_comando
from aplicacion.dto import BodegaDTO
from infraestructura.repositorios import RepositorioBodegaSQLite

@dataclass
class InicializarBodegas(Comando):
    pass

class InicializarBodegasHandler:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or RepositorioBodegaSQLite()
    
    def handle(self, comando: InicializarBodegas):
        # Verificar si ya existen bodegas
        bodegas_existentes = self.repositorio.obtener_todas()
        if bodegas_existentes:
            return {'message': 'Bodegas ya inicializadas', 'count': len(bodegas_existentes)}
        
        # Crear 3 bodegas por defecto
        bodegas = [
            BodegaDTO(nombre="Bodega Central", direccion="Carrera 68 #25-45, Fontibón, Bogotá D.C."),
            BodegaDTO(nombre="Bodega Norte", direccion="Autopista Norte #245-67, Suba, Bogotá D.C."),
            BodegaDTO(nombre="Bodega Sur", direccion="Cl 97 Sur #6-2, Bogotá D.C.")
        ]
        
        for bodega_dto in bodegas:
            self.repositorio.crear(bodega_dto)
        
        return {'message': 'Bodegas inicializadas exitosamente', 'count': 3}

@ejecutar_comando.register
def _(comando: InicializarBodegas):
    handler = InicializarBodegasHandler()
    return handler.handle(comando)
