from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src.aplicacion.comandos.entrega_inventario import EntregaInventario, EntregaInventarioHandler
from src.aplicacion.dto import InventarioDTO


def build_lote(producto_id, reservada, disponible=0, fecha=0, bodega_id='b1'):
    return InventarioDTO(
        producto_id=producto_id,
        cantidad_disponible=disponible,
        cantidad_reservada=reservada,
        fecha_vencimiento=fecha,
        bodega_id=bodega_id,
        pasillo='A',
        estante='1',
        requiere_cadena_frio=False
    )


def setup_repo(lotes_side_effect):
    repo = MagicMock()
    repo.obtener_por_producto_id.side_effect = lotes_side_effect
    return repo


def setup_model(instance):
    class FakeQuery:
        def __init__(self, inst):
            self.instance = inst
        def filter_by(self, **kwargs):
            return self
        def first(self):
            return self.instance

    class FakeInventarioModel:
        query = FakeQuery(instance)

    return FakeInventarioModel


def test_entrega_inventario_exitoso():
    repo = setup_repo([[build_lote('p1', 6)], [build_lote('p1', 6)]])
    inventario_instance = SimpleNamespace(cantidad_reservada=6)
    fake_model = setup_model(inventario_instance)
    fake_db = SimpleNamespace(session=MagicMock())

    fake_modules = {
        'infraestructura.modelos': SimpleNamespace(InventarioModel=fake_model),
        'config.db': SimpleNamespace(db=fake_db)
    }

    with patch('src.aplicacion.comandos.entrega_inventario.RepositorioInventarioSQLite', return_value=repo), \
            patch.dict('sys.modules', fake_modules, clear=False):

        handler = EntregaInventarioHandler()
        resultado = handler.handle(EntregaInventario(items=[{'producto_id': 'p1', 'cantidad': 5}]))

    assert resultado['success'] is True
    assert inventario_instance.cantidad_reservada == 1
    fake_db.session.commit.assert_called()


def test_entrega_inventario_producto_no_encontrado():
    repo = setup_repo([[]])

    with patch('src.aplicacion.comandos.entrega_inventario.RepositorioInventarioSQLite', return_value=repo):
        handler = EntregaInventarioHandler()
        resultado = handler.handle(EntregaInventario(items=[{'producto_id': 'p1', 'cantidad': 1}]))

    assert resultado['success'] is False
    assert 'no encontrado' in resultado['error']


def test_entrega_inventario_cantidad_insuficiente():
    repo = setup_repo([[build_lote('p1', 1)]])

    with patch('src.aplicacion.comandos.entrega_inventario.RepositorioInventarioSQLite', return_value=repo):
        handler = EntregaInventarioHandler()
        resultado = handler.handle(EntregaInventario(items=[{'producto_id': 'p1', 'cantidad': 5}]))

    assert resultado['success'] is False
    assert 'insuficiente' in resultado['error']


def test_entrega_inventario_datos_invalidos():
    repo = setup_repo([])

    with patch('src.aplicacion.comandos.entrega_inventario.RepositorioInventarioSQLite', return_value=repo):
        handler = EntregaInventarioHandler()
        resultado = handler.handle(EntregaInventario(items=[{'producto_id': '', 'cantidad': 0}]))

    assert resultado['success'] is False


def test_entrega_inventario_lote_no_encontrado():
    repo = setup_repo([[build_lote('p1', 2)], [build_lote('p1', 2)]])
    fake_model = setup_model(None)
    fake_db = SimpleNamespace(session=MagicMock())

    fake_modules = {
        'infraestructura.modelos': SimpleNamespace(InventarioModel=fake_model),
        'config.db': SimpleNamespace(db=fake_db)
    }

    with patch('src.aplicacion.comandos.entrega_inventario.RepositorioInventarioSQLite', return_value=repo), \
            patch.dict('sys.modules', fake_modules, clear=False):

        handler = EntregaInventarioHandler()
        resultado = handler.handle(EntregaInventario(items=[{'producto_id': 'p1', 'cantidad': 1}]))

    assert resultado['success'] is False
    assert 'Lote de inventario no encontrado' in resultado['error']

