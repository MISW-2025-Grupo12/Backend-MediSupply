"""API endpoints para sugerencias de clientes"""
from flask import Blueprint, request, Response
import json
import logging
from aplicacion.comandos.generar_sugerencias import GenerarSugerencias, ejecutar_comando
from infraestructura.repositorios import RepositorioSugerenciaCliente

logger = logging.getLogger(__name__)

# Blueprint para sugerencias basadas en visitas
bp_visitas = Blueprint('sugerencias_visitas', __name__, url_prefix='/ventas/api/visitas')

# Blueprint para obtener sugerencias por cliente
bp_clientes = Blueprint('sugerencias_clientes', __name__, url_prefix='/ventas/api/clientes')

@bp_visitas.route('/<visita_id>/sugerencias', methods=['POST'])
def generar_sugerencias(visita_id):
    """
    Generar sugerencias para un cliente usando servicios de IA basado en una visita
    
    El endpoint obtiene automáticamente:
    - El cliente_id desde la visita
    - Las evidencias asociadas a la visita (si existen)
    - El historial de compras del cliente
    """
    try:
        # Crear comando con visita_id
        comando = GenerarSugerencias(visita_id=visita_id)
        
        # Ejecutar comando
        sugerencia_dto = ejecutar_comando(comando)
        
        # Retornar respuesta
        respuesta = {
            'mensaje': 'Sugerencias generadas exitosamente',
            'visita_id': visita_id,
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

@bp_clientes.route('/<cliente_id>/sugerencias', methods=['GET'])
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

