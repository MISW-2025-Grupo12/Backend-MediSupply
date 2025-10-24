"""
Endpoints de autenticación (registro y login)
"""
import seedwork.presentacion.api as api
import json
from flask import request, Response, Blueprint
from aplicacion.comandos.registrar_proveedor import RegistrarProveedor
from aplicacion.comandos.registrar_vendedor import RegistrarVendedor
from aplicacion.comandos.registrar_cliente import RegistrarCliente
from aplicacion.comandos.registrar_administrador import RegistrarAdministrador
from aplicacion.comandos.registrar_repartidor import RegistrarRepartidor
from aplicacion.comandos.login import Login
from seedwork.aplicacion.comandos import ejecutar_comando
from dominio.excepciones import (
    EmailYaRegistradoError,
    IdentificacionYaRegistradaError,
    CredencialesInvalidasError,
    UsuarioInactivoError,
    NombreInvalidoError,
    EmailInvalidoError,
    TelefonoInvalidoError,
    IdentificacionInvalidaError,
    PasswordInvalidaError
)

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = api.crear_blueprint('auth', '/usuarios/api/auth')


@bp.route('/registro-vendedor', methods=['POST'])
def registro_vendedor():
    """
    Endpoint para registrar un vendedor con autenticación
    
    Request Body:
        {
            "nombre": "string",
            "email": "string",
            "identificacion": "string",
            "telefono": "string",
            "direccion": "string",
            "password": "string"
        }
    
    Responses:
        201: Vendedor registrado exitosamente
        400: Errores de validación
        409: Email o identificación ya registrados
        500: Error interno del servidor
    """
    try:
        # Obtener datos del request
        datos = request.json
        
        # Validación básica de HTTP
        if not datos:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}),
                status=400,
                mimetype='application/json'
            )
        
        # Validar que todos los campos requeridos estén presentes
        campos_requeridos = ['nombre', 'email', 'identificacion', 'telefono', 'direccion', 'password']
        campos_faltantes = [campo for campo in campos_requeridos if campo not in datos or not datos[campo]]
        
        if campos_faltantes:
            return Response(
                json.dumps({
                    'error': 'Campos requeridos faltantes',
                    'campos': campos_faltantes
                }),
                status=400,
                mimetype='application/json'
            )
        
        # Crear comando
        comando = RegistrarVendedor(
            nombre=datos.get('nombre', ''),
            email=datos.get('email', ''),
            identificacion=datos.get('identificacion', ''),
            telefono=datos.get('telefono', ''),
            direccion=datos.get('direccion', ''),
            password=datos.get('password', '')
        )
        
        # Ejecutar comando
        vendedor_dto = ejecutar_comando(comando)
        
        # Preparar respuesta (sin contraseña)
        respuesta = {
            'mensaje': 'Cuenta de vendedor creada exitosamente',
            'vendedor': {
                'id': str(vendedor_dto.id),
                'nombre': vendedor_dto.nombre,
                'email': vendedor_dto.email,
                'identificacion': vendedor_dto.identificacion,
                'telefono': vendedor_dto.telefono,
                'direccion': vendedor_dto.direccion
            }
        }
        
        return Response(
            json.dumps(respuesta),
            status=201,
            mimetype='application/json'
        )
        
    except EmailYaRegistradoError:
        return Response(
            json.dumps({'error': 'El correo ya está registrado'}),
            status=409,
            mimetype='application/json'
        )
        
    except IdentificacionYaRegistradaError:
        return Response(
            json.dumps({'error': 'La identificación ya está registrada'}),
            status=409,
            mimetype='application/json'
        )
        
    except NombreInvalidoError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except EmailInvalidoError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except TelefonoInvalidoError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except IdentificacionInvalidaError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except PasswordInvalidaError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error en registro de vendedor: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}),
            status=500,
            mimetype='application/json'
        )


