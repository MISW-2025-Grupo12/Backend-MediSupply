import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from seedwork.dominio.repositorios import Repositorio

class TestRepositorio:
    def test_crear_repositorio_abstracto(self):
        # Repositorio es abstracto, solo verificamos que existe
        assert Repositorio is not None

    def test_repositorio_es_abstracto(self):
        assert hasattr(Repositorio, '__abstractmethods__')

    def test_repositorio_herencia(self):
        # Verificar que Repositorio puede ser heredado
        class MiRepositorio(Repositorio):
            def obtener_por_id(self, id):
                return {"id": id, "datos": "test"}
            
            def obtener_todos(self):
                return [{"id": 1}, {"id": 2}]
            
            def agregar(self, entidad):
                return {"id": entidad.get("id"), "agregado": True}
            
            def actualizar(self, entidad):
                return {"id": entidad.get("id"), "actualizado": True}
            
            def eliminar(self, id):
                return {"id": id, "eliminado": True}
        
        repositorio = MiRepositorio()
        assert repositorio is not None

    def test_repositorio_con_metodos_abstractos(self):
        # Verificar que se puede crear una clase que herede de Repositorio
        class TestRepositorio(Repositorio):
            def obtener_por_id(self, id):
                return {"id": id}
            
            def obtener_todos(self):
                return []
            
            def agregar(self, entidad):
                return entidad
            
            def actualizar(self, entidad):
                return entidad
            
            def eliminar(self, id):
                return {"id": id}
        
        repositorio = TestRepositorio()
        assert repositorio is not None

    def test_repositorio_obtener_por_id(self):
        class TestRepositorio(Repositorio):
            def __init__(self):
                self.datos = {1: {"id": 1, "nombre": "test1"}, 2: {"id": 2, "nombre": "test2"}}
            
            def obtener_por_id(self, id):
                return self.datos.get(id)
            
            def obtener_todos(self):
                return list(self.datos.values())
            
            def agregar(self, entidad):
                self.datos[entidad["id"]] = entidad
                return entidad
            
            def actualizar(self, entidad):
                if entidad["id"] in self.datos:
                    self.datos[entidad["id"]] = entidad
                return entidad
            
            def eliminar(self, id):
                return self.datos.pop(id, None)
        
        repositorio = TestRepositorio()
        
        # Obtener entidad existente
        entidad = repositorio.obtener_por_id(1)
        assert entidad["id"] == 1
        assert entidad["nombre"] == "test1"
        
        # Obtener entidad no existente
        entidad = repositorio.obtener_por_id(999)
        assert entidad is None

    def test_repositorio_obtener_todos(self):
        class TestRepositorio(Repositorio):
            def __init__(self):
                self.datos = [{"id": 1}, {"id": 2}, {"id": 3}]
            
            def obtener_por_id(self, id):
                return next((d for d in self.datos if d["id"] == id), None)
            
            def obtener_todos(self):
                return self.datos.copy()
            
            def agregar(self, entidad):
                self.datos.append(entidad)
                return entidad
            
            def actualizar(self, entidad):
                for i, d in enumerate(self.datos):
                    if d["id"] == entidad["id"]:
                        self.datos[i] = entidad
                        break
                return entidad
            
            def eliminar(self, id):
                for i, d in enumerate(self.datos):
                    if d["id"] == id:
                        return self.datos.pop(i)
                return None
        
        repositorio = TestRepositorio()
        
        todas = repositorio.obtener_todos()
        assert len(todas) == 3
        assert todas[0]["id"] == 1
        assert todas[1]["id"] == 2
        assert todas[2]["id"] == 3

    def test_repositorio_agregar(self):
        class TestRepositorio(Repositorio):
            def __init__(self):
                self.datos = []
            
            def obtener_por_id(self, id):
                return next((d for d in self.datos if d["id"] == id), None)
            
            def obtener_todos(self):
                return self.datos.copy()
            
            def agregar(self, entidad):
                self.datos.append(entidad)
                return entidad
            
            def actualizar(self, entidad):
                for i, d in enumerate(self.datos):
                    if d["id"] == entidad["id"]:
                        self.datos[i] = entidad
                        break
                return entidad
            
            def eliminar(self, id):
                for i, d in enumerate(self.datos):
                    if d["id"] == id:
                        return self.datos.pop(i)
                return None
        
        repositorio = TestRepositorio()
        
        nueva_entidad = {"id": 4, "nombre": "test4"}
        resultado = repositorio.agregar(nueva_entidad)
        
        assert resultado == nueva_entidad
        assert len(repositorio.obtener_todos()) == 1
        assert repositorio.obtener_por_id(4) == nueva_entidad

    def test_repositorio_actualizar(self):
        class TestRepositorio(Repositorio):
            def __init__(self):
                self.datos = [{"id": 1, "nombre": "test1"}]
            
            def obtener_por_id(self, id):
                return next((d for d in self.datos if d["id"] == id), None)
            
            def obtener_todos(self):
                return self.datos.copy()
            
            def agregar(self, entidad):
                self.datos.append(entidad)
                return entidad
            
            def actualizar(self, entidad):
                for i, d in enumerate(self.datos):
                    if d["id"] == entidad["id"]:
                        self.datos[i] = entidad
                        break
                return entidad
            
            def eliminar(self, id):
                for i, d in enumerate(self.datos):
                    if d["id"] == id:
                        return self.datos.pop(i)
                return None
        
        repositorio = TestRepositorio()
        
        entidad_actualizada = {"id": 1, "nombre": "test1_actualizado"}
        resultado = repositorio.actualizar(entidad_actualizada)
        
        assert resultado == entidad_actualizada
        assert repositorio.obtener_por_id(1)["nombre"] == "test1_actualizado"

    def test_repositorio_eliminar(self):
        class TestRepositorio(Repositorio):
            def __init__(self):
                self.datos = [{"id": 1, "nombre": "test1"}, {"id": 2, "nombre": "test2"}]
            
            def obtener_por_id(self, id):
                return next((d for d in self.datos if d["id"] == id), None)
            
            def obtener_todos(self):
                return self.datos.copy()
            
            def agregar(self, entidad):
                self.datos.append(entidad)
                return entidad
            
            def actualizar(self, entidad):
                for i, d in enumerate(self.datos):
                    if d["id"] == entidad["id"]:
                        self.datos[i] = entidad
                        break
                return entidad
            
            def eliminar(self, id):
                for i, d in enumerate(self.datos):
                    if d["id"] == id:
                        return self.datos.pop(i)
                return None
        
        repositorio = TestRepositorio()
        
        # Eliminar entidad existente
        resultado = repositorio.eliminar(1)
        assert resultado["id"] == 1
        assert len(repositorio.obtener_todos()) == 1
        assert repositorio.obtener_por_id(1) is None
        
        # Eliminar entidad no existente
        resultado = repositorio.eliminar(999)
        assert resultado is None
        assert len(repositorio.obtener_todos()) == 1

    def test_repositorio_con_error_handling(self):
        class TestRepositorio(Repositorio):
            def __init__(self):
                self.datos = [{"id": 1, "nombre": "test1"}]
                self.raise_error = False
            
            def obtener_por_id(self, id):
                if self.raise_error:
                    raise Exception("Error de base de datos")
                return next((d for d in self.datos if d["id"] == id), None)
            
            def obtener_todos(self):
                if self.raise_error:
                    raise Exception("Error de base de datos")
                return self.datos.copy()
            
            def agregar(self, entidad):
                if self.raise_error:
                    raise Exception("Error de base de datos")
                self.datos.append(entidad)
                return entidad
            
            def actualizar(self, entidad):
                if self.raise_error:
                    raise Exception("Error de base de datos")
                for i, d in enumerate(self.datos):
                    if d["id"] == entidad["id"]:
                        self.datos[i] = entidad
                        break
                return entidad
            
            def eliminar(self, id):
                if self.raise_error:
                    raise Exception("Error de base de datos")
                for i, d in enumerate(self.datos):
                    if d["id"] == id:
                        return self.datos.pop(i)
                return None
        
        repositorio = TestRepositorio()
        
        # Operaciones normales
        assert repositorio.obtener_por_id(1)["id"] == 1
        assert len(repositorio.obtener_todos()) == 1
        
        # Activar modo de error
        repositorio.raise_error = True
        
        # Verificar que se lanzan excepciones
        with pytest.raises(Exception, match="Error de base de datos"):
            repositorio.obtener_por_id(1)
        
        with pytest.raises(Exception, match="Error de base de datos"):
            repositorio.obtener_todos()
        
        with pytest.raises(Exception, match="Error de base de datos"):
            repositorio.agregar({"id": 2, "nombre": "test2"})
        
        with pytest.raises(Exception, match="Error de base de datos"):
            repositorio.actualizar({"id": 1, "nombre": "test1_actualizado"})
        
        with pytest.raises(Exception, match="Error de base de datos"):
            repositorio.eliminar(1)
