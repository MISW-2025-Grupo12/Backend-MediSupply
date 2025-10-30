from dataclasses import dataclass
from typing import List, Dict
from seedwork.aplicacion.comandos import Comando
from seedwork.aplicacion.comandos import ejecutar_comando as comando
from infraestructura.modelos import PlanVisitaModel, VisitaModel
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
            if not comando.nombre or not comando.id_usuario:
                return {'success': False, 'error': 'nombre e id_usuario son obligatorios'}

            if not comando.visitas_clientes or len(comando.visitas_clientes) == 0:
                return {'success': False, 'error': 'Debe incluir al menos un cliente con fechas de visita'}

            # Crear plan
            plan_id = str(uuid.uuid4())
            plan_model = PlanVisitaModel(
                id=plan_id,
                nombre=comando.nombre,
                id_usuario=comando.id_usuario,
                fecha_inicio=datetime.fromisoformat(comando.fecha_inicio),
                fecha_fin=datetime.fromisoformat(comando.fecha_fin)
            )

            db.session.add(plan_model)

            # Crear visitas asociadas
            for cliente in comando.visitas_clientes:
                cliente_id = cliente.id_cliente
                for fecha in cliente.visitas:
                    visita_model = VisitaModel(
                        id=str(uuid.uuid4()),
                        vendedor_id=comando.id_usuario,
                        cliente_id=cliente_id,
                        fecha_programada=datetime.fromisoformat(fecha),
                        direccion=f"Visita automática del plan {comando.nombre}",
                        telefono="N/A",
                        estado="pendiente",
                        descripcion=f"Visita programada del plan {comando.nombre}",
                        plan_id=plan_id
                    )
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