@bp.route('/registro-proveedor', methods=['POST'])
def registro_proveedor():
    """
    Endpoint para registrar un proveedor con autenticación
    
    Request Body:
        {
            "nombre": "string",
            "email": "string",
            "identificacion": "string",
            "telefono": "string",
            "direccion": "string",
            "password": "string"
        }
    
    Responses:
        201: Proveedor registrado exitosamente
        400: Errores de validación
        409: Email o identificación ya registrados
        500: Error interno del servidor
    """
    try:
        # Obtener datos del request
        datos = request.json
        
        # Validación básica de HTTP
        if not datos:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}),
                status=400,
                mimetype='application/json'
            )
        
        # Validar que todos los campos requeridos estén presentes
        campos_requeridos = ['nombre', 'email', 'identificacion', 'telefono', 'direccion', 'password']
        campos_faltantes = [campo for campo in campos_requeridos if campo not in datos or not datos[campo]]
        
        if campos_faltantes:
            return Response(
                json.dumps({
                    'error': 'Campos requeridos faltantes',
                    'campos': campos_faltantes
                }),
                status=400,
                mimetype='application/json'
            )
        
        # Crear comando
        comando = RegistrarProveedor(
            nombre=datos.get('nombre', ''),
            email=datos.get('email', ''),
            identificacion=datos.get('identificacion', ''),
            telefono=datos.get('telefono', ''),
            direccion=datos.get('direccion', ''),
            password=datos.get('password', '')
        )
        
        # Ejecutar comando
        proveedor_dto = ejecutar_comando(comando)
        
        # Preparar respuesta (sin contraseña)
        respuesta = {
            'mensaje': 'Cuenta de proveedor creada exitosamente',
            'proveedor': {
                'id': str(proveedor_dto.id),
                'nombre': proveedor_dto.nombre,
                'email': proveedor_dto.email,
                'identificacion': proveedor_dto.identificacion,
                'telefono': proveedor_dto.telefono,
                'direccion': proveedor_dto.direccion
            }
        }
        
        return Response(
            json.dumps(respuesta),
            status=201,
            mimetype='application/json'
        )
        
    except EmailYaRegistradoError:
        return Response(
            json.dumps({'error': 'El correo ya está registrado'}),
            status=409,
            mimetype='application/json'
        )
        
    except IdentificacionYaRegistradaError:
        return Response(
            json.dumps({'error': 'La identificación ya está registrada'}),
            status=409,
            mimetype='application/json'
        )
        
    except NombreInvalidoError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except EmailInvalidoError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except TelefonoInvalidoError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except IdentificacionInvalidaError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except PasswordInvalidaError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error en registro de proveedor: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}),
            status=500,
            mimetype='application/json'
        )


