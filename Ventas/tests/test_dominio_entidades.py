import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock

# Configurar el path para importar los módulos
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.entidades import Visita, Pedido, ItemPedido
from dominio.objetos_valor import EstadoVisita, EstadoPedido, FechaProgramada, Descripcion, Cantidad, Precio

class TestVisita:
    """Pruebas para la entidad Visita"""
    
    def setup_method(self):
        """Configurar para cada prueba"""
        self.fecha_futura = datetime.now() + timedelta(days=1)
        self.vendedor_id = str(uuid.uuid4())
        self.cliente_id = str(uuid.uuid4())
    
    def test_crear_visita_exitoso(self):
        """Test crear visita exitosamente"""
        visita = Visita(
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=FechaProgramada(self.fecha_futura)
        )
        
        assert visita.vendedor_id == self.vendedor_id
        assert visita.cliente_id == self.cliente_id
        assert visita.fecha_programada.fecha == self.fecha_futura
        assert visita.estado.estado == "pendiente"
        assert visita.id is not None
    
    def test_crear_visita_con_detalles_completos(self):
        """Test crear visita con todos los detalles"""
        from dominio.objetos_valor import Direccion, Telefono, Descripcion
        
        visita = Visita(
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=FechaProgramada(self.fecha_futura),
            direccion=Direccion("Calle 123 #45-67"),
            telefono=Telefono("3001234567"),
            estado=EstadoVisita("pendiente"),
            descripcion=Descripcion("Visita programada")
        )
        
        assert visita.vendedor_id == self.vendedor_id
        assert visita.cliente_id == self.cliente_id
        assert visita.fecha_programada.fecha == self.fecha_futura
        assert visita.direccion.direccion == "Calle 123 #45-67"
        assert visita.telefono.telefono == "3001234567"
        assert visita.estado.estado == "pendiente"
        assert visita.descripcion.descripcion == "Visita programada"
        assert visita.id is not None
    
    def test_disparar_evento_creacion_detallado(self):
        """Test disparar evento de creación con detalles completos"""
        from dominio.objetos_valor import Direccion, Telefono, Descripcion
        
        visita = Visita(
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=FechaProgramada(self.fecha_futura),
            direccion=Direccion("Calle 123 #45-67"),
            telefono=Telefono("3001234567"),
            estado=EstadoVisita("pendiente"),
            descripcion=Descripcion("Visita programada")
        )
        
        evento = visita.disparar_evento_creacion()
        
        assert evento.visita_id == visita.id
        assert evento.vendedor_id == self.vendedor_id
        assert evento.cliente_id == self.cliente_id
        assert evento.fecha_programada == self.fecha_futura
        assert evento.direccion == "Calle 123 #45-67"
        assert evento.telefono == "3001234567"
        assert evento.estado == "pendiente"
        assert evento.descripcion == "Visita programada"
    
    def test_visita_con_estado_personalizado(self):
        """Test crear visita con estado personalizado"""
        vendedor_id = str(uuid.uuid4())
        cliente_id = str(uuid.uuid4())
        fecha_programada = datetime.now() + timedelta(days=1)
        
        visita = Visita(
            vendedor_id=vendedor_id,
            cliente_id=cliente_id,
            fecha_programada=FechaProgramada(fecha_programada),
            estado=EstadoVisita("completada")
        )
        
        assert visita.estado.estado == "completada"
    
    def test_visita_con_id_personalizado(self):
        """Test crear visita con ID personalizado"""
        visita_id = str(uuid.uuid4())
        vendedor_id = str(uuid.uuid4())
        cliente_id = str(uuid.uuid4())
        fecha_programada = datetime.now() + timedelta(days=1)
        
        visita = Visita(
            id=visita_id,
            vendedor_id=vendedor_id,
            cliente_id=cliente_id,
            fecha_programada=FechaProgramada(fecha_programada)
        )
        
        assert visita.id == visita_id
    
    def test_visita_valores_por_defecto(self):
        """Test crear visita con valores por defecto"""
        vendedor_id = str(uuid.uuid4())
        cliente_id = str(uuid.uuid4())
        
        visita = Visita(
            vendedor_id=vendedor_id,
            cliente_id=cliente_id
        )
        
        assert visita.estado.estado == "pendiente"
        assert visita.fecha_programada is not None
        assert isinstance(visita.fecha_programada.fecha, datetime)
    
    def test_visita_creacion_basica(self):
        """Test creación básica de visita"""
        visita = Visita()
        
        assert visita.vendedor_id == ""
        assert visita.cliente_id == ""
        assert isinstance(visita.fecha_programada, FechaProgramada)
        assert isinstance(visita.estado, EstadoVisita)
    
    def test_visita_creacion_con_valores(self):
        """Test creación de visita con valores específicos"""
        vendedor_id = str(uuid.uuid4())
        cliente_id = str(uuid.uuid4())
        fecha = datetime.now().replace(microsecond=0) + timedelta(days=1)
        
        visita = Visita(
            vendedor_id=vendedor_id,
            cliente_id=cliente_id,
            fecha_programada=FechaProgramada(fecha),
            estado=EstadoVisita("pendiente")
        )
        
        assert visita.vendedor_id == vendedor_id
        assert visita.cliente_id == cliente_id
        assert visita.fecha_programada.fecha == fecha
        assert visita.estado.estado == "pendiente"
    
    def test_visita_disparar_evento_creacion(self):
        """Test que se puede disparar el evento de creación de visita"""
        vendedor_id = str(uuid.uuid4())
        cliente_id = str(uuid.uuid4())
        
        visita = Visita(
            vendedor_id=vendedor_id,
            cliente_id=cliente_id
        )
        
        # Verificar que se puede disparar el evento
        evento = visita.disparar_evento_creacion()
        assert evento is not None
        assert evento.vendedor_id == vendedor_id
        assert evento.cliente_id == cliente_id
    
    def test_visita_registrar_visita(self):
        """Test registrar visita con datos completos"""
        vendedor_id = str(uuid.uuid4())
        cliente_id = str(uuid.uuid4())
        fecha_realizada = datetime.now().date()
        hora_realizada = datetime.now().time()
        novedades = "Visita completada exitosamente"
        pedido_generado = str(uuid.uuid4())
        
        visita = Visita(
            vendedor_id=vendedor_id,
            cliente_id=cliente_id
        )
        
        visita.registrar_visita(
            fecha_realizada=fecha_realizada,
            hora_realizada=hora_realizada,
            novedades=novedades,
            pedido_generado=pedido_generado
        )
        
        assert visita.fecha_realizada == fecha_realizada
        assert visita.hora_realizada == hora_realizada
        assert visita.novedades == novedades
        assert visita.pedido_generado == pedido_generado
        assert visita.estado.estado == "completada"

