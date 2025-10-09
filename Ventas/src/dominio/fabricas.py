from seedwork.dominio.fabricas import Fabrica
from seedwork.dominio.reglas import ReglaNegocio

class FabricaVisita(Fabrica):
    def crear_objeto(self, tipo, **kwargs):
        pass
    
    def validar_regla(self, regla: ReglaNegocio):
        if not regla.es_valido():
            raise ValueError(regla.__class__.__name__)
