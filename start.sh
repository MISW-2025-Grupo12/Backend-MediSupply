#!/bin/bash

echo "🚀 Iniciando MediSupply - Servicio de Logística"
echo "=============================================="

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

# Verificar si Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

echo "✅ Docker y Docker Compose están disponibles"

# Construir y levantar los servicios
echo "🔨 Construyendo y levantando servicios..."
docker-compose up --build -d

# Esperar a que la base de datos esté lista
echo "⏳ Esperando a que la base de datos esté lista..."
sleep 10

# Inicializar la base de datos con datos de prueba
echo "📊 Inicializando base de datos con datos de prueba..."
docker-compose exec logistica python init_db.py

echo ""
echo "✅ Servicios iniciados correctamente!"
echo ""
echo "🌐 Servicios disponibles:"
echo "   - API de Logística: http://localhost:5002"
echo "   - Health Check: http://localhost:5002/health"
echo "   - Swagger Docs: http://localhost:5002/swagger"
echo "   - PostgreSQL: localhost:5432"
echo ""
echo "📋 Para probar la API:"
echo "   1. Importa la colección de Postman: Logistica/postman_collection.json"
echo "   2. O usa curl: curl http://localhost:5002/api/v1/entregas"
echo ""
echo "🛑 Para detener los servicios: docker-compose down"
echo ""

