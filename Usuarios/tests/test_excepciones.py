import pytest
import sys
import os
from unittest.mock import Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from seedwork.dominio.excepciones import (
    ExcepcionDominio, 
    IdDebeSerInmutableExcepcion, 
    ReglaNegocioExcepcion, 
    ExcepcionFabrica
)
from seedwork.dominio.reglas import ReglaNegocio
from dominio.excepciones import (
    NombreInvalidoError,
    EmailInvalidoError,
    TelefonoInvalidoError,
    IdentificacionInvalidaError,
    PasswordInvalidaError,
    EmailYaRegistradoError,
    IdentificacionYaRegistradaError,
    CredencialesInvalidasError,
    UsuarioInactivoError
)


class TestExcepcionesDominio:
    """Test para excepciones de dominio"""
    
    def test_excepcion_dominio_herencia(self):
        """Test que ExcepcionDominio hereda de Exception"""
        # Arrange & Act
        excepcion = ExcepcionDominio("Test error")
        
        # Assert
        assert isinstance(excepcion, Exception)
        assert str(excepcion) == "Test error"
    
    def test_id_debe_ser_inmutable_excepcion_mensaje_por_defecto(self):
        """Test IdDebeSerInmutableExcepcion con mensaje por defecto"""
        # Arrange & Act
        excepcion = IdDebeSerInmutableExcepcion()
        
        # Assert
        assert isinstance(excepcion, ExcepcionDominio)
        assert str(excepcion) == "El identificador debe ser inmutable"
        assert excepcion._IdDebeSerInmutableExcepcion__mensaje == "El identificador debe ser inmutable"
    
    def test_id_debe_ser_inmutable_excepcion_mensaje_personalizado(self):
        """Test IdDebeSerInmutableExcepcion con mensaje personalizado"""
        # Arrange
        mensaje = "ID no puede ser modificado"
        
        # Act
        excepcion = IdDebeSerInmutableExcepcion(mensaje)
        
        # Assert
        assert isinstance(excepcion, ExcepcionDominio)
        assert str(excepcion) == mensaje
        assert excepcion._IdDebeSerInmutableExcepcion__mensaje == mensaje
    
    def test_regla_negocio_excepcion(self):
        """Test ReglaNegocioExcepcion"""
        # Arrange
        regla = Mock(spec=ReglaNegocio)
        regla.__str__ = Mock(return_value="Regla de negocio violada")
        
        # Act
        excepcion = ReglaNegocioExcepcion(regla)
        
        # Assert
        assert isinstance(excepcion, ExcepcionDominio)
        assert excepcion.regla == regla
        assert str(excepcion) == "Regla de negocio violada"
    
    def test_excepcion_fabrica(self):
        """Test ExcepcionFabrica"""
        # Arrange
        mensaje = "Error en fábrica"
        
        # Act
        excepcion = ExcepcionFabrica(mensaje)
        
        # Assert
        assert isinstance(excepcion, ExcepcionDominio)
        assert str(excepcion) == mensaje
        assert excepcion._ExcepcionFabrica__mensaje == mensaje
    
    def test_excepcion_fabrica_con_mensaje_vacio(self):
        """Test ExcepcionFabrica con mensaje vacío"""
        # Arrange & Act
        excepcion = ExcepcionFabrica("")
        
        # Assert
        assert isinstance(excepcion, ExcepcionDominio)
        assert str(excepcion) == ""
        assert excepcion._ExcepcionFabrica__mensaje == ""


class TestExcepcionesAutenticacion:
    """Tests para excepciones específicas de autenticación"""
    
    def test_nombre_invalido_error(self):
        """Test NombreInvalidoError"""
        # Arrange & Act
        excepcion = NombreInvalidoError("Nombre no puede estar vacío")
        
        # Assert
        assert isinstance(excepcion, Exception)
        assert str(excepcion) == "Nombre no puede estar vacío"
    
    def test_email_invalido_error(self):
        """Test EmailInvalidoError"""
        # Arrange & Act
        excepcion = EmailInvalidoError("Email no cumple con formato RFC 5322")
        
        # Assert
        assert isinstance(excepcion, Exception)
        assert str(excepcion) == "Email no cumple con formato RFC 5322"
    
    def test_telefono_invalido_error(self):
        """Test TelefonoInvalidoError"""
        # Arrange & Act
        excepcion = TelefonoInvalidoError("Teléfono debe contener solo números")
        
        # Assert
        assert isinstance(excepcion, Exception)
        assert str(excepcion) == "Teléfono debe contener solo números"
    
    def test_identificacion_invalida_error(self):
        """Test IdentificacionInvalidaError"""
        # Arrange & Act
        excepcion = IdentificacionInvalidaError("Identificación debe ser numérica")
        
        # Assert
        assert isinstance(excepcion, Exception)
        assert str(excepcion) == "Identificación debe ser numérica"
    
    def test_password_invalida_error(self):
        """Test PasswordInvalidaError"""
        # Arrange & Act
        excepcion = PasswordInvalidaError("Password debe tener entre 8 y 50 caracteres")
        
        # Assert
        assert isinstance(excepcion, Exception)
        assert str(excepcion) == "Password debe tener entre 8 y 50 caracteres"
    
    def test_email_ya_registrado_error(self):
        """Test EmailYaRegistradoError"""
        # Arrange & Act
        excepcion = EmailYaRegistradoError("test@example.com")
        
        # Assert
        assert isinstance(excepcion, Exception)
        assert str(excepcion) == "El correo ya está registrado"
        assert excepcion.email == "test@example.com"
    
    def test_identificacion_ya_registrada_error(self):
        """Test IdentificacionYaRegistradaError"""
        # Arrange & Act
        excepcion = IdentificacionYaRegistradaError("1234567890")
        
        # Assert
        assert isinstance(excepcion, Exception)
        assert str(excepcion) == "La identificación ya está registrada"
        assert excepcion.identificacion == "1234567890"
    
    def test_credenciales_invalidas_error(self):
        """Test CredencialesInvalidasError"""
        # Arrange & Act
        excepcion = CredencialesInvalidasError()
        
        # Assert
        assert isinstance(excepcion, Exception)
        assert str(excepcion) == "Credenciales inválidas"
    
    def test_usuario_inactivo_error(self):
        """Test UsuarioInactivoError"""
        # Arrange & Act
        excepcion = UsuarioInactivoError()
        
        # Assert
        assert isinstance(excepcion, Exception)
        assert str(excepcion) == "Usuario inactivo"
