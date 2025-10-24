import seedwork.presentacion.api as api
import json
from datetime import datetime
from flask import request, Response, Blueprint
from aplicacion.comandos.crear_visita import CrearVisita
from aplicacion.comandos.registrar_visita import RegistrarVisita
from aplicacion.comandos.subir_evidencia import SubirEvidencia
from aplicacion.consultas.obtener_visitas import ObtenerVisitas
from aplicacion.consultas.obtener_visitas_por_vendedor import ObtenerVisitasPorVendedor
from aplicacion.consultas.obtener_evidencias_visita import ObtenerEvidenciasVisita
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.consultas import ejecutar_consulta
from aplicacion.mapeadores import MapeadorVisitaAgregacionDTOJson

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = api.crear_blueprint('visita', '/ventas/api/visitas')

@bp.route('/', methods=['POST'])
def crear_visita():
    try:
        visita_dict = request.json
        
        if not visita_dict:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}), 
                status=400, 
                mimetype='application/json'
            )
        
        # Convertir fecha_programada de string a datetime
        fecha_programada = None
        if 'fecha_programada' in visita_dict:
            try:
                # Parsear fecha ISO
                fecha_programada = datetime.fromisoformat(visita_dict['fecha_programada'].replace('Z', '+00:00'))
                # Remover zona horaria para que sea compatible con datetime.now()
                if fecha_programada.tzinfo is not None:
                    fecha_programada = fecha_programada.replace(tzinfo=None)
            except ValueError:
                return Response(
                    json.dumps({'error': 'Formato de fecha inválido. Use ISO format'}), 
                    status=400, 
                    mimetype='application/json'
                )
        
        comando = CrearVisita(
            vendedor_id=visita_dict.get('vendedor_id', ''),
            cliente_id=visita_dict.get('cliente_id', ''),
            fecha_programada=fecha_programada or datetime.now(),
            direccion=visita_dict.get('direccion', ''),
            telefono=visita_dict.get('telefono', ''),
            estado=visita_dict.get('estado', 'pendiente'),
            descripcion=visita_dict.get('descripcion', '')
        )
        
        resultado = ejecutar_comando(comando)
        
        mapeador = MapeadorVisitaAgregacionDTOJson()
        visita_json = mapeador.agregacion_a_externo(resultado)
        
        return Response(
            json.dumps(visita_json), 
            status=201, 
            mimetype='application/json'
        )
        
    except ValueError as e:
        return Response(
            json.dumps({'error': str(e)}), 
            status=400, 
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error creando visita: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

@bp.route('/', methods=['GET'])
def obtener_visitas():

    def parsear_fecha(valor):
        """Intenta parsear fecha con o sin hora."""
        try:
            return datetime.fromisoformat(valor)
        except ValueError:
            return datetime.strptime(valor, "%Y-%m-%d")
    
    try:
        estado = request.args.get('estado')
        vendedor_id = request.args.get('vendedor_id')
        fecha_inicio_str = request.args.get("fecha_inicio")
        fecha_fin_str = request.args.get("fecha_fin")

        fecha_inicio = parsear_fecha(fecha_inicio_str) if fecha_inicio_str else None
        fecha_fin = parsear_fecha(fecha_fin_str) if fecha_fin_str else None
        
        consulta = ObtenerVisitas(
            estado=estado,
            vendedor_id=vendedor_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        visitas_agregacion = ejecutar_consulta(consulta)
        
        mapeador = MapeadorVisitaAgregacionDTOJson()
        visitas_json = mapeador.agregaciones_a_externo(visitas_agregacion)
        
        return Response(
            json.dumps(visitas_json), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo visitas con agregación: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

@bp.route('/vendedor/<vendedor_id>', methods=['GET'])
def obtener_visitas_por_vendedor(vendedor_id):

    def parsear_fecha(valor):
        """Intenta parsear fecha con o sin hora."""
        try:
            return datetime.fromisoformat(valor)
        except ValueError:
            return datetime.strptime(valor, "%Y-%m-%d")
    
    try:
        estado = request.args.get('estado')
        fecha_inicio_str = request.args.get("fecha_inicio")
        fecha_fin_str = request.args.get("fecha_fin")

        fecha_inicio = parsear_fecha(fecha_inicio_str) if fecha_inicio_str else None
        fecha_fin = parsear_fecha(fecha_fin_str) if fecha_fin_str else None
        
        consulta = ObtenerVisitasPorVendedor(
            vendedor_id=vendedor_id, 
            estado=estado,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        visitas_agregacion = ejecutar_consulta(consulta)
        
        mapeador = MapeadorVisitaAgregacionDTOJson()
        visitas_json = mapeador.agregaciones_a_externo(visitas_agregacion)
        
        return Response(
            json.dumps(visitas_json), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo visitas por vendedor: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

@bp.route('/<visita_id>', methods=['PUT'])
def registrar_visita(visita_id):
    try:
        visita_dict = request.json
        
        if not visita_dict:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}), 
                status=400, 
                mimetype='application/json'
            )
        
        # Validar campos obligatorios
        campos_obligatorios = ['fecha_realizada', 'hora_realizada', 'cliente_id']
        for campo in campos_obligatorios:
            if campo not in visita_dict or not visita_dict[campo]:
                return Response(
                    json.dumps({'error': f'El campo {campo} es obligatorio'}), 
                    status=400, 
                    mimetype='application/json'
                )
        
        comando = RegistrarVisita(
            visita_id=visita_id,
            fecha_realizada=visita_dict.get('fecha_realizada'),
            hora_realizada=visita_dict.get('hora_realizada'),
            cliente_id=visita_dict.get('cliente_id'),
            novedades=visita_dict.get('novedades'),
            pedido_generado=visita_dict.get('pedido_generado', False)
        )
        
        resultado = ejecutar_comando(comando)
        
        return Response(
            json.dumps({
                'message': 'Visita registrada exitosamente',
                'visita_id': str(resultado.id),
                'estado': resultado.estado
            }), 
            status=200, 
            mimetype='application/json'
        )
        
    except ValueError as e:
        return Response(
            json.dumps({'error': str(e)}), 
            status=400, 
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error registrando visita: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

@bp.route('/<visita_id>/evidencias', methods=['POST'])
def subir_evidencia(visita_id):
    """
    Endpoint para subir evidencia visual (fotos/videos) de una visita
    Solo accesible para vendedores
    """
    try:
        # Validar archivo
        if 'archivo' not in request.files:
            return Response(
                json.dumps({'error': 'No se proporcionó ningún archivo'}),
                status=400,
                mimetype='application/json'
            )
        
        file = request.files['archivo']
        if file.filename == '':
            return Response(
                json.dumps({'error': 'Nombre de archivo vacío'}),
                status=400,
                mimetype='application/json'
            )
        
        # Obtener comentarios
        comentarios = request.form.get('comentarios', '')
        
        # Leer datos del archivo
        file_data = file.read()
        
        # Obtener vendedor_id del header (inyectado por Nginx desde el token JWT)
        vendedor_id = request.headers.get('X-User-Id', 'unknown-user')
        
        comando = SubirEvidencia(
            visita_id=visita_id,
            archivo_data=file_data,
            nombre_archivo=file.filename,
            content_type=file.content_type or 'application/octet-stream',
            comentarios=comentarios,
            vendedor_id=vendedor_id
        )
        
        evidencia_dto = ejecutar_comando(comando)
        
        respuesta = {
            'mensaje': 'Evidencia subida exitosamente',
            'evidencia': {
                'id': str(evidencia_dto.id),
                'visita_id': evidencia_dto.visita_id,
                'archivo_url': evidencia_dto.archivo_url,
                'nombre_archivo': evidencia_dto.nombre_archivo,
                'formato': evidencia_dto.formato,
                'tamaño_mb': round(evidencia_dto.tamaño_bytes / 1024 / 1024, 2),
                'comentarios': evidencia_dto.comentarios,
                'created_at': evidencia_dto.created_at.isoformat()
            }
        }
        
        return Response(
            json.dumps(respuesta),
            status=201,
            mimetype='application/json'
        )
    
    except ValueError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error subiendo evidencia: {e}")
        return Response(
            json.dumps({'error': f'Error interno: {str(e)}'}),
            status=500,
            mimetype='application/json'
        )

@bp.route('/<visita_id>/evidencias', methods=['GET'])
def obtener_evidencias(visita_id):
    """
    Endpoint para obtener todas las evidencias de una visita
    Accesible para vendedores y administradores
    """
    try:
        consulta = ObtenerEvidenciasVisita(visita_id=visita_id)
        evidencias = ejecutar_consulta(consulta)
        
        respuesta = {
            'visita_id': visita_id,
            'total': len(evidencias),
            'evidencias': [
                {
                    'id': str(e.id),
                    'archivo_url': e.archivo_url,
                    'nombre_archivo': e.nombre_archivo,
                    'formato': e.formato,
                    'tamaño_mb': round(e.tamaño_bytes / 1024 / 1024, 2),
                    'comentarios': e.comentarios,
                    'vendedor_id': e.vendedor_id,
                    'created_at': e.created_at.isoformat()
                }
                for e in evidencias
            ]
        }
        
        return Response(
            json.dumps(respuesta),
            status=200,
            mimetype='application/json'
        )
    
    except Exception as e:
        logger.error(f"Error obteniendo evidencias: {e}")
        return Response(
            json.dumps({'error': f'Error interno: {str(e)}'}),
            status=500,
            mimetype='application/json'
        )
