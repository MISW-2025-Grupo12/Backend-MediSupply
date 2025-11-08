"""Comando para generar sugerencias usando Vertex AI"""
from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando, ejecutar_comando
import logging
from typing import Optional
from aplicacion.dto import SugerenciaClienteDTO
from infraestructura.repositorios import RepositorioSugerenciaCliente, RepositorioEvidenciaVisita
from infraestructura.servicio_vertex_ai import ServicioVertexAI
from infraestructura.servicio_usuarios import ServicioUsuarios
from aplicacion.servicios.servicio_historial_cliente import ServicioHistorialCliente

logger = logging.getLogger(__name__)

@dataclass
class GenerarSugerencias(Comando):
    cliente_id: str
    evidencia_id: Optional[str] = None
    evidencia_url: Optional[str] = None

class GenerarSugerenciasHandler:
    def __init__(
        self,
        repositorio_sugerencia=None,
        repositorio_evidencia=None,
        servicio_vertex_ai=None,
        servicio_usuarios=None,
        servicio_historial=None
    ):
        self.repositorio_sugerencia = repositorio_sugerencia or RepositorioSugerenciaCliente()
        self.repositorio_evidencia = repositorio_evidencia or RepositorioEvidenciaVisita()
        self.servicio_vertex_ai = servicio_vertex_ai or ServicioVertexAI()
        self.servicio_usuarios = servicio_usuarios or ServicioUsuarios()
        self.servicio_historial = servicio_historial or ServicioHistorialCliente()
    
    def handle(self, comando: GenerarSugerencias) -> SugerenciaClienteDTO:
        """
        Genera sugerencias para un cliente usando Vertex AI
        
        Args:
            comando: Comando con cliente_id y opcionalmente evidencia_id o evidencia_url
        
        Returns:
            SugerenciaClienteDTO con las sugerencias generadas
        """
        try:
            # 1. Obtener datos del cliente
            logger.info(f"Obteniendo datos del cliente {comando.cliente_id}")
            datos_cliente = self.servicio_usuarios.obtener_cliente_por_id(comando.cliente_id)
            
            if not datos_cliente:
                raise ValueError(f"Cliente {comando.cliente_id} no encontrado")
            
            # 2. Obtener historial de pedidos
            logger.info(f"Obteniendo historial de pedidos del cliente {comando.cliente_id}")
            historial_pedidos = self.servicio_historial.obtener_historial_cliente(comando.cliente_id)
            
            # 3. Procesar evidencia si se proporciona
            archivo_url = None
            mime_type = None
            comentarios_evidencia = None
            evidencia_id_final = None
            
            if comando.evidencia_id:
                # Obtener evidencia por ID
                logger.info(f"Obteniendo evidencia {comando.evidencia_id}")
                evidencia = self.repositorio_evidencia.obtener_por_id(comando.evidencia_id)
                
                if not evidencia:
                    raise ValueError(f"Evidencia {comando.evidencia_id} no encontrada")
                
                evidencia_id_final = comando.evidencia_id
                archivo_url = evidencia.archivo_url
                formato = evidencia.formato
                comentarios_evidencia = evidencia.comentarios
                mime_type = self.servicio_vertex_ai.obtener_mime_type(formato)
                
                logger.info(
                    "Evidencia procesada (%s): mime=%s",
                    archivo_url,
                    mime_type,
                )
                
            elif comando.evidencia_url:
                # Usar URL proporcionada directamente
                logger.info(f"Usando URL de evidencia proporcionada: {comando.evidencia_url}")
                archivo_url = comando.evidencia_url
                
                # Intentar determinar MIME type desde la URL
                if '.' in comando.evidencia_url:
                    extension = comando.evidencia_url.rsplit('.', 1)[-1].split('?')[0]  # Remover query params
                    mime_type = self.servicio_vertex_ai.obtener_mime_type(extension)
                else:
                    mime_type = 'application/octet-stream'
                
                logger.info(
                    "Evidencia URL procesada (%s): mime=%s",
                    archivo_url,
                    mime_type,
                )
            
            # 4. Generar sugerencias con Vertex AI
            logger.info(f"Generando sugerencias para cliente {comando.cliente_id}")
            sugerencias_texto = self.servicio_vertex_ai.generar_sugerencias(
                datos_cliente=datos_cliente,
                historial_pedidos=historial_pedidos,
                archivo_url=archivo_url,
                mime_type=mime_type,
                comentarios_evidencia=comentarios_evidencia
            )
            
            # 5. Crear DTO de sugerencia
            sugerencia_dto = SugerenciaClienteDTO(
                cliente_id=comando.cliente_id,
                evidencia_id=evidencia_id_final,
                sugerencias_texto=sugerencias_texto,
                modelo_usado=self.servicio_vertex_ai.base_model
            )
            
            # 6. Guardar sugerencia en BD
            logger.info(f"Guardando sugerencia para cliente {comando.cliente_id}")
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

