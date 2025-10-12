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

### Usuarios (Puerto 5001)
- `POST /api/proveedores/` - Crear proveedor
- `POST /api/vendedores/` - Crear vendedor
- `POST /api/clientes/` - Crear cliente
- `GET /health` - Estado del servicio

### Productos (Puerto 5000)
- `POST /api/productos/` - Crear producto básico
- `POST /api/productos/con-inventario` - Crear producto con inventario
- `POST /api/productos/categorias/` - Crear categoría
- `GET /health` - Estado del servicio

### Ventas (Puerto 5002)
- `POST /api/visitas/` - Crear visita
- `POST /api/pedidos/` - Crear pedido
- `POST /api/pedidos/{id}/items` - Agregar item al pedido
- `POST /api/pedidos/{id}/confirmar` - Confirmar pedido
- `GET /health` - Estado del servicio

### Logística (Puerto 5003)
- `GET /api/inventario/` - Consultar inventario
- `POST /api/inventario/reservar` - Reservar inventario
- `GET /api/logistica/entregas/` - Consultar entregas
- `GET /health` - Estado del servicio

