import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.objetos_valor import Nombre, Email, Direccion, Telefono, Identificacion, Password
from dominio.excepciones import (
    NombreInvalidoError,
    EmailInvalidoError,
    TelefonoInvalidoError,
    IdentificacionInvalidaError,
    PasswordInvalidaError
)


class TestObjetosValor:
    
    # ==================== NOMBRE ====================
    
    def test_nombre_creacion_exitosa(self):
        """Test creación exitosa de objeto Nombre"""
        # Arrange & Act
        nombre = Nombre("Farmacia Central")
        
        # Assert
        assert nombre.nombre == "Farmacia Central"
    
    def test_nombre_vacio_lanza_excepcion(self):
        """Test que nombre vacío lanza excepción"""
        # Act & Assert
        with pytest.raises(NombreInvalidoError):
            Nombre("")
    
    def test_nombre_muy_largo_lanza_excepcion(self):
        """Test que nombre muy largo lanza excepción"""
        # Arrange
        nombre_largo = "N" * 101  # Más de 100 caracteres
        
        # Act & Assert
        with pytest.raises(NombreInvalidoError):
            Nombre(nombre_largo)
    
    # ==================== EMAIL ====================
    
    def test_email_creacion_exitosa(self):
        """Test creación exitosa de objeto Email"""
        # Arrange & Act
        email = Email("contacto@farmacia.com")
        
        # Assert
        assert email.email == "contacto@farmacia.com"
    
    def test_email_invalido_lanza_excepcion(self):
        """Test que email inválido lanza excepción"""
        # Act & Assert
        with pytest.raises(EmailInvalidoError):
            Email("email_invalido")
    
    def test_email_sin_arroba_lanza_excepcion(self):
        """Test que email sin @ lanza excepción"""
        # Act & Assert
        with pytest.raises(EmailInvalidoError):
            Email("emailsinarro ba.com")
    
    def test_email_muy_largo_lanza_excepcion(self):
        """Test que email muy largo lanza excepción"""
        # Arrange
        email_largo = "e" * 90 + "@test.com"  # Más de 100 caracteres
        
        # Act & Assert
        with pytest.raises(EmailInvalidoError):
            Email(email_largo)
    
    # ==================== DIRECCION ====================
    
    def test_direccion_creacion_exitosa(self):
        """Test creación exitosa de objeto Direccion"""
        # Arrange & Act
        direccion = Direccion("Calle 123 #45-67")
        
        # Assert
        assert direccion.direccion == "Calle 123 #45-67"
    
    # ==================== TELEFONO ====================
    
    def test_telefono_creacion_exitosa(self):
        """Test creación exitosa de objeto Telefono"""
        # Arrange & Act
        telefono = Telefono("3001234567")
        
        # Assert
        assert telefono.telefono == "3001234567"
    
    def test_telefono_con_letras_lanza_excepcion(self):
        """Test que teléfono con letras lanza excepción"""
        # Act & Assert
        with pytest.raises(TelefonoInvalidoError):
            Telefono("300ABC4567")
    
    def test_telefono_con_guiones_es_valido(self):
        """Test que teléfono con guiones es válido (se limpian automáticamente)"""
        # Arrange & Act
        telefono = Telefono("300-123-4567")
        
        # Assert
        assert telefono.telefono == "300-123-4567"  # Se guarda como se ingresó
    
    def test_telefono_muy_largo_lanza_excepcion(self):
        """Test que teléfono muy largo lanza excepción"""
        # Arrange
        telefono_largo = "1" * 16  # Más de 15 caracteres
        
        # Act & Assert
        with pytest.raises(TelefonoInvalidoError):
            Telefono(telefono_largo)
    
    # ==================== IDENTIFICACION ====================
    
    def test_identificacion_creacion_exitosa(self):
        """Test creación exitosa de objeto Identificacion"""
        # Arrange & Act
        identificacion = Identificacion("1234567890")
        
        # Assert
        assert identificacion.identificacion == "1234567890"
    
    def test_identificacion_con_letras_lanza_excepcion(self):
        """Test que identificación con letras lanza excepción"""
        # Act & Assert
        with pytest.raises(IdentificacionInvalidaError):
            Identificacion("123ABC7890")
    
    def test_identificacion_con_guiones_lanza_excepcion(self):
        """Test que identificación con guiones lanza excepción"""
        # Act & Assert
        with pytest.raises(IdentificacionInvalidaError):
            Identificacion("123-456-7890")
    
    def test_identificacion_muy_larga_lanza_excepcion(self):
        """Test que identificación muy larga lanza excepción"""
        # Arrange
        identificacion_larga = "1" * 21  # Más de 20 caracteres
        
        # Act & Assert
        with pytest.raises(IdentificacionInvalidaError):
            Identificacion(identificacion_larga)
    
    # ==================== PASSWORD ====================
    
    def test_password_creacion_exitosa(self):
        """Test creación exitosa de objeto Password"""
        # Arrange & Act
        password = Password("Password123")
        
        # Assert
        assert password.password == "Password123"
    
    def test_password_muy_corta_lanza_excepcion(self):
        """Test que password muy corta lanza excepción"""
        # Act & Assert
        with pytest.raises(PasswordInvalidaError):
            Password("Pass12")  # Menos de 8 caracteres
    
    def test_password_muy_larga_lanza_excepcion(self):
        """Test que password muy larga lanza excepción"""
        # Arrange
        password_larga = "P" * 51  # Más de 50 caracteres
        
        # Act & Assert
        with pytest.raises(PasswordInvalidaError):
            Password(password_larga)
    
    def test_password_minima_longitud_valida(self):
        """Test que password con 8 caracteres es válida"""
        # Arrange & Act
        password = Password("Pass1234")  # Exactamente 8 caracteres
        
        # Assert
        assert password.password == "Pass1234"
    
    def test_password_maxima_longitud_valida(self):
        """Test que password con 50 caracteres es válida"""
        # Arrange & Act
        password = Password("P" * 50)  # Exactamente 50 caracteres
        
        # Assert
        assert password.password == "P" * 50
