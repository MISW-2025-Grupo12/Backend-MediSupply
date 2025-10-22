from dataclasses import dataclass
from seedwork.dominio.objetos_valor import ObjetoValor
from email_validator import validate_email, EmailNotValidError
from .excepciones import (
    NombreInvalidoError, 
    EmailInvalidoError, 
    TelefonoInvalidoError,
    IdentificacionInvalidaError,
    PasswordInvalidaError
)


@dataclass(frozen=True)
class Nombre(ObjetoValor):
    nombre: str
    
    def __post_init__(self):
        if not self.nombre or not self.nombre.strip():
            raise NombreInvalidoError("El nombre no puede estar vacío")
        
        if len(self.nombre) > 100:
            raise NombreInvalidoError("El nombre excede los 100 caracteres")


@dataclass(frozen=True)
class Email(ObjetoValor):
    email: str
    
    def __post_init__(self):
        if not self.email or not self.email.strip():
            raise EmailInvalidoError("El correo electrónico no puede estar vacío")
        
        if len(self.email) > 100:
            raise EmailInvalidoError("El correo electrónico excede los 100 caracteres")
        
        # Validar formato según RFC 5322
        try:
            validate_email(self.email, check_deliverability=False)
        except EmailNotValidError as e:
            raise EmailInvalidoError("El correo electrónico no es válido")


@dataclass(frozen=True)
class Direccion(ObjetoValor):
    direccion: str


@dataclass(frozen=True)
class Telefono(ObjetoValor):
    telefono: str
    
    def __post_init__(self):
        if not self.telefono or not self.telefono.strip():
            raise TelefonoInvalidoError("El teléfono no puede estar vacío")
        
        # Verificar que solo contenga números (puede incluir espacios y guiones opcionales)
        telefono_limpio = self.telefono.replace(" ", "").replace("-", "").replace("+", "")
        
        if not telefono_limpio.isdigit():
            raise TelefonoInvalidoError("El teléfono debe contener solo números")
        
        if len(telefono_limpio) > 15:
            raise TelefonoInvalidoError("El teléfono excede los 15 caracteres")


@dataclass(frozen=True)
class Identificacion(ObjetoValor):
    identificacion: str
    
    def __post_init__(self):
        if not self.identificacion or not self.identificacion.strip():
            raise IdentificacionInvalidaError("La identificación no puede estar vacía")
        
        if not self.identificacion.isdigit():
            raise IdentificacionInvalidaError("La identificación debe contener solo números")
        
        if len(self.identificacion) > 20:
            raise IdentificacionInvalidaError("La identificación excede los 20 caracteres")


@dataclass(frozen=True)
class Password(ObjetoValor):
    password: str
    
    def __post_init__(self):
        if not self.password:
            raise PasswordInvalidaError("La contraseña no puede estar vacía")
        
        if len(self.password) < 8:
            raise PasswordInvalidaError("La contraseña debe tener al menos 8 caracteres")
        
        if len(self.password) > 50:
            raise PasswordInvalidaError("La contraseña excede los 50 caracteres")