from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta
from seedwork.aplicacion.consultas import ejecutar_consulta as consulta
from infraestructura.repositorios import RepositorioPedidoSQLite
from infraestructura.servicio_usuarios import ServicioUsuarios

import logging

logger = logging.getLogger(__name__)

@dataclass
class ObtenerInformeVentasPorVendedor(Consulta):
    fecha_inicio: str = None
    fecha_fin: str = None

class ObtenerInformeVentasPorVendedorHandler:
    def __init__(self):
        self._repositorio: RepositorioPedidoSQLite = RepositorioPedidoSQLite()
        self._servicio_usuarios: ServicioUsuarios = ServicioUsuarios()

    def handle(self, consulta: ObtenerInformeVentasPorVendedor) -> list[dict]:
        try:
            pedidos = self._repositorio.obtener_pedidos_confirmados(
                fecha_inicio=consulta.fecha_inicio,
                fecha_fin=consulta.fecha_fin
            )

            if not pedidos:
                logger.info("No se encontraron pedidos entregados en el rango dado.")
                return []

            ventas_por_vendedor = {}

            for pedido in pedidos:
                if not pedido.vendedor_id:
                    continue

                vendedor_id = pedido.vendedor_id

                if vendedor_id not in ventas_por_vendedor:
                    vendedor_datos = self._servicio_usuarios.obtener_vendedor_por_id(vendedor_id)
                    vendedor_nombre = vendedor_datos.get("nombre") if vendedor_datos else "Vendedor desconocido"

                    ventas_por_vendedor[vendedor_id] = {
                        "vendedor_id": vendedor_id,
                        "vendedor_nombre": vendedor_nombre,
                        "numero_pedidos": 0,
                        "total_ventas": 0.0,
                        "clientes_atendidos": set()
                    }

                ventas_por_vendedor[vendedor_id]["numero_pedidos"] += 1
                ventas_por_vendedor[vendedor_id]["total_ventas"] += pedido.total.valor
                ventas_por_vendedor[vendedor_id]["clientes_atendidos"].add(pedido.cliente_id)

            resultado = []
            for vendedor_id, datos in ventas_por_vendedor.items():
                resultado.append({
                    "vendedor_id": datos["vendedor_id"],
                    "vendedor_nombre": datos["vendedor_nombre"],
                    "numero_pedidos": datos["numero_pedidos"],
                    "total_ventas": datos["total_ventas"],
                    "clientes_atendidos": len(datos["clientes_atendidos"])
                })

            logger.info(f"Informe de ventas por vendedor generado: {len(resultado)} vendedores")
            return resultado

        except Exception as e:
            logger.error(f"Error generando informe de ventas por vendedor: {e}")
            return []

@consulta.register(ObtenerInformeVentasPorVendedor)
def ejecutar_obtener_informe_ventas_por_vendedor(consulta: ObtenerInformeVentasPorVendedor):
    handler = ObtenerInformeVentasPorVendedorHandler()
    return handler.handle(consulta)

