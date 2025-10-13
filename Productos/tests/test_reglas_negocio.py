import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.reglas import (
    NombreProductoNoPuedeSerVacio,
    DescripcionProductoNoPuedeSerVacio,
    PrecioProductoNoPuedeSerVacio,
    PrecioProductoNoPuedeSerMenorACero,
    PrecioProductoDebeSerNumerico,
    CategoriaProductoNoPuedeSerVacia,
    CategoriaIdNoPuedeSerVacio,
    CategoriaDebeExistir,
    ProveedorIdNoPuedeSerVacio,
    ProveedorDebeExistir
)
from dominio.objetos_valor import Nombre, Descripcion, Precio, Categoria


class TestReglasNegocio:
    
    def test_nombre_producto_no_puede_ser_vacio_valido(self):
        """Test regla nombre válido"""
        nombre = Nombre("Paracetamol")
        regla = NombreProductoNoPuedeSerVacio(nombre)
        
        assert regla.es_valido() is True
    
    def test_nombre_producto_no_puede_ser_vacio_invalido(self):
        """Test regla nombre inválido"""
        nombre = Nombre("")
        regla = NombreProductoNoPuedeSerVacio(nombre)
        
        assert regla.es_valido() is False
    
    def test_nombre_producto_no_puede_ser_vacio_none(self):
        """Test regla nombre None"""
        regla = NombreProductoNoPuedeSerVacio(None)
        
        assert regla.es_valido() is False
    
    def test_descripcion_producto_no_puede_ser_vacio_valido(self):
        """Test regla descripción válida"""
        descripcion = Descripcion("Analgésico para dolor")
        regla = DescripcionProductoNoPuedeSerVacio(descripcion)
        
        assert regla.es_valido() is True
    
    def test_descripcion_producto_no_puede_ser_vacio_invalido(self):
        """Test regla descripción inválida"""
        descripcion = Descripcion("")
        regla = DescripcionProductoNoPuedeSerVacio(descripcion)
        
        assert regla.es_valido() is False
    
    def test_precio_producto_no_puede_ser_vacio_valido(self):
        """Test regla precio válido"""
        precio = Precio(25000.0)
        regla = PrecioProductoNoPuedeSerVacio(precio)
        
        assert regla.es_valido() is True
    
    def test_precio_producto_no_puede_ser_vacio_invalido(self):
        """Test regla precio inválido"""
        precio = Precio(0.0)
        regla = PrecioProductoNoPuedeSerVacio(precio)
        
        assert regla.es_valido() is False
    
    def test_precio_producto_no_puede_ser_menor_a_cero_valido(self):
        """Test regla precio mayor a cero válido"""
        precio = Precio(25000.0)
        regla = PrecioProductoNoPuedeSerMenorACero(precio)
        
        assert regla.es_valido() is True
    
    def test_precio_producto_no_puede_ser_menor_a_cero_invalido(self):
        """Test regla precio menor a cero inválido"""
        precio = Precio(-1000.0)
        regla = PrecioProductoNoPuedeSerMenorACero(precio)
        
        assert regla.es_valido() is False
    
    def test_precio_producto_debe_ser_numerico_valido(self):
        """Test regla precio numérico válido"""
        precio = Precio(25000.0)
        regla = PrecioProductoDebeSerNumerico(precio)
        
        assert regla.es_valido() is True
    
    
    def test_categoria_producto_no_puede_ser_vacia_valida(self):
        """Test regla categoría válida"""
        categoria = Categoria("Medicamentos")
        regla = CategoriaProductoNoPuedeSerVacia(categoria)
        
        assert regla.es_valido() is True
    
    def test_categoria_producto_no_puede_ser_vacia_invalida(self):
        """Test regla categoría inválida"""
        categoria = Categoria("")
        regla = CategoriaProductoNoPuedeSerVacia(categoria)
        
        assert regla.es_valido() is False
    
    def test_categoria_id_no_puede_ser_vacio_valido(self):
        """Test regla categoría ID válido"""
        categoria_id = "123e4567-e89b-12d3-a456-426614174000"
        regla = CategoriaIdNoPuedeSerVacio(categoria_id)
        
        assert regla.es_valido() is True
    
    def test_categoria_id_no_puede_ser_vacio_invalido(self):
        """Test regla categoría ID inválido"""
        categoria_id = ""
        regla = CategoriaIdNoPuedeSerVacio(categoria_id)
        
        assert regla.es_valido() is False
    
    def test_categoria_debe_existir_con_mock(self):
        """Test regla categoría debe existir con mock"""
        categoria_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_repo = Mock()
        mock_repo.obtener_por_id.return_value = Mock()  # Categoría existe
        regla = CategoriaDebeExistir(categoria_id, mock_repo)
        
        assert regla.es_valido() is True
        mock_repo.obtener_por_id.assert_called_once_with(categoria_id)
    
    def test_categoria_debe_existir_no_existe(self):
        """Test regla categoría no existe"""
        categoria_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_repo = Mock()
        mock_repo.obtener_por_id.return_value = None  # Categoría no existe
        regla = CategoriaDebeExistir(categoria_id, mock_repo)
        
        assert regla.es_valido() is False
    
    def test_proveedor_id_no_puede_ser_vacio_valido(self):
        """Test regla proveedor ID válido"""
        proveedor_id = "123e4567-e89b-12d3-a456-426614174000"
        regla = ProveedorIdNoPuedeSerVacio(proveedor_id)
        
        assert regla.es_valido() is True
    
    def test_proveedor_id_no_puede_ser_vacio_invalido(self):
        """Test regla proveedor ID inválido"""
        proveedor_id = ""
        regla = ProveedorIdNoPuedeSerVacio(proveedor_id)
        
        assert regla.es_valido() is False
    
    def test_proveedor_debe_existir_con_mock(self):
        """Test regla proveedor debe existir con mock"""
        proveedor_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_servicio = Mock()
        mock_servicio.validar_proveedor_existe.return_value = True
        regla = ProveedorDebeExistir(proveedor_id, mock_servicio)
        
        assert regla.es_valido() is True
        mock_servicio.validar_proveedor_existe.assert_called_once_with(proveedor_id)
    
    def test_proveedor_debe_existir_no_existe(self):
        """Test regla proveedor no existe"""
        proveedor_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_servicio = Mock()
        mock_servicio.validar_proveedor_existe.return_value = False
        regla = ProveedorDebeExistir(proveedor_id, mock_servicio)
        
        assert regla.es_valido() is False