class TestPedido:
    """Pruebas para la entidad Pedido"""
    
    def test_crear_pedido_exitoso(self):
        """Test crear pedido exitosamente"""
        vendedor_id = str(uuid.uuid4())
        cliente_id = str(uuid.uuid4())
        
        pedido = Pedido(
            vendedor_id=vendedor_id,
            cliente_id=cliente_id
        )
        
        assert pedido.vendedor_id == vendedor_id
        assert pedido.cliente_id == cliente_id
        assert pedido.estado.estado == "borrador"
        assert pedido.total.valor == 0.0
        assert pedido.id is not None
        assert len(pedido.items) == 0
    
    def test_pedido_con_estado_personalizado(self):
        """Test crear pedido con estado personalizado"""
        vendedor_id = str(uuid.uuid4())
        cliente_id = str(uuid.uuid4())
        
        pedido = Pedido(
            vendedor_id=vendedor_id,
            cliente_id=cliente_id,
            estado=EstadoPedido("confirmado")
        )
        
        assert pedido.estado.estado == "confirmado"
    
    def test_pedido_con_id_personalizado(self):
        """Test crear pedido con ID personalizado"""
        pedido_id = str(uuid.uuid4())
        vendedor_id = str(uuid.uuid4())
        cliente_id = str(uuid.uuid4())
        
        pedido = Pedido(
            id=pedido_id,
            vendedor_id=vendedor_id,
            cliente_id=cliente_id
        )
        
        assert pedido.id == pedido_id
    
    def test_pedido_valores_por_defecto(self):
        """Test crear pedido con valores por defecto"""
        vendedor_id = str(uuid.uuid4())
        cliente_id = str(uuid.uuid4())
        
        pedido = Pedido(
            vendedor_id=vendedor_id,
            cliente_id=cliente_id
        )
        
        assert pedido.estado.estado == "borrador"
        assert pedido.total.valor == 0.0
        assert len(pedido.items) == 0
    
    def test_pedido_creacion_basica(self):
        """Test creación básica de pedido"""
        pedido = Pedido()
        
        assert pedido.vendedor_id == ""
        assert pedido.cliente_id == ""
        assert isinstance(pedido.estado, EstadoPedido)
        assert isinstance(pedido.total, Precio)
        assert pedido.total.valor == 0.0
        assert isinstance(pedido.items, list)
        assert len(pedido.items) == 0
    
    def test_pedido_creacion_con_valores(self):
        """Test creación de pedido con valores específicos"""
        vendedor_id = str(uuid.uuid4())
        cliente_id = str(uuid.uuid4())
        
        pedido = Pedido(
            vendedor_id=vendedor_id,
            cliente_id=cliente_id,
            estado=EstadoPedido("borrador"),
            total=Precio(100.0)
        )
        
        assert pedido.vendedor_id == vendedor_id
        assert pedido.cliente_id == cliente_id
        assert pedido.estado.estado == "borrador"
        assert pedido.total.valor == 100.0
    
    def test_pedido_disparar_evento_creacion(self):
        """Test que se puede disparar el evento de creación de pedido"""
        vendedor_id = str(uuid.uuid4())
        cliente_id = str(uuid.uuid4())
        
        pedido = Pedido(
            vendedor_id=vendedor_id,
            cliente_id=cliente_id
        )
        
        # Verificar que se puede disparar el evento
        evento = pedido.disparar_evento_creacion()
        assert evento is not None
        assert evento.vendedor_id == vendedor_id
        assert evento.cliente_id == cliente_id
    
    def test_pedido_agregar_item_nuevo(self):
        """Test agregar item nuevo al pedido"""
        pedido = Pedido()
        producto_id = str(uuid.uuid4())
        cantidad = 2
        precio_unitario = 10.50
        
        item = ItemPedido(
            producto_id=producto_id,
            cantidad=Cantidad(cantidad),
            precio_unitario=Precio(precio_unitario)
        )
        
        resultado = pedido.agregar_item(item)
        
        assert resultado == True
        assert len(pedido.items) == 1
        assert pedido.items[0].producto_id == producto_id
        assert pedido.items[0].cantidad.valor == cantidad
        assert pedido.items[0].precio_unitario.valor == precio_unitario
    
    def test_pedido_agregar_item_existente(self):
        """Test agregar item que ya existe en el pedido"""
        pedido = Pedido()
        producto_id = str(uuid.uuid4())
        
        # Crear items
        item1 = ItemPedido(
            producto_id=producto_id,
            cantidad=Cantidad(2),
            precio_unitario=Precio(10.50)
        )
        
        item2 = ItemPedido(
            producto_id=producto_id,
            cantidad=Cantidad(3),
            precio_unitario=Precio(10.50)
        )
        
        # Agregar item inicial
        pedido.agregar_item(item1)
        assert len(pedido.items) == 1
        
        # Agregar el mismo producto con cantidad adicional
        pedido.agregar_item(item2)
        assert len(pedido.items) == 1  # Sigue siendo 1 item
        assert pedido.items[0].cantidad.valor == 5  # 2 + 3
    
    def test_pedido_agregar_item_no_borrador(self):
        """Test que no se puede agregar item si el pedido no está en borrador"""
        pedido = Pedido()
        pedido.estado = EstadoPedido("confirmado")
        
        item = ItemPedido(
            producto_id=str(uuid.uuid4()),
            cantidad=Cantidad(2),
            precio_unitario=Precio(10.50)
        )
        
        resultado = pedido.agregar_item(item)
        assert resultado == False
    
    def test_pedido_quitar_item_exitoso(self):
        """Test quitar item del pedido exitosamente"""
        pedido = Pedido()
        producto_id = str(uuid.uuid4())
        
        # Crear y agregar item
        item = ItemPedido(
            producto_id=producto_id,
            cantidad=Cantidad(2),
            precio_unitario=Precio(10.50)
        )
        pedido.agregar_item(item)
        assert len(pedido.items) == 1
        
        # Quitar item usando el ID del item
        resultado = pedido.quitar_item(item.id)
        assert resultado == True
        assert len(pedido.items) == 0
    
    def test_pedido_quitar_item_no_existe(self):
        """Test quitar item que no existe en el pedido"""
        pedido = Pedido()
        item_id = str(uuid.uuid4())
        
        resultado = pedido.quitar_item(item_id)
        assert resultado == False
    
    def test_pedido_quitar_item_no_borrador(self):
        """Test que no se puede quitar item si el pedido no está en borrador"""
        pedido = Pedido()
        producto_id = str(uuid.uuid4())
        
        # Crear y agregar item
        item = ItemPedido(
            producto_id=producto_id,
            cantidad=Cantidad(2),
            precio_unitario=Precio(10.50)
        )
        pedido.agregar_item(item)
        pedido.estado = EstadoPedido("confirmado")
        
        resultado = pedido.quitar_item(item.id)
        assert resultado == False
    
    def test_pedido_calcular_total(self):
        """Test calcular total del pedido"""
        pedido = Pedido()
        
        # Agregar items
        item1 = ItemPedido(
            producto_id=str(uuid.uuid4()),
            cantidad=Cantidad(2),
            precio_unitario=Precio(10.50)
        )
        
        item2 = ItemPedido(
            producto_id=str(uuid.uuid4()),
            cantidad=Cantidad(1),
            precio_unitario=Precio(5.25)
        )
        
        pedido.agregar_item(item1)
        pedido.agregar_item(item2)
        
        total = pedido.calcular_total()
        assert total == 26.25
    
    def test_pedido_calcular_total_vacio(self):
        """Test calcular total de pedido vacío"""
        pedido = Pedido()
        
        total = pedido.calcular_total()
        assert total == 0.0
    
    def test_pedido_marcar_en_transito_exitoso(self):
        """Test marcar pedido como en_transito desde confirmado"""
        pedido = Pedido(
            vendedor_id=str(uuid.uuid4()),
            cliente_id=str(uuid.uuid4()),
            estado=EstadoPedido("confirmado")
        )
        
        resultado = pedido.marcar_en_transito()
        
        assert resultado == True
        assert pedido.estado.estado == "en_transito"
    
    def test_pedido_marcar_en_transito_falla(self):
        """Test marcar pedido como en_transito desde estado incorrecto"""
        pedido = Pedido(
            vendedor_id=str(uuid.uuid4()),
            cliente_id=str(uuid.uuid4()),
            estado=EstadoPedido("borrador")
        )
        
        resultado = pedido.marcar_en_transito()
        
        assert resultado == False
        assert pedido.estado.estado == "borrador"  # No cambia
    
    def test_pedido_marcar_entregado_exitoso(self):
        """Test marcar pedido como entregado desde en_transito"""
        pedido = Pedido(
            vendedor_id=str(uuid.uuid4()),
            cliente_id=str(uuid.uuid4()),
            estado=EstadoPedido("en_transito")
        )
        
        resultado = pedido.marcar_entregado()
        
        assert resultado == True
        assert pedido.estado.estado == "entregado"
    
    def test_pedido_marcar_entregado_falla(self):
        """Test marcar pedido como entregado desde estado incorrecto"""
        pedido = Pedido(
            vendedor_id=str(uuid.uuid4()),
            cliente_id=str(uuid.uuid4()),
            estado=EstadoPedido("confirmado")
        )
        
        resultado = pedido.marcar_entregado()
        
        assert resultado == False
        assert pedido.estado.estado == "confirmado"  # No cambia

