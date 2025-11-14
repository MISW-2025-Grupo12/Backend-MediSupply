from datetime import datetime
from unittest.mock import MagicMock, patch

from aplicacion.consultas.obtener_entregas import ObtenerEntregas, ObtenerEntregasHandler
from aplicacion.dto import EntregaDTO


class TestObtenerEntregasHandler:
    def test_handle_sin_fechas(self):
        repo_mock = MagicMock()
        repo_mock.obtener_todos.return_value = []

        with patch('aplicacion.consultas.obtener_entregas.RepositorioEntregaSQLite', return_value=repo_mock):
            handler = ObtenerEntregasHandler()
            consulta = ObtenerEntregas(con_ruta=True)
            handler.handle(consulta)

        repo_mock.obtener_todos.assert_called_once_with(con_ruta=True)

    def test_handle_con_fechas(self):
        repo_mock = MagicMock()
        repo_mock.obtener_por_rango.return_value = []

        fecha_inicio = datetime(2025, 11, 10, 8, 0, 0)
        fecha_fin = datetime(2025, 11, 10, 18, 0, 0)

        with patch('aplicacion.consultas.obtener_entregas.RepositorioEntregaSQLite', return_value=repo_mock):
            handler = ObtenerEntregasHandler()
            consulta = ObtenerEntregas(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, con_ruta=False)
            handler.handle(consulta)

        repo_mock.obtener_por_rango.assert_called_once()
        args, kwargs = repo_mock.obtener_por_rango.call_args
        assert args[0] == fecha_inicio
        # se amplía a final del día cuando fecha_inicio == fecha_fin
        assert args[1].date() == fecha_fin.date()
        assert kwargs['con_ruta'] is False

    def test_handle_filtra_por_estado(self):
        entrega_confirmada = EntregaDTO(
            direccion='Calle 1',
            fecha_entrega=datetime.now(),
            pedido={'estado': 'confirmado'}
        )
        entrega_cancelada = EntregaDTO(
            direccion='Calle 2',
            fecha_entrega=datetime.now(),
            pedido={'estado': 'cancelado'}
        )
        repo_mock = MagicMock()
        repo_mock.obtener_todos.return_value = [entrega_confirmada, entrega_cancelada]

        with patch('aplicacion.consultas.obtener_entregas.RepositorioEntregaSQLite', return_value=repo_mock):
            handler = ObtenerEntregasHandler()
            consulta = ObtenerEntregas(estado_pedido='confirmado')
            resultado = handler.handle(consulta)

        assert resultado == [entrega_confirmada]

    def test_handle_propagates_error(self):
        repo_mock = MagicMock()
        repo_mock.obtener_todos.side_effect = RuntimeError('falló')

        with patch('aplicacion.consultas.obtener_entregas.RepositorioEntregaSQLite', return_value=repo_mock):
            handler = ObtenerEntregasHandler()
            consulta = ObtenerEntregas()
            try:
                handler.handle(consulta)
            except RuntimeError as error:
                assert str(error) == 'falló'
            else:
                assert False, 'Se esperaba excepción'

