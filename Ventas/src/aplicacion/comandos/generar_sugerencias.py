"""Comando para generar sugerencias usando Vertex AI"""
from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando, ejecutar_comando
import logging
from typing import Optional
from aplicacion.dto import SugerenciaClienteDTO
from infraestructura.repositorios import RepositorioSugerenciaCliente, RepositorioEvidenciaVisita, RepositorioVisita
from infraestructura.servicio_vertex_ai import ServicioVertexAI
from infraestructura.servicio_usuarios import ServicioUsuarios
from aplicacion.servicios.servicio_historial_cliente import ServicioHistorialCliente

logger = logging.getLogger(__name__)

@dataclass
class GenerarSugerencias(Comando):
    visita_id: str

class GenerarSugerenciasHandler:
    def __init__(
        self,
        repositorio_sugerencia=None,
        repositorio_evidencia=None,
        repositorio_visita=None,
        servicio_vertex_ai=None,
        servicio_usuarios=None,
        servicio_historial=None
    ):
        self.repositorio_sugerencia = repositorio_sugerencia or RepositorioSugerenciaCliente()
        self.repositorio_evidencia = repositorio_evidencia or RepositorioEvidenciaVisita()
        self.repositorio_visita = repositorio_visita or RepositorioVisita()
        self.servicio_vertex_ai = servicio_vertex_ai or ServicioVertexAI()
        self.servicio_usuarios = servicio_usuarios or ServicioUsuarios()
        self.servicio_historial = servicio_historial or ServicioHistorialCliente()
    
    def handle(self, comando: GenerarSugerencias) -> SugerenciaClienteDTO:
        """
        Genera sugerencias para un cliente usando Vertex AI basado en una visita
        
        Args:
            comando: Comando con visita_id
        
        Returns:
            SugerenciaClienteDTO con las sugerencias generadas
        """
        try:
            # 1. Obtener la visita por ID
            logger.info(f"Obteniendo visita {comando.visita_id}")
            visita = self.repositorio_visita.obtener_por_id(comando.visita_id)
            
            if not visita:
                raise ValueError(f"Visita {comando.visita_id} no encontrada")
            
            cliente_id = visita.cliente_id
            logger.info(f"Visita encontrada para cliente {cliente_id}")
            
            # 2. Obtener datos del cliente
            logger.info(f"Obteniendo datos del cliente {cliente_id}")
            datos_cliente = self.servicio_usuarios.obtener_cliente_por_id(cliente_id)
            
            if not datos_cliente:
                raise ValueError(f"Cliente {cliente_id} no encontrado")
            
            # 3. Obtener historial de pedidos
            logger.info(f"Obteniendo historial de pedidos del cliente {cliente_id}")
            historial_pedidos = self.servicio_historial.obtener_historial_cliente(cliente_id)
            
            # 4. Obtener evidencias de la visita
            logger.info(f"Obteniendo evidencias de la visita {comando.visita_id}")
            evidencias = self.repositorio_evidencia.obtener_por_visita(comando.visita_id)
            
            # 5. Procesar evidencias
            archivo_url = None
            mime_type = None
            comentarios_evidencia = None
            evidencia_id_final = None
            
            if evidencias:
                # Usar la primera evidencia (la más reciente si están ordenadas por created_at)
                # Ordenar por created_at descendente para usar la más reciente
                evidencias_ordenadas = sorted(evidencias, key=lambda e: e.created_at, reverse=True)
                evidencia_principal = evidencias_ordenadas[0]
                
                evidencia_id_final = str(evidencia_principal.id)
                archivo_url = evidencia_principal.archivo_url
                formato = evidencia_principal.formato
                mime_type = self.servicio_vertex_ai.obtener_mime_type(formato)
                
                # Combinar comentarios de todas las evidencias
                comentarios_parts = []
                for evidencia in evidencias_ordenadas:
                    if evidencia.comentarios:
                        comentarios_parts.append(evidencia.comentarios)
                
                if comentarios_parts:
                    comentarios_evidencia = "\n".join(comentarios_parts)
                
                logger.info(
                    f"Procesadas {len(evidencias)} evidencias. Usando evidencia principal: {archivo_url} (mime={mime_type})"
                )
            else:
                logger.info("No se encontraron evidencias para esta visita")
            
            # 6. Generar sugerencias con Vertex AI
            logger.info(f"Generando sugerencias para cliente {cliente_id} basado en visita {comando.visita_id}")
            sugerencias_texto = self.servicio_vertex_ai.generar_sugerencias(
                datos_cliente=datos_cliente,
                historial_pedidos=historial_pedidos,
                archivo_url=archivo_url,
                mime_type=mime_type,
                comentarios_evidencia=comentarios_evidencia
            )
            
            # 7. Crear DTO de sugerencia
            sugerencia_dto = SugerenciaClienteDTO(
                cliente_id=cliente_id,
                evidencia_id=evidencia_id_final,
                sugerencias_texto=sugerencias_texto,
                modelo_usado=self.servicio_vertex_ai.base_model
            )
            
            # 8. Guardar sugerencia en BD
            logger.info(f"Guardando sugerencia para cliente {cliente_id}")
            sugerencia_guardada = self.repositorio_sugerencia.crear(sugerencia_dto)
            
            logger.info(f"Sugerencia generada exitosamente: {sugerencia_guardada.id}")
            return sugerencia_guardada
            
        except ValueError as e:
            logger.warning(f"Error de validación: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error generando sugerencias: {e}")
            raise

@ejecutar_comando.register
def _(comando: GenerarSugerencias):
    handler = GenerarSugerenciasHandler()
    return handler.handle(comando)

