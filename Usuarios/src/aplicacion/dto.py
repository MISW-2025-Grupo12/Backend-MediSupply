from dataclasses import dataclass, field
import uuid
from seedwork.aplicacion.dto import DTO
from typing import Optional, Dict


@dataclass(frozen=True)
class ProveedorDTO(DTO):
    nombre: str
    email: str
    identificacion: str
    telefono: str
    direccion: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class VendedorDTO(DTO):
    nombre: str
    email: str
    identificacion: str
    telefono: str
    direccion: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class ClienteDTO(DTO):
    nombre: str
    email: str
    identificacion: str
    telefono: str
    direccion: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class AdministradorDTO(DTO):
    nombre: str
    email: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class RepartidorDTO(DTO):
    nombre: str
    email: str
    identificacion: str
    telefono: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class UsuarioDTO(DTO):
    """DTO para usuario autenticado"""
    email: str
    tipo_usuario: str
    identificacion: str
    entidad_id: str
    is_active: bool = True
    id: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass(frozen=True)
class RegistroProveedorDTO(DTO):
    """DTO para registro de proveedor con autenticación"""
    nombre: str
    email: str
    identificacion: str
    telefono: str
    direccion: str
    password: str


@dataclass(frozen=True)
class RegistroVendedorDTO(DTO):
    """DTO para registro de vendedor con autenticación"""
    nombre: str
    email: str
    identificacion: str
    telefono: str
    direccion: str
    password: str


@dataclass(frozen=True)
class RegistroClienteDTO(DTO):
    """DTO para registro de cliente con autenticación"""
    nombre: str
    email: str
    identificacion: str
    telefono: str
    direccion: str
    password: str


@dataclass(frozen=True)
class RegistroAdministradorDTO(DTO):
    """DTO para registro de administrador con autenticación"""
    nombre: str
    email: str
    password: str


@dataclass(frozen=True)
class RegistroRepartidorDTO(DTO):
    """DTO para registro de repartidor con autenticación"""
    nombre: str
    email: str
    identificacion: str
    telefono: str
    password: str


@dataclass(frozen=True)
class LoginDTO(DTO):
    """DTO para login de usuario"""
    email: str
    password: str


@dataclass(frozen=True)
class TokenDTO(DTO):
    """DTO para respuesta de token JWT"""
    access_token: str
    token_type: str
    expires_in: int
    user_info: Dict[str, any]