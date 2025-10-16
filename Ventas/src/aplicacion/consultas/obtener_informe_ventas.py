from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta
from seedwork.aplicacion.consultas import ejecutar_consulta as consulta
from infraestructura.repositorios import RepositorioPedidoSQLite
from infraestructura.servicio_usuarios import ServicioUsuarios

import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------
# Consulta: ObtenerInformeVentas
# ---------------------------------------------------------------
@dataclass
class ObtenerInformeVentas(Consulta):
    """Consulta para obtener los datos del dashboard de ventas."""
    fecha_inicio: str = None
    fecha_fin: str = None
    vendedor_id: str = None


# ---------------------------------------------------------------
# Handler: ObtenerInformeVentasHandler
# ---------------------------------------------------------------
class ObtenerInformeVentasHandler:
    def __init__(self):
        self._repositorio: RepositorioPedidoSQLite = RepositorioPedidoSQLite()
        self._servicio_usuarios: ServicioUsuarios = ServicioUsuarios()

    def handle(self, consulta: ObtenerInformeVentas) -> dict:
        """
        Obtiene las métricas principales del dashboard:
        - Ventas totales
        - Total de productos vendidos
        - Ventas por mes
        - Ventas por cliente
        - Productos más vendidos
        """
        try:
            pedidos = self._repositorio.obtener_pedidos_confirmados(
                fecha_inicio=consulta.fecha_inicio,
                fecha_fin=consulta.fecha_fin,
                vendedor_id=consulta.vendedor_id
            )

            if not pedidos:
                logger.info("No se encontraron pedidos confirmados en el rango dado.")
                return {
                    "ventas_totales": 0,
                    "total_productos_vendidos": 0,
                    "ventas_por_mes": {},
                    "ventas_por_cliente": {},
                    "productos_mas_vendidos": []
                }

            total_ventas = 0
            total_productos_vendidos = 0
            ventas_por_mes = {}
            ventas_por_cliente = {}
            productos_vendidos = {}

            # -------------------------------------------------------
            # Recorremos los pedidos confirmados y acumulamos métricas
            # -------------------------------------------------------
            for pedido in pedidos:
                total_ventas += pedido.total.valor

                # 🧩 Ventas por cliente (id + nombre si disponible)
                cliente_id = pedido.cliente_id
                cliente_datos = self._servicio_usuarios.obtener_cliente_por_id(pedido.cliente_id)
                cliente_nombre = cliente_datos.get("nombre") if cliente_datos else "Cliente desconocido"
                if cliente_id not in ventas_por_cliente:
                    ventas_por_cliente[cliente_id] = {
                        "nombre": cliente_nombre,
                        "cantidad_pedidos": 0,
                        "monto_total": 0
                    }
                ventas_por_cliente[cliente_id]["cantidad_pedidos"] += 1  # cantidad de pedidos
                ventas_por_cliente[cliente_id]["monto_total"] += pedido.total.valor



                # 🗓️ Ventas por mes
                fecha_pedido = getattr(pedido, "created_at", None) or getattr(pedido, "_created_at_model", None)
                if fecha_pedido:
                    mes_key = fecha_pedido.strftime("%Y-%m")
                    ventas_por_mes[mes_key] = ventas_por_mes.get(mes_key, 0) + pedido.total.valor

                # 🔢 Productos vendidos
                for item in pedido.items:
                    cantidad = item.cantidad.valor
                    producto_id = item.producto_id
                    producto_nombre = getattr(item, "nombre_producto", "Producto sin nombre")

                    total_productos_vendidos += cantidad

                    if producto_id not in productos_vendidos:
                        productos_vendidos[producto_id] = {"nombre": producto_nombre, "cantidad": 0}
                    productos_vendidos[producto_id]["cantidad"] += cantidad


            # -------------------------------------------------------
            # Productos más vendidos (Top 10)
            # -------------------------------------------------------
            productos_mas_vendidos = [
                {
                    "producto_id": pid,
                    "nombre": datos["nombre"],
                    "cantidad": datos["cantidad"]
                }
                for pid, datos in sorted(productos_vendidos.items(), key=lambda x: x[1]["cantidad"], reverse=True)[:10]
            ]

            # ✅ Ventas por cliente (convertimos a lista para el frontend)
            ventas_por_cliente_formateadas = [
                {
                    "cliente_id": cid,
                    "nombre": datos["nombre"],
                    "cantidad_pedidos": datos["cantidad_pedidos"],
                    "monto_total": datos["monto_total"]
                }
                for cid, datos in ventas_por_cliente.items()
            ]

            # ✅ Retorno final
            return {
                "ventas_totales": total_ventas,
                "total_productos_vendidos": total_productos_vendidos,
                "ventas_por_mes": ventas_por_mes,
                "ventas_por_cliente": ventas_por_cliente_formateadas,
                "productos_mas_vendidos": productos_mas_vendidos
            }

        except Exception as e:
            logger.error(f"Error generando informe de ventas: {e}")
            return {
                "ventas_totales": 0,
                "total_productos_vendidos": 0,
                "ventas_por_mes": {},
                "ventas_por_cliente": {},
                "productos_mas_vendidos": []
            }


# ---------------------------------------------------------------
# Registro de la consulta en el seedwork
# ---------------------------------------------------------------
@consulta.register(ObtenerInformeVentas)
def ejecutar_obtener_informe_ventas(consulta: ObtenerInformeVentas):
    handler = ObtenerInformeVentasHandler()
    return handler.handle(consulta)
