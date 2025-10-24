# Auth-Service - Servicio de Autenticación Centralizada

## Descripción

El Auth-Service es un servicio centralizado de autenticación y autorización para la plataforma MediSupply. Implementa:

- **Autenticación JWT**: Valida credenciales y genera tokens
- **Autorización basada en roles (RBAC)**: Controla acceso por endpoint según rol de usuario
- **Configuración externalizada**: Permisos definidos en archivo JSON

## Arquitectura

```
Cliente → Nginx Gateway → Auth-Service (valida) → Microservicio
                    ↓
            Headers: X-User-Id, X-User-Role
```

### Flujo de Autenticación

1. **Login**: Cliente envía credenciales a `/auth/login`
2. **Validación**: Auth-Service llama a servicio de Usuarios
3. **Token**: Auth-Service genera JWT y lo retorna
4. **Requests**: Cliente incluye token en header `Authorization: Bearer <token>`
5. **Verificación**: Nginx intercepta requests y llama a Auth-Service `/verify`
6. **Autorización**: Auth-Service valida token + rol contra `permissions.json`
7. **Headers**: Si autorizado, Nginx inyecta headers `X-User-*` al microservicio

## Endpoints

### `POST /login`

Autentica usuario y retorna token JWT.

**Request:**
```json
{
  "email": "usuario@medisupply.com",
  "password": "Password123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "user_info": {
    "id": "uuid",
    "email": "usuario@medisupply.com",
    "tipo_usuario": "VENDEDOR",
    "identificacion": "1234567890",
    "entidad_id": "uuid"
  }
}
```

### `GET/POST /verify`

Verifica token JWT y autorización por roles (usado internamente por Nginx).

**Headers:**
- `Authorization: Bearer <token>`
- `X-Original-Method: GET/POST/etc`
- `X-Original-URI: /path/completo`

**Response (200):**

Headers de respuesta:
- `X-User-Id: <uuid>`
- `X-User-Role: <VENDEDOR|CLIENTE|etc>`
- `X-User-Email: <email>`

**Response (401):** Token inválido

**Response (403):** Token válido pero rol no autorizado

### `GET /health`

Health check del servicio.

**Response (200):**
```json
{
  "status": "up",
  "service": "auth-service",
  "version": "1.0.0",
  "permissions_loaded": 50,
  "usuarios_service": "http://usuarios:5001"
}
```

## Configuración de Permisos

Los permisos se definen en `config/permissions.json`:

```json
{
  "POST:/ventas/api/visitas/[^/]+/evidencias": ["VENDEDOR", "ADMINISTRADOR"],
  "GET:/productos/api/productos": ["*"],
  "POST:/productos/api/productos": ["PROVEEDOR", "ADMINISTRADOR"]
}
```

### Formato

- **Key**: `METODO:/path/regex`
  - Soporta regex para paths dinámicos (ej: `[^/]+` para IDs)
- **Value**: Array de roles permitidos
  - `["*"]` = público (sin autenticación)
  - `["AUTHENTICATED"]` = cualquier usuario autenticado
  - `["VENDEDOR", "ADMINISTRADOR"]` = solo estos roles

### Roles Disponibles

- `VENDEDOR`
- `CLIENTE`
- `PROVEEDOR`
- `ADMINISTRADOR`
- `REPARTIDOR`

## Variables de Entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `JWT_SECRET_KEY` | `medisupply-jwt...` | Clave para firmar JWTs |
| `TOKEN_EXPIRATION_HOURS` | `24` | Duración del token en horas |
| `USUARIOS_SERVICE_URL` | `http://usuarios:5001` | URL del servicio de Usuarios |
| `PORT` | `5004` | Puerto del servicio |
| `FLASK_ENV` | `production` | Ambiente (development/production) |

## Docker

### Construir

```bash
docker build -t auth-service .
```

### Ejecutar

```bash
docker run -p 5004:5004 \
  -e JWT_SECRET_KEY=mi-clave-secreta \
  -e USUARIOS_SERVICE_URL=http://usuarios:5001 \
  auth-service
```

### Docker Compose

```yaml
auth-service:
  build: ./Auth-Service
  ports:
    - "5004:5004"
  environment:
    - JWT_SECRET_KEY=medisupply-jwt-secret-key-production-2024
    - USUARIOS_SERVICE_URL=http://usuarios:5001
```

## Testing

### Script de Testing

Ejecutar suite completa de tests:

```bash
python test_auth_gateway.py
```

### Manual con curl

**Login:**
```bash
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"Admin123"}'
```

**Usar token:**
```bash
TOKEN="eyJhbGc..."
curl http://localhost:8080/ventas/api/visitas \
  -H "Authorization: Bearer $TOKEN"
```

## Logs

El servicio registra:
- ✅ Logins exitosos
- ❌ Intentos fallidos de autenticación
- 🔍 Validaciones de autorización
- 🔒 Roles requeridos vs roles del usuario

Ejemplo:
```
🔐 Intento de login: admin@test.com
✅ Login exitoso: admin@test.com (ADMINISTRADOR)
🔍 Verificando: POST /ventas/api/visitas/123/evidencias
👤 Usuario: admin@test.com (ID: uuid, Rol: ADMINISTRADOR)
🔒 Roles requeridos: ['VENDEDOR', 'ADMINISTRADOR']
✅ Autorizado
```

## Seguridad

### Best Practices Implementadas

1. **JWT firmado**: Tokens no pueden ser falsificados
2. **Expiración**: Tokens expiran después de 24 horas
3. **Autorización granular**: Control por endpoint y método HTTP
4. **Headers seguros**: Info de usuario solo si autorizado
5. **Logs de auditoría**: Todos los accesos registrados

### Recomendaciones

- Usar HTTPS en producción
- Rotar `JWT_SECRET_KEY` periódicamente
- Implementar rate limiting en Nginx
- Monitorear intentos fallidos de login
- Usar secretos de Docker/Kubernetes para credenciales

## Troubleshooting

### "Token required"

Cliente no envió header `Authorization: Bearer <token>`.

### "Invalid or expired token"

Token mal formado, expirado o firmado con otra clave.

### "Forbidden: requires one of [...]"

Token válido pero usuario no tiene rol necesario para el endpoint.

### "Servicio de autenticación no disponible"

Auth-Service no puede conectar con servicio de Usuarios.

## Desarrollo

### Agregar nuevo permiso

1. Editar `config/permissions.json`
2. Agregar regla: `"METODO:/path": ["ROLES"]`
3. Reiniciar servicio (auto-recarga en desarrollo)

### Agregar nuevo rol

1. Agregar rol en servicio de Usuarios
2. Agregar en `permissions.json` donde sea necesario
3. No requiere cambios en Auth-Service (es dinámico)

## Migración desde Autenticación Distribuida

### Antes

```python
@require_auth
@require_role('VENDEDOR', 'ADMINISTRADOR')
def subir_evidencia():
    usuario_id = g.usuario['usuario_id']
    ...
```

### Después

```python
def subir_evidencia():
    usuario_id = request.headers.get('X-User-Id')
    ...
```

La autorización se maneja automáticamente en el gateway.

