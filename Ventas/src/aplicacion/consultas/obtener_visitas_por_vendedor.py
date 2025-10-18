from dataclasses import dataclass
from datetime import datetime
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
import logging
from aplicacion.dto import VisitaDTO
from aplicacion.dto_agregacion import VisitaAgregacionDTO
from infraestructura.repositorios import RepositorioVisitaSQLite
from infraestructura.servicio_usuarios import ServicioUsuarios

logger = logging.getLogger(__name__)

@dataclass
class ObtenerVisitasPorVendedor(Consulta):
    """Consulta para obtener visitas por vendedor con agregación completa"""
    vendedor_id: str
    estado: str = None  # Filtro opcional por estado
    fecha_inicio: datetime = None  # Filtro opcional por fecha inicio
    fecha_fin: datetime = None  # Filtro opcional por fecha fin

class ObtenerVisitasPorVendedorHandler:
    def __init__(self, repositorio=None, servicio_usuarios=None):
        self.repositorio = repositorio or RepositorioVisitaSQLite()
        self.servicio_usuarios = servicio_usuarios or ServicioUsuarios()
    
    def handle(self, consulta: ObtenerVisitasPorVendedor) -> list[VisitaAgregacionDTO]:
        try:
            # 1. Obtener todas las visitas del repositorio
            visitas = self.repositorio.obtener_todos()
            
            # 2. Filtrar por vendedor_id
            visitas_vendedor = [v for v in visitas if v.vendedor_id == consulta.vendedor_id]
            
            # 3. Aplicar filtro por estado si se especifica
            if consulta.estado:
                visitas_vendedor = [v for v in visitas_vendedor if v.estado == consulta.estado]
            
            # 4. Aplicar filtro por rango de fechas si se especifica
            if consulta.fecha_inicio and consulta.fecha_fin:
                # Si ambas fechas son iguales → filtrar solo ese día
                if consulta.fecha_inicio.date() == consulta.fecha_fin.date():
                    visitas_vendedor = [v for v in visitas_vendedor if v.fecha_programada.date() == consulta.fecha_inicio.date()]
                else:
                    # Si son diferentes → rango normal
                    visitas_vendedor = [v for v in visitas_vendedor if consulta.fecha_inicio.date() <= v.fecha_programada.date() <= consulta.fecha_fin.date()]
            
            # 5. Construir agregaciones completas
            agregaciones = []
            for visita in visitas_vendedor:
                try:
                    # Obtener vendedor
                    vendedor = self.servicio_usuarios.obtener_vendedor_por_id(visita.vendedor_id)
                    if not vendedor:
                        logger.warning(f"Vendedor {visita.vendedor_id} no encontrado para visita {visita.id}")
                        continue
                    
                    # Obtener cliente
                    cliente = self.servicio_usuarios.obtener_cliente_por_id(visita.cliente_id)
                    if not cliente:
                        logger.warning(f"Cliente {visita.cliente_id} no encontrado para visita {visita.id}")
                        continue
                    
                    # Construir agregación completa
                    agregacion = VisitaAgregacionDTO(
                        id=visita.id,
                        fecha_programada=visita.fecha_programada,
                        direccion=visita.direccion,
                        telefono=visita.telefono,
                        estado=visita.estado,
                        descripcion=visita.descripcion,
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
                    
                    agregaciones.append(agregacion)
                    
                except Exception as e:
                    logger.warning(f"Error construyendo agregación para visita {visita.id}: {e}")
                    continue
            
            return agregaciones
            
        except Exception as e:
            logger.error(f"Error obteniendo visitas por vendedor: {e}")
            raise

@ejecutar_consulta.register
def _(consulta: ObtenerVisitasPorVendedor):
    handler = ObtenerVisitasPorVendedorHandler()
    return handler.handle(consulta)
