import seedwork.presentacion.api as api
import json
import uuid
from datetime import datetime
from flask import request, Response, Blueprint
from aplicacion.comandos.crear_producto import CrearProducto
from aplicacion.comandos.crear_producto_con_inventario import CrearProductoConInventario
from aplicacion.consultas.obtener_productos import ObtenerProductos
from aplicacion.consultas.obtener_producto_por_id import ObtenerProductoPorId
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.consultas import ejecutar_consulta
from aplicacion.mapeadores import MapeadorProductoDTOJson, MapeadorProductoAgregacionDTOJson
from seedwork.presentacion.paginacion import paginar_resultados, extraer_parametros_paginacion
from aplicacion.dto import CargaMasivaJobDTO
from aplicacion.servicios.servicio_carga_masiva import ServicioCargaMasiva
from infraestructura.servicio_gcp_storage import get_storage_service
from infraestructura.repositorios import RepositorioJobSQLite

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = api.crear_blueprint('producto', '/productos/api/productos')

# Endpoint para crear producto
@bp.route('/', methods=['POST'])
def crear_producto():
    try:
        # Obtener datos del request
        producto_dict = request.json
        
        # Validación básica de HTTP - solo verificar que el JSON existe
        if not producto_dict:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}), 
                status=400, 
                mimetype='application/json'
            )
        
        # Crear comando - las validaciones se harán en el dominio
        comando = CrearProducto(
            nombre=producto_dict.get('nombre', ''),
            descripcion=producto_dict.get('descripcion', ''),
            precio=float(producto_dict.get('precio', 0)),
            categoria=producto_dict.get('categoria', ''),
            categoria_id=producto_dict.get('categoria_id', ''),
            proveedor_id=producto_dict.get('proveedor_id', '')
        )
        
        # Ejecutar comando - las reglas de negocio se validan aquí
        resultado = ejecutar_comando(comando)
        
        # Convertir agregación a JSON
        mapeador = MapeadorProductoAgregacionDTOJson()
        producto_json = mapeador.agregacion_a_externo(resultado)
        
        return Response(
            json.dumps(producto_json), 
            status=201, 
            mimetype='application/json'
        )
        
    except ValueError as e:
        # Las reglas de negocio lanzan ValueError
        return Response(
            json.dumps({'error': str(e)}), 
            status=400, 
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error creando producto: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

# Endpoint para crear producto con inventario
@bp.route('/con-inventario', methods=['POST'])
def crear_producto_con_inventario():
    try:
        # Obtener datos del request
        producto_dict = request.json
        
        # Validación básica de HTTP
        if not producto_dict:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}), 
                status=400, 
                mimetype='application/json'
            )
        
        # Crear comando con inventario
        comando = CrearProductoConInventario(
            nombre=producto_dict.get('nombre', ''),
            descripcion=producto_dict.get('descripcion', ''),
            precio=float(producto_dict.get('precio', 0)),
            stock=int(producto_dict.get('stock', 0)),
            fecha_vencimiento=producto_dict.get('fecha_vencimiento', ''),
            categoria=producto_dict.get('categoria', ''),
            categoria_id=producto_dict.get('categoria_id', ''),
            proveedor_id=producto_dict.get('proveedor_id', '')
        )
        
        # Ejecutar comando
        resultado = ejecutar_comando(comando)
        
        # Convertir agregación a JSON
        mapeador = MapeadorProductoAgregacionDTOJson()
        producto_json = mapeador.agregacion_a_externo(resultado)
        
        return Response(
            json.dumps(producto_json), 
            status=201, 
            mimetype='application/json'
        )
        
    except ValueError as e:
        # Las reglas de negocio lanzan ValueError
        return Response(
            json.dumps({'error': str(e)}), 
            status=400, 
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error creando producto con inventario: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

# Endpoint para obtener todos los productos con agregación completa
@bp.route('/', methods=['GET'])
def obtener_productos():
    try:
        # Obtener parámetros de paginación
        page, page_size = extraer_parametros_paginacion(request.args)
        
        # Crear consulta
        consulta = ObtenerProductos()
        
        # Ejecutar consulta (retorna agregaciones completas)
        productos_agregacion = ejecutar_consulta(consulta)
        
        # Convertir agregaciones a JSON
        mapeador = MapeadorProductoAgregacionDTOJson()
        productos_json = mapeador.agregaciones_a_externo(productos_agregacion)
        
        # Aplicar paginación
        max_page_size = 10000 if page_size > 100 else 100
        resultado_paginado = paginar_resultados(productos_json, page=page, page_size=page_size, max_page_size=max_page_size)
        
        return Response(
            json.dumps(resultado_paginado), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo productos con agregación: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

# Endpoint para obtener un producto por ID
@bp.route('/<producto_id>', methods=['GET'])
def obtener_producto_por_id(producto_id):
    try:
        # Crear consulta
        consulta = ObtenerProductoPorId(producto_id=producto_id)
        
        # Ejecutar consulta
        producto = ejecutar_consulta(consulta)
        
        if not producto:
            return Response(
                json.dumps({'error': 'Producto no encontrado'}), 
                status=404, 
                mimetype='application/json'
            )
        
        return Response(
            json.dumps(producto), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo producto por ID: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

# Endpoint para cargar productos masivamente desde CSV
@bp.route('/carga-masiva', methods=['POST'])
def crear_carga_masiva():
    try:
        # Validar que se haya enviado un archivo
        if 'file' not in request.files:
            return Response(
                json.dumps({'error': 'No se envió ningún archivo'}), 
                status=400, 
                mimetype='application/json'
            )
        
        file = request.files['file']
        
        if file.filename == '':
            return Response(
                json.dumps({'error': 'No se seleccionó ningún archivo'}), 
                status=400, 
                mimetype='application/json'
            )
        
        # Leer contenido del archivo
        csv_content = file.read()
        
        # Validar archivo CSV
        servicio_carga = ServicioCargaMasiva()
        es_valido, mensaje = servicio_carga.validar_archivo_csv(file.filename, csv_content)
        
        if not es_valido:
            return Response(
                json.dumps({'error': mensaje}), 
                status=400, 
                mimetype='application/json'
            )
        
        # Contar filas
        total_filas = servicio_carga.contar_filas(csv_content)
        
        if total_filas == 0:
            return Response(
                json.dumps({'error': 'El archivo CSV no tiene filas de datos'}), 
                status=400, 
                mimetype='application/json'
            )
        
        # Generar job_id
        job_id = str(uuid.uuid4())
        
        # Guardar CSV original en GCP Storage
        servicio_storage = get_storage_service()
        servicio_storage.guardar_csv_original(csv_content, job_id)
        
        # Crear job en BD
        repositorio_job = RepositorioJobSQLite()
        job_dto = CargaMasivaJobDTO(
            id=uuid.UUID(job_id),
            status='pending',
            total_filas=total_filas
        )
        repositorio_job.crear(job_dto)
        
        logger.info(f"Job de carga masiva creado: {job_id} con {total_filas} filas")
        
        return Response(
            json.dumps({
                'job_id': job_id,
                'status': 'pending',
                'total_filas': total_filas
            }), 
            status=202, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error creando carga masiva: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

# Endpoint para listar todos los jobs de carga masiva
@bp.route('/carga-masiva', methods=['GET'])
def listar_cargas_masivas():
    """Lista todos los jobs de carga masiva, opcionalmente filtrados por status"""
    try:
        # Obtener parámetros de paginación
        page, page_size = extraer_parametros_paginacion(request.args)
        
        # Obtener parámetros opcionales de filtrado
        status = request.args.get('status', None)  # pending, processing, completed, failed
        ordenar_por = request.args.get('ordenar_por', 'created_at')  # created_at, updated_at, status
        orden = request.args.get('orden', 'desc')  # asc, desc
        
        # Validar status
        if status and status not in ['pending', 'processing', 'completed', 'failed']:
            return Response(
                json.dumps({'error': f'Status inválido: {status}. Valores válidos: pending, processing, completed, failed'}), 
                status=400, 
                mimetype='application/json'
            )
        
        # Obtener jobs del repositorio
        repositorio_job = RepositorioJobSQLite()
        jobs = repositorio_job.obtener_todos(status=status, ordenar_por=ordenar_por, orden=orden)
        
        # Convertir a formato JSON
        jobs_json = []
        for job in jobs:
            porcentaje = (job.filas_procesadas / job.total_filas * 100) if job.total_filas > 0 else 0.0
            
            job_json = {
                'job_id': str(job.id),
                'status': job.status,
                'progreso': {
                    'total_filas': job.total_filas,
                    'filas_procesadas': job.filas_procesadas,
                    'filas_exitosas': job.filas_exitosas,
                    'filas_error': job.filas_error,
                    'filas_rechazadas': job.filas_rechazadas,
                    'porcentaje': round(porcentaje, 2)
                },
                'created_at': job.created_at.isoformat() if job.created_at else None,
                'updated_at': job.updated_at.isoformat() if job.updated_at else None
            }
            
            # Agregar result_url si está completado
            if job.status == 'completed' and job.result_url:
                job_json['result_url'] = job.result_url
            
            # Agregar error si falló
            if job.status == 'failed' and job.error:
                job_json['error'] = job.error
            
            jobs_json.append(job_json)
        
        # Aplicar paginación
        resultado_paginado = paginar_resultados(jobs_json, page=page, page_size=page_size)
        
        return Response(
            json.dumps(resultado_paginado), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error listando cargas masivas: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

# Endpoint para consultar el estado de un job de carga masiva
@bp.route('/carga-masiva/<job_id>', methods=['GET'])
def obtener_estado_carga_masiva(job_id):
    try:
        repositorio_job = RepositorioJobSQLite()
        job = repositorio_job.obtener_por_id(job_id)
        
        if not job:
            return Response(
                json.dumps({'error': 'Job no encontrado'}), 
                status=404, 
                mimetype='application/json'
            )
        
        # Calcular porcentaje
        porcentaje = (job.filas_procesadas / job.total_filas * 100) if job.total_filas > 0 else 0.0
        
        # Construir respuesta
        respuesta = {
            'job_id': str(job.id),
            'status': job.status,
            'progreso': {
                'total_filas': job.total_filas,
                'filas_procesadas': job.filas_procesadas,
                'filas_exitosas': job.filas_exitosas,
                'filas_error': job.filas_error,
                'filas_rechazadas': job.filas_rechazadas,
                'porcentaje': round(porcentaje, 2)
            },
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'updated_at': job.updated_at.isoformat() if job.updated_at else None
        }
        
        # Agregar result_url si está completado
        if job.status == 'completed' and job.result_url:
            respuesta['result_url'] = job.result_url
        
        # Agregar error si falló
        if job.status == 'failed' and job.error:
            respuesta['error'] = job.error
        
        return Response(
            json.dumps(respuesta), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo estado de carga masiva: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

