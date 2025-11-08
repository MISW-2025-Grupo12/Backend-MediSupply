"""API endpoints para sugerencias de clientes"""
from flask import Blueprint, request, Response
import json
import logging
from aplicacion.comandos.generar_sugerencias import GenerarSugerencias, ejecutar_comando
from infraestructura.repositorios import RepositorioSugerenciaCliente

logger = logging.getLogger(__name__)

bp = Blueprint('sugerencias', __name__, url_prefix='/ventas/api/clientes')

@bp.route('/<cliente_id>/sugerencias', methods=['POST'])
def generar_sugerencias(cliente_id):
    """
    Generar sugerencias para un cliente usando Vertex AI
    
    Body opcional:
    {
        "evidencia_id": "uuid-opcional",  // ID de evidencia existente
        "evidencia_url": "url-opcional"    // URL directa de evidencia
    }
    """
    try:
        # Obtener datos del body (opcional)
        body = request.get_json() or {}
        evidencia_id = body.get('evidencia_id')
        evidencia_url = body.get('evidencia_url')
        
        # Validar que no se proporcionen ambos
        if evidencia_id and evidencia_url:
            return Response(
                json.dumps({'error': 'No se puede proporcionar evidencia_id y evidencia_url al mismo tiempo'}),
                status=400,
                mimetype='application/json'
            )
        
        # Crear comando
        comando = GenerarSugerencias(
            cliente_id=cliente_id,
            evidencia_id=evidencia_id,
            evidencia_url=evidencia_url
        )
        
        # Ejecutar comando
        sugerencia_dto = ejecutar_comando(comando)
        
        # Retornar respuesta
        respuesta = {
            'mensaje': 'Sugerencias generadas exitosamente',
            'sugerencia': {
                'id': str(sugerencia_dto.id),
                'cliente_id': sugerencia_dto.cliente_id,
                'evidencia_id': sugerencia_dto.evidencia_id,
                'sugerencias_texto': sugerencia_dto.sugerencias_texto,
                'modelo_usado': sugerencia_dto.modelo_usado,
                'created_at': sugerencia_dto.created_at.isoformat()
            }
        }
        
        return Response(
            json.dumps(respuesta),
            status=201,
            mimetype='application/json'
        )
        
    except ValueError as e:
        logger.warning(f"Error de validación: {str(e)}")
        return Response(
            json.dumps({'error': str(e)}),
            status=404,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error generando sugerencias: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}),
            status=500,
            mimetype='application/json'
        )

@bp.route('/<cliente_id>/sugerencias', methods=['GET'])
def obtener_sugerencias(cliente_id):
    """Obtener todas las sugerencias de un cliente"""
    try:
        repositorio = RepositorioSugerenciaCliente()
        sugerencias = repositorio.obtener_por_cliente_id(cliente_id)
        
        sugerencias_data = []
        for sugerencia in sugerencias:
            sugerencias_data.append({
                'id': str(sugerencia.id),
                'cliente_id': sugerencia.cliente_id,
                'evidencia_id': sugerencia.evidencia_id,
                'sugerencias_texto': sugerencia.sugerencias_texto,
                'modelo_usado': sugerencia.modelo_usado,
                'created_at': sugerencia.created_at.isoformat()
            })
        
        return Response(
            json.dumps({
                'cliente_id': cliente_id,
                'total': len(sugerencias_data),
                'sugerencias': sugerencias_data
            }),
            status=200,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo sugerencias: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}),
            status=500,
            mimetype='application/json'
        )

