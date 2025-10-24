"""
Excepciones personalizadas del dominio de Usuarios
"""

class ErrorDominio(Exception):
    """Clase base para errores de dominio"""
    pass


class EmailYaRegistradoError(ErrorDominio):
    """Error cuando se intenta registrar un email que ya existe"""
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"El correo ya está registrado")


class IdentificacionYaRegistradaError(ErrorDominio):
    """Error cuando se intenta registrar una identificación que ya existe"""
    def __init__(self, identificacion: str):
        self.identificacion = identificacion
        super().__init__(f"La identificación ya está registrada")


class IdentificacionInvalidaError(ErrorDominio):
    """Error cuando la identificación no cumple con el formato requerido"""
    def __init__(self, mensaje: str):
        super().__init__(mensaje)


class PasswordInvalidaError(ErrorDominio):
    """Error cuando la contraseña no cumple con los requisitos"""
    def __init__(self, mensaje: str):
        super().__init__(mensaje)


class CredencialesInvalidasError(ErrorDominio):
    """Error cuando las credenciales de login son inválidas"""
    def __init__(self):
        super().__init__("Credenciales inválidas")


class UsuarioInactivoError(ErrorDominio):
    """Error cuando se intenta autenticar un usuario inactivo"""
    def __init__(self):
        super().__init__("Usuario inactivo")


class UsuarioNoEncontradoError(ErrorDominio):
    """Error cuando no se encuentra un usuario"""
    def __init__(self, identificador: str):
        self.identificador = identificador
        super().__init__(f"Usuario no encontrado")


class NombreInvalidoError(ErrorDominio):
    """Error cuando el nombre no cumple con los requisitos"""
    def __init__(self, mensaje: str):
        super().__init__(mensaje)


class EmailInvalidoError(ErrorDominio):
    """Error cuando el email no cumple con el formato RFC 5322"""
    def __init__(self, mensaje: str):
        super().__init__(mensaje)


class TelefonoInvalidoError(ErrorDominio):
    """Error cuando el teléfono no cumple con el formato requerido"""
    def __init__(self, mensaje: str):
        super().__init__(mensaje)


class EstadoInvalidoError(ErrorDominio):
    """Error cuando el estado no es válido"""
    def __init__(self, mensaje: str):
        super().__init__(mensaje)