class TestItemPedido:
    """Pruebas para la entidad ItemPedido"""
    
    def test_crear_item_pedido_exitoso(self):
        """Test crear item de pedido exitosamente"""
        producto_id = str(uuid.uuid4())
        cantidad = 2
        precio_unitario = 10.50
        
        item = ItemPedido(
            producto_id=producto_id,
            cantidad=Cantidad(cantidad),
            precio_unitario=Precio(precio_unitario)
        )
        
        assert item.producto_id == producto_id
        assert item.cantidad.valor == cantidad
        assert item.precio_unitario.valor == precio_unitario
        assert item.id is not None
    
    def test_item_pedido_con_id_personalizado(self):
        """Test crear item de pedido con ID personalizado"""
        item_id = str(uuid.uuid4())
        producto_id = str(uuid.uuid4())
        
        item = ItemPedido(
            id=item_id,
            producto_id=producto_id,
            cantidad=Cantidad(2),
            precio_unitario=Precio(10.50)
        )
        
        assert item.id == item_id
    
    def test_item_pedido_calcular_subtotal(self):
        """Test calcular subtotal del item"""
        item = ItemPedido(
            producto_id=str(uuid.uuid4()),
            cantidad=Cantidad(3),
            precio_unitario=Precio(5.25)
        )
        
        subtotal = item.calcular_subtotal()
        assert subtotal == 15.75
    
    def test_item_pedido_creacion_basica(self):
        """Test creación básica de item de pedido"""
        item = ItemPedido()
        
        assert item.producto_id == ""
        assert isinstance(item.cantidad, Cantidad)
        assert isinstance(item.precio_unitario, Precio)
        assert item.cantidad.valor == 0
        assert item.precio_unitario.valor == 0.0
    
    def test_item_pedido_creacion_con_valores(self):
        """Test creación de item de pedido con valores específicos"""
        producto_id = str(uuid.uuid4())
        cantidad = 5
        precio_unitario = 12.75
        
        item = ItemPedido(
            producto_id=producto_id,
            cantidad=Cantidad(cantidad),
            precio_unitario=Precio(precio_unitario)
        )
        
        assert item.producto_id == producto_id
        assert item.cantidad.valor == cantidad
        assert item.precio_unitario.valor == precio_unitario
    
    def test_item_pedido_calcular_subtotal_cero(self):
        """Test calcular subtotal cuando cantidad es cero"""
        item = ItemPedido(
            producto_id=str(uuid.uuid4()),
            cantidad=Cantidad(0),
            precio_unitario=Precio(10.50)
        )
        
        subtotal = item.calcular_subtotal()
        assert subtotal == 0.0
    
    def test_item_pedido_actualizar_cantidad_exitoso(self):
        """Test actualizar cantidad de item exitosamente"""
        item = ItemPedido(
            producto_id=str(uuid.uuid4()),
            cantidad=Cantidad(2),
            precio_unitario=Precio(10.50)
        )
        
        resultado = item.actualizar_cantidad(5)
        assert resultado == True
        assert item.cantidad.valor == 5
    
    def test_item_pedido_actualizar_cantidad_negativa(self):
        """Test actualizar cantidad a valor negativo"""
        item = ItemPedido(
            producto_id=str(uuid.uuid4()),
            cantidad=Cantidad(2),
            precio_unitario=Precio(10.50)
        )
        
        resultado = item.actualizar_cantidad(-1)
        assert resultado == False
        assert item.cantidad.valor == 2  # No cambió
    
    def test_item_pedido_actualizar_cantidad_cero(self):
        """Test actualizar cantidad a cero"""
        item = ItemPedido(
            producto_id=str(uuid.uuid4()),
            cantidad=Cantidad(2),
            precio_unitario=Precio(10.50)
        )
        
        resultado = item.actualizar_cantidad(0)
        assert resultado == True
        assert item.cantidad.valor == 0