@bp.route('/registro-cliente', methods=['POST'])
def registro_cliente():
    """
    Endpoint para registrar un cliente con autenticación
    
    Request Body:
        {
            "nombre": "string",
            "email": "string",
            "identificacion": "string",
            "telefono": "string",
            "direccion": "string",
            "password": "string"
        }
    
    Responses:
        201: Cliente registrado exitosamente
        400: Errores de validación
        409: Email o identificación ya registrados
        500: Error interno del servidor
    """
    try:
        # Obtener datos del request
        datos = request.json
        
        # Validación básica de HTTP
        if not datos:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}),
                status=400,
                mimetype='application/json'
            )
        
        # Validar que todos los campos requeridos estén presentes
        campos_requeridos = ['nombre', 'email', 'identificacion', 'telefono', 'direccion', 'password']
        campos_faltantes = [campo for campo in campos_requeridos if campo not in datos or not datos[campo]]
        
        if campos_faltantes:
            return Response(
                json.dumps({
                    'error': 'Campos requeridos faltantes',
                    'campos': campos_faltantes
                }),
                status=400,
                mimetype='application/json'
            )
        
        # Crear comando
        comando = RegistrarCliente(
            nombre=datos.get('nombre', ''),
            email=datos.get('email', ''),
            identificacion=datos.get('identificacion', ''),
            telefono=datos.get('telefono', ''),
            direccion=datos.get('direccion', ''),
            password=datos.get('password', '')
        )
        
        # Ejecutar comando
        cliente_dto = ejecutar_comando(comando)
        
        # Preparar respuesta (sin contraseña)
        respuesta = {
            'mensaje': 'Cuenta de cliente creada exitosamente',
            'cliente': {
                'id': str(cliente_dto.id),
                'nombre': cliente_dto.nombre,
                'email': cliente_dto.email,
                'identificacion': cliente_dto.identificacion,
                'telefono': cliente_dto.telefono,
                'direccion': cliente_dto.direccion
            }
        }
        
        return Response(
            json.dumps(respuesta),
            status=201,
            mimetype='application/json'
        )
        
    except EmailYaRegistradoError:
        return Response(
            json.dumps({'error': 'El correo ya está registrado'}),
            status=409,
            mimetype='application/json'
        )
        
    except IdentificacionYaRegistradaError:
        return Response(
            json.dumps({'error': 'La identificación ya está registrada'}),
            status=409,
            mimetype='application/json'
        )
        
    except NombreInvalidoError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except EmailInvalidoError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except TelefonoInvalidoError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except IdentificacionInvalidaError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except PasswordInvalidaError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error en registro de cliente: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}),
            status=500,
            mimetype='application/json'
        )


@bp.route('/registro-administrador', methods=['POST'])
def registro_administrador():
    """
    Endpoint para registrar un administrador con autenticación
    
    Request Body:
        {
            "nombre": "string",
            "email": "string",
            "password": "string"
        }
    
    Responses:
        201: Administrador registrado exitosamente
        400: Errores de validación
        409: Email ya registrado
        500: Error interno del servidor
    """
    try:
        # Obtener datos del request
        datos = request.json
        
        # Validación básica de HTTP
        if not datos:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}),
                status=400,
                mimetype='application/json'
            )
        
        # Validar que todos los campos requeridos estén presentes
        campos_requeridos = ['nombre', 'email', 'password']
        campos_faltantes = [campo for campo in campos_requeridos if campo not in datos or not datos[campo]]
        
        if campos_faltantes:
            return Response(
                json.dumps({
                    'error': 'Campos requeridos faltantes',
                    'campos': campos_faltantes
                }),
                status=400,
                mimetype='application/json'
            )
        
        # Crear comando
        comando = RegistrarAdministrador(
            nombre=datos.get('nombre', ''),
            email=datos.get('email', ''),
            password=datos.get('password', '')
        )
        
        # Ejecutar comando
        administrador_dto = ejecutar_comando(comando)
        
        # Preparar respuesta (sin contraseña)
        respuesta = {
            'mensaje': 'Cuenta de administrador creada exitosamente',
            'administrador': {
                'id': str(administrador_dto.id),
                'nombre': administrador_dto.nombre,
                'email': administrador_dto.email
            }
        }
        
        return Response(
            json.dumps(respuesta),
            status=201,
            mimetype='application/json'
        )
        
    except EmailYaRegistradoError:
        return Response(
            json.dumps({'error': 'El correo ya está registrado'}),
            status=409,
            mimetype='application/json'
        )
        
    except NombreInvalidoError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except EmailInvalidoError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except PasswordInvalidaError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error en registro de administrador: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}),
            status=500,
            mimetype='application/json'
        )


