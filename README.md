# Backend-MediSupply

## 👥 Equipo

**MISO GRUPO 12:**
- Manuel Sanchez
- Jairo Reyes  
- Nicolas Malagon
- Sergio Perez

## 📚 Documentación

### 📖 Documentación Pública
- **Postman Documentation**: [Ver documentación completa](https://documenter.getpostman.com/view/30409960/2sB3QMKUGP)

### 🧪 Colecciones de Postman
- **MediSupply - Flujo Completo**: Colección principal con flujo de ejecución automático
- **MediSupply - Proyecto Final**: Colección original del proyecto

## 🏗️ Arquitectura

El sistema está compuesto por 4 microservicios:

- **🔐 Usuarios** (Puerto 5001) - Gestión de proveedores, vendedores y clientes
- **📦 Productos** (Puerto 5000) - Catálogo de productos y categorías  
- **🛒 Ventas** (Puerto 5002) - Gestión de visitas y pedidos
- **🚚 Logística** (Puerto 5003) - Control de inventario y entregas

## 🚀 Requisitos

- Docker y Docker Compose
- Python 3.9+
- PostgreSQL 15

## 🐳 Ejecución

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver estado de los servicios
docker-compose ps

# Ver logs de un servicio específico
docker-compose logs -f ventas
```

## 📋 Flujo de Ejecución

1. **Configuración Inicial** - Verificar servicios
2. **Crear Entidades Base** - Proveedores, Categorías, Vendedores, Clientes
3. **Crear Productos** - Con y sin inventario
4. **Crear Visitas** - Programar visitas de venta
5. **Crear Pedidos** - Con items y confirmación
6. **Gestionar Inventario** - Reservas y descuentos
7. **Consultar Entregas** - Ver entregas programadas

## 🔧 Endpoints Principales

### 🔐 Usuarios (Puerto 5001)
**Gestión de proveedores, vendedores y clientes**

#### Proveedores
- `POST /usuarios/api/proveedores/` - Crear proveedor
- `GET /usuarios/api/proveedores/` - Obtener todos los proveedores
- `GET /usuarios/api/proveedores/{id}` - Obtener proveedor por ID

#### Vendedores
- `POST /usuarios/api/vendedores/` - Crear vendedor
- `GET /usuarios/api/vendedores/` - Obtener todos los vendedores
- `GET /usuarios/api/vendedores/{id}` - Obtener vendedor por ID

#### Clientes
- `POST /usuarios/api/clientes/` - Crear cliente
- `GET /usuarios/api/clientes/` - Obtener todos los clientes
- `GET /usuarios/api/clientes/{id}` - Obtener cliente por ID

#### Salud del Servicio
- `GET /health` - Estado del servicio

### 📦 Productos (Puerto 5000)
**Catálogo de productos y categorías**

#### Productos
- `POST /productos/api/productos/` - Crear producto básico
- `POST /productos/api/productos/con-inventario` - Crear producto con inventario
- `GET /productos/api/productos/` - Obtener todos los productos
- `GET /productos/api/productos/{id}` - Obtener producto por ID

#### Categorías
- `POST /productos/api/categorias/` - Crear categoría
- `GET /productos/api/categorias/` - Obtener todas las categorías
- `GET /productos/api/categorias/{id}` - Obtener categoría por ID

#### Salud del Servicio
- `GET /health` - Estado del servicio

### 🛒 Ventas (Puerto 5002)
**Gestión de visitas y pedidos**

#### Visitas
- `POST /ventas/api/visitas/` - Crear visita
- `GET /ventas/api/visitas/` - Obtener visitas (con filtro de estado opcional)
- `GET /ventas/api/visitas/vendedor/{vendedor_id}` - Obtener visitas por vendedor
- `PUT /ventas/api/visitas/{visita_id}` - Registrar/actualizar visita

#### Pedidos
- `POST /ventas/api/pedidos/` - Crear pedido
- `GET /ventas/api/pedidos/` - Obtener todos los pedidos (con filtros opcionales)
- `GET /ventas/api/pedidos/{pedido_id}` - Obtener pedido por ID
- `POST /ventas/api/pedidos/{pedido_id}/items` - Agregar item al pedido
- `PUT /ventas/api/pedidos/{pedido_id}/items/{item_id}` - Actualizar item del pedido
- `DELETE /ventas/api/pedidos/{pedido_id}/items/{item_id}` - Quitar item del pedido
- `POST /ventas/api/pedidos/{pedido_id}/confirmar` - Confirmar pedido

#### Búsqueda de Productos
- `GET /ventas/api/pedidos/productos/buscar` - Buscar productos con inventario disponible

#### Salud del Servicio
- `GET /health` - Estado del servicio
- `GET /ventas/health` - Estado detallado del servicio
- `GET /spec` - Documentación Swagger

### 🚚 Logística (Puerto 5003)
**Control de inventario y entregas**

#### Inventario
- `GET /logistica/api/inventario/` - Obtener todo el inventario
- `GET /logistica/api/inventario/buscar` - Buscar productos con inventario
- `POST /logistica/api/inventario/reservar` - Reservar inventario
- `POST /logistica/api/inventario/descontar` - Descontar inventario
- `GET /logistica/api/inventario/producto/{id}` - Obtener inventario de producto específico

#### Entregas
- `GET /logistica/api/entregas/` - Obtener entregas programadas (con filtros de fecha)
- `POST /logistica/api/entregas/creartemp` - Crear entregas temporales (para pruebas)

#### Salud del Servicio
- `GET /health` - Estado del servicio
- `GET /logistica/health` - Estado detallado del servicio
- `GET /spec` - Documentación Swagger

## 📋 Parámetros de Consulta y Filtros

### Visitas (Ventas)
- `GET /ventas/api/visitas/?estado=pendiente` - Filtrar visitas por estado
- `GET /ventas/api/visitas/vendedor/{vendedor_id}?estado=pendiente` - Visitas de vendedor con filtro de estado

### Pedidos (Ventas)
- `GET /ventas/api/pedidos/?vendedor_id={id}` - Filtrar pedidos por vendedor
- `GET /ventas/api/pedidos/?estado=confirmado` - Filtrar pedidos por estado

### Búsqueda de Productos (Ventas)
- `GET /ventas/api/pedidos/productos/buscar?q={termino}` - Buscar productos por término

### Inventario (Logística)
- `GET /logistica/api/inventario/buscar?q={termino}&limite=50` - Buscar productos con inventario
- `GET /logistica/api/inventario/producto/{id}` - Inventario específico de un producto

### Entregas (Logística)
- `GET /logistica/api/entregas/?fecha_inicio=2024-01-01&fecha_fin=2024-01-31` - Filtrar entregas por rango de fechas
- `GET /logistica/api/entregas/?fecha_inicio=2024-01-15&fecha_fin=2024-01-15` - Entregas de un día específico

