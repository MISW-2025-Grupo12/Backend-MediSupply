import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from seedwork.presentacion.paginacion import paginar_resultados, extraer_parametros_paginacion


class TestPaginarResultados:
    """Pruebas para la función paginar_resultados"""
    
    def test_paginacion_primera_pagina(self):
        """Test paginación de la primera página"""
        items = list(range(1, 11))  # [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        result = paginar_resultados(items, page=1, page_size=3)
        
        assert result['items'] == [1, 2, 3]
        assert result['pagination']['page'] == 1
        assert result['pagination']['page_size'] == 3
        assert result['pagination']['total_items'] == 10
        assert result['pagination']['total_pages'] == 4
        assert result['pagination']['has_next'] is True
        assert result['pagination']['has_prev'] is False
    
    def test_paginacion_pagina_intermedia(self):
        """Test paginación de una página intermedia"""
        items = list(range(1, 11))
        
        result = paginar_resultados(items, page=2, page_size=3)
        
        assert result['items'] == [4, 5, 6]
        assert result['pagination']['page'] == 2
        assert result['pagination']['has_next'] is True
        assert result['pagination']['has_prev'] is True
    
    def test_paginacion_ultima_pagina(self):
        """Test paginación de la última página"""
        items = list(range(1, 11))
        
        result = paginar_resultados(items, page=4, page_size=3)
        
        assert result['items'] == [10]  # Solo queda 1 item
        assert result['pagination']['page'] == 4
        assert result['pagination']['has_next'] is False
        assert result['pagination']['has_prev'] is True
    
    def test_paginacion_lista_vacia(self):
        """Test paginación de lista vacía"""
        items = []
        
        result = paginar_resultados(items, page=1, page_size=10)
        
        assert result['items'] == []
        assert result['pagination']['total_items'] == 0
        assert result['pagination']['total_pages'] == 1
        assert result['pagination']['has_next'] is False
        assert result['pagination']['has_prev'] is False
    
    def test_paginacion_page_invalido(self):
        """Test paginación con número de página inválido"""
        items = list(range(1, 11))
        
        # Page negativo debe convertirse a 1
        result = paginar_resultados(items, page=-1, page_size=5)
        assert result['pagination']['page'] == 1
        
        # Page cero debe convertirse a 1
        result = paginar_resultados(items, page=0, page_size=5)
        assert result['pagination']['page'] == 1
        
        # Page que excede total_pages debe ajustarse
        result = paginar_resultados(items, page=100, page_size=5)
        assert result['pagination']['page'] == 2  # total_pages = 2
    
    def test_paginacion_page_size_invalido(self):
        """Test paginación con tamaño de página inválido"""
        items = list(range(1, 11))
        
        # page_size negativo debe convertirse a 20 (default)
        result = paginar_resultados(items, page=1, page_size=-5)
        assert result['pagination']['page_size'] == 20
        
        # page_size cero debe convertirse a 20 (default)
        result = paginar_resultados(items, page=1, page_size=0)
        assert result['pagination']['page_size'] == 20
    
    def test_paginacion_max_page_size(self):
        """Test que page_size no exceda el máximo permitido"""
        items = list(range(1, 201))
        
        result = paginar_resultados(items, page=1, page_size=200, max_page_size=100)
        
        assert result['pagination']['page_size'] == 100
        assert len(result['items']) == 100
    
    def test_paginacion_valores_default(self):
        """Test paginación con valores por defecto"""
        items = list(range(1, 51))
        
        result = paginar_resultados(items)
        
        assert result['pagination']['page'] == 1
        assert result['pagination']['page_size'] == 20
        assert len(result['items']) == 20
    
    def test_paginacion_todos_los_items_en_una_pagina(self):
        """Test cuando todos los items caben en una página"""
        items = list(range(1, 6))  # 5 items
        
        result = paginar_resultados(items, page=1, page_size=10)
        
        assert result['items'] == [1, 2, 3, 4, 5]
        assert result['pagination']['total_pages'] == 1
        assert result['pagination']['has_next'] is False
        assert result['pagination']['has_prev'] is False


class TestExtraerParametrosPaginacion:
    """Pruebas para la función extraer_parametros_paginacion"""
    
    def test_extraer_parametros_validos(self):
        """Test extracción de parámetros válidos"""
        request_args = {'page': '2', 'page_size': '50'}
        
        page, page_size = extraer_parametros_paginacion(request_args)
        
        assert page == 2
        assert page_size == 50
    
    def test_extraer_parametros_default(self):
        """Test extracción con valores por defecto"""
        request_args = {}
        
        page, page_size = extraer_parametros_paginacion(request_args)
        
        assert page == 1
        assert page_size == 20
    
    def test_extraer_parametros_invalidos(self):
        """Test extracción con valores inválidos"""
        request_args = {'page': 'invalid', 'page_size': 'abc'}
        
        page, page_size = extraer_parametros_paginacion(request_args)
        
        assert page == 1
        assert page_size == 20
    
    def test_extraer_parametros_parciales(self):
        """Test extracción con solo algunos parámetros"""
        request_args = {'page': '3'}
        
        page, page_size = extraer_parametros_paginacion(request_args)
        
        assert page == 3
        assert page_size == 20
        
        request_args = {'page_size': '30'}
        
        page, page_size = extraer_parametros_paginacion(request_args)
        
        assert page == 1
        assert page_size == 30