@bp.route('/registro-repartidor', methods=['POST'])
def registro_repartidor():
    """
    Endpoint para registrar un repartidor con autenticación
    
    Request Body:
        {
            "nombre": "string",
            "email": "string",
            "identificacion": "string",
            "telefono": "string",
            "password": "string"
        }
    
    Responses:
        201: Repartidor registrado exitosamente
        400: Errores de validación
        409: Email o identificación ya registrados
        500: Error interno del servidor
    """
    try:
        # Obtener datos del request
        datos = request.json
        
        # Validación básica de HTTP
        if not datos:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}),
                status=400,
                mimetype='application/json'
            )
        
        # Validar que todos los campos requeridos estén presentes
        campos_requeridos = ['nombre', 'email', 'identificacion', 'telefono', 'password']
        campos_faltantes = [campo for campo in campos_requeridos if campo not in datos or not datos[campo]]
        
        if campos_faltantes:
            return Response(
                json.dumps({
                    'error': 'Campos requeridos faltantes',
                    'campos': campos_faltantes
                }),
                status=400,
                mimetype='application/json'
            )
        
        # Crear comando
        comando = RegistrarRepartidor(
            nombre=datos.get('nombre', ''),
            email=datos.get('email', ''),
            identificacion=datos.get('identificacion', ''),
            telefono=datos.get('telefono', ''),
            password=datos.get('password', '')
        )
        
        # Ejecutar comando
        repartidor_dto = ejecutar_comando(comando)
        
        # Preparar respuesta (sin contraseña)
        respuesta = {
            'mensaje': 'Cuenta de repartidor creada exitosamente',
            'repartidor': {
                'id': str(repartidor_dto.id),
                'nombre': repartidor_dto.nombre,
                'email': repartidor_dto.email,
                'identificacion': repartidor_dto.identificacion,
                'telefono': repartidor_dto.telefono
            }
        }
        
        return Response(
            json.dumps(respuesta),
            status=201,
            mimetype='application/json'
        )
        
    except EmailYaRegistradoError:
        return Response(
            json.dumps({'error': 'El correo ya está registrado'}),
            status=409,
            mimetype='application/json'
        )
        
    except IdentificacionYaRegistradaError:
        return Response(
            json.dumps({'error': 'La identificación ya está registrada'}),
            status=409,
            mimetype='application/json'
        )
        
    except NombreInvalidoError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except EmailInvalidoError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except TelefonoInvalidoError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except IdentificacionInvalidaError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except PasswordInvalidaError as e:
        return Response(
            json.dumps({'error': str(e)}),
            status=400,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error en registro de repartidor: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}),
            status=500,
            mimetype='application/json'
        )


@bp.route('/validate-credentials', methods=['POST'])
def validate_credentials():
    """
    Endpoint interno para validar credenciales de usuario
    Usado por Auth-Service para verificar email/password
    
    Request Body:
        {
            "email": "string",
            "password": "string"
        }
    
    Responses:
        200: Credenciales válidas - retorna información del usuario
        401: Credenciales inválidas o usuario inactivo
        400: Datos inválidos
        500: Error interno del servidor
    """
    try:
        # Obtener datos del request
        datos = request.json
        
        # Validación básica de HTTP
        if not datos:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}),
                status=400,
                mimetype='application/json'
            )
        
        # Validar campos requeridos
        if 'email' not in datos or not datos['email']:
            return Response(
                json.dumps({'error': 'El email es requerido'}),
                status=400,
                mimetype='application/json'
            )
        
        if 'password' not in datos or not datos['password']:
            return Response(
                json.dumps({'error': 'La contraseña es requerida'}),
                status=400,
                mimetype='application/json'
            )
        
        # Crear comando de login (solo para validar credenciales)
        comando = Login(
            email=datos['email'],
            password=datos['password']
        )
        
        # Ejecutar comando - esto valida las credenciales
        token_dto = ejecutar_comando(comando)
        
        # Retornar solo la información del usuario (sin token)
        # El Auth-Service generará su propio token
        respuesta = token_dto.user_info
        
        return Response(
            json.dumps(respuesta),
            status=200,
            mimetype='application/json'
        )
        
    except CredencialesInvalidasError:
        return Response(
            json.dumps({'error': 'Credenciales inválidas'}),
            status=401,
            mimetype='application/json'
        )
        
    except UsuarioInactivoError:
        return Response(
            json.dumps({'error': 'Usuario inactivo'}),
            status=401,
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error validando credenciales: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}),
            status=500,
            mimetype='application/json'
        )