class TestEstadoVisita:
    """Pruebas para el objeto valor EstadoVisita"""
    
    def test_estados_disponibles(self):
        """Test que los estados están disponibles"""
        estado_pendiente = EstadoVisita("pendiente")
        estado_completada = EstadoVisita("completada")
        
        assert estado_pendiente.estado == "pendiente"
        assert estado_completada.estado == "completada"
    
    def test_estado_es_string(self):
        """Test que el estado es un string"""
        estado_pendiente = EstadoVisita("pendiente")
        estado_completada = EstadoVisita("completada")
        
        assert isinstance(estado_pendiente.estado, str)
        assert isinstance(estado_completada.estado, str)

class TestEstadoPedido:
    """Pruebas para el objeto valor EstadoPedido"""
    
    def test_estados_disponibles(self):
        """Test que los estados están disponibles"""
        estado_borrador = EstadoPedido("borrador")
        estado_confirmado = EstadoPedido("confirmado")
        estado_cancelado = EstadoPedido("cancelado")
        
        assert estado_borrador.estado == "borrador"
        assert estado_confirmado.estado == "confirmado"
        assert estado_cancelado.estado == "cancelado"
    
    def test_estado_es_string(self):
        """Test que el estado es un string"""
        estado_borrador = EstadoPedido("borrador")
        estado_confirmado = EstadoPedido("confirmado")
        
        assert isinstance(estado_borrador.estado, str)
        assert isinstance(estado_confirmado.estado, str)

class TestFechaProgramada:
    """Pruebas para el objeto valor FechaProgramada"""
    
    def test_fecha_programada_valida(self):
        """Test crear fecha programada válida"""
        from datetime import timedelta
        fecha = datetime.now() + timedelta(days=1)  # Fecha futura
        fecha_programada = FechaProgramada(fecha)
        
        assert fecha_programada.fecha == fecha
    
    def test_fecha_programada_por_defecto(self):
        """Test crear fecha programada por defecto"""
        from datetime import timedelta
        fecha = datetime.now() + timedelta(days=1)  # Fecha futura
        fecha_programada = FechaProgramada(fecha)
        
        assert isinstance(fecha_programada.fecha, datetime)
        assert fecha_programada.fecha is not None
