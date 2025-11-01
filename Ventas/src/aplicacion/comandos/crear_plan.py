from dataclasses import dataclass
from typing import List, Dict
from seedwork.aplicacion.comandos import Comando
from seedwork.aplicacion.comandos import ejecutar_comando as comando
from infraestructura.modelos import PlanVisitaModel, VisitaModel
from infraestructura.servicio_usuarios import ServicioUsuarios
from config.db import db
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ClienteVisita:
    id_cliente: str
    visitas: List[str]  # Fechas en formato ISO

@dataclass
class CrearPlan(Comando):
    nombre: str
    id_usuario: str
    fecha_inicio: str
    fecha_fin: str
    visitas_clientes: List[ClienteVisita]


class CrearPlanHandler:
    def __init__(self):
        pass  # no repositorio aún, usamos db directo por ahora

    def handle(self, comando: CrearPlan) -> dict:
        """Crear un nuevo plan de visitas con las visitas asociadas"""
        try:
            # Validar datos mínimos
            if not comando.nombre or not isinstance(comando.nombre, str):
                return {'success': False, 'error': 'El nombre del plan es obligatorio y debe ser texto', 'code': 400}
            if len(comando.nombre) > 100:
                return {'success': False, 'error': 'El nombre del plan no debe exceder 100 caracteres', 'code': 400}
            if not comando.id_usuario:
                return {'success': False, 'error': 'id_usuario es obligatorio', 'code': 400}

            if not comando.visitas_clientes or len(comando.visitas_clientes) == 0:
                return {'success': False, 'error': 'Debe incluir al menos un cliente con fechas de visita', 'code': 400}

            # Validar y convertir fechas de plan
            try:
                fecha_inicio_dt = datetime.fromisoformat(comando.fecha_inicio)
                fecha_fin_dt = datetime.fromisoformat(comando.fecha_fin)
            except Exception:
                return {
                    'success': False,
                    'error': 'Formato de fecha inválido. Use ISO 8601: YYYY-MM-DDTHH:MM:SS',
                    'code': 400
                }

            if fecha_inicio_dt > fecha_fin_dt:
                return {
                    'success': False,
                    'error': 'La fecha y hora de inicio no pueden ser posteriores a la fecha y hora de fin',
                    'code': 400
                }

            # Crear plan
            plan_id = str(uuid.uuid4())
            plan_model = PlanVisitaModel(
                id=plan_id,
                nombre=comando.nombre,
                id_usuario=comando.id_usuario,
                fecha_inicio=fecha_inicio_dt,
                fecha_fin=fecha_fin_dt
            )

            db.session.add(plan_model)

            # Crear visitas asociadas (enriqueciendo direccion/telefono desde Usuarios)
            cache_clientes: Dict[str, dict] = {}
            servicio_usuarios = ServicioUsuarios()

            for cliente in comando.visitas_clientes:
                cliente_id = cliente.id_cliente

                if cliente_id not in cache_clientes:
                    cliente_data = servicio_usuarios.obtener_cliente_por_id(cliente_id)
                    if not cliente_data:
                        db.session.rollback()
                        return {'success': False, 'error': 'Cliente no encontrado', 'code': 404}
                    cache_clientes[cliente_id] = cliente_data
                datos_cliente = cache_clientes[cliente_id]

                for fecha in cliente.visitas:
                    # Validar fecha de visita
                    try:
                        fecha_programada_dt = datetime.fromisoformat(fecha)
                    except Exception:
                        db.session.rollback()
                        return {
                            'success': False,
                            'error': 'Formato de fecha de visita inválido. Use ISO 8601: YYYY-MM-DDTHH:MM:SS',
                            'code': 400
                        }

                    visita_model = VisitaModel(
                        id=str(uuid.uuid4()),
                        vendedor_id=comando.id_usuario,
                        cliente_id=cliente_id,
                        fecha_programada=fecha_programada_dt,
                        direccion=datos_cliente.get("direccion", "N/A"),
                        telefono=datos_cliente.get("telefono", "N/A"),
                        estado="pendiente",
                        descripcion=f"Visita programada del plan {comando.nombre}",
                        plan_id=plan_id
                    )
                    # Validar dirección no vacía y longitud máxima
                    if not visita_model.direccion or len(visita_model.direccion) == 0:
                        db.session.rollback()
                        return {'success': False, 'error': 'La dirección de la visita no puede estar vacía', 'code': 400}
                    if len(visita_model.direccion) > 200:
                        db.session.rollback()
                        return {'success': False, 'error': 'La dirección de la visita no debe exceder 200 caracteres', 'code': 400}
                    db.session.add(visita_model)

            db.session.commit()

            return {
                'success': True,
                'message': 'Plan creado exitosamente',
                'plan_id': plan_id
            }

        except Exception as e:
            logger.error(f"Error creando plan: {e}")
            db.session.rollback()
            return {'success': False, 'error': f'Error interno: {str(e)}'}


@comando.register(CrearPlan)
def ejecutar_crear_plan(comando: CrearPlan):
    handler = CrearPlanHandler()
    return handler.handle(comando)
