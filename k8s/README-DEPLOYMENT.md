# MediSupply - Guía de Despliegue en GKE

> **NOTA IMPORTANTE**: Esta guía es para despliegue manual. Si usas Terraform (IaC/), los nombres de recursos tendrán sufijo `-prod` (ej: `medisupply-cluster-prod`, `medisupply-db-prod`). Ver [IaC/README.md](../IaC/README.md) para despliegue automatizado.

## ⚙️ Configuración Inicial

### 1. Creación de Bases de Datos PostgreSQL

#### Crear Instancia de Cloud SQL
```bash
# Crear instancia de Cloud SQL PostgreSQL
gcloud sql instances create medisupply-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1 \
  --root-password=medisupply123 \
  --storage-type=SSD \
  --storage-size=10GB \
  --storage-auto-increase \
  --backup-start-time=03:00 \
  --enable-ip-alias \
  --network=default
```

#### Crear Bases de Datos
```bash
# Crear base de datos para cada microservicio
gcloud sql databases create productos_db --instance=medisupply-db
gcloud sql databases create usuarios_db --instance=medisupply-db
gcloud sql databases create ventas_db --instance=medisupply-db
gcloud sql databases create logistica_db --instance=medisupply-db
```

#### Crear Usuarios de Base de Datos
```bash
# Crear usuarios para cada microservicio
gcloud sql users create productos_user --instance=medisupply-db --password=productos123
gcloud sql users create usuarios_user --instance=medisupply-db --password=usuarios123
gcloud sql users create ventas_user --instance=medisupply-db --password=ventas123
gcloud sql users create logistica_user --instance=medisupply-db --password=logistica123
```

#### Obtener IP Privada de la Instancia
```bash
# Obtener la IP privada de la instancia
gcloud sql instances describe medisupply-db --format="value(ipAddresses[0].ipAddress)"
```

### 2. Configuración de Conexión a Base de Datos

#### Crear Secret con Credenciales
```bash
# Crear secret con credenciales de base de datos
kubectl create secret generic db-credentials \
  --from-literal=productos-user=productos_user \
  --from-literal=productos-password=productos123 \
  --from-literal=usuarios-user=usuarios_user \
  --from-literal=usuarios-password=usuarios123 \
  --from-literal=ventas-user=ventas_user \
  --from-literal=ventas-password=ventas123 \
  --from-literal=logistica-user=logistica_user \
  --from-literal=logistica-password=logistica123 \
  -n medisupply
```

#### Configurar Cloud SQL Proxy (Opcional)
```bash
# Crear service account para Cloud SQL Proxy
gcloud iam service-accounts create cloudsql-proxy \
  --display-name="Cloud SQL Proxy Service Account"

# Asignar permisos
gcloud projects add-iam-policy-binding desarrolloswcloud \
  --member="serviceAccount:cloudsql-proxy@desarrolloswcloud.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

# Crear clave para Cloud SQL Proxy
gcloud iam service-accounts keys create cloudsql-proxy-key.json \
  --iam-account=cloudsql-proxy@desarrolloswcloud.iam.gserviceaccount.com

# Crear secret para Cloud SQL Proxy
kubectl create secret generic cloudsql-proxy-credentials \
  --from-file=service-account-key.json=cloudsql-proxy-key.json \
  -n medisupply
```

### 3. Autenticación en Google Cloud
```bash
# Iniciar sesión en Google Cloud
gcloud auth login

# Configurar proyecto por defecto
gcloud config set project desarrolloswcloud

# Habilitar APIs necesarias
gcloud services enable container.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 4. Configurar Docker para GCR
```bash
# Configurar autenticación para Google Container Registry
gcloud auth configure-docker gcr.io
```

## 🏗️ Creación del Cluster GKE

### Opción 1: Cluster con Workload Identity (Recomendado)
```bash
# Crear cluster con Workload Identity habilitado
gcloud container clusters create medisupply-cluster \
  --zone=us-central1-a \
  --num-nodes=2 \
  --enable-workload-identity \
  --workload-pool=desarrolloswcloud.svc.id.goog \
  --scopes="https://www.googleapis.com/auth/cloud-platform"
```

### Opción 2: Cluster Básico (Alternativa)
```bash
# Crear cluster básico
gcloud container clusters create medisupply-cluster \
  --zone=us-central1-a \
  --num-nodes=2 \
  --scopes="https://www.googleapis.com/auth/pubsub,https://www.googleapis.com/auth/cloud-platform"
```

### Configurar kubectl
```bash
# Obtener credenciales del cluster
gcloud container clusters get-credentials medisupply-cluster \
  --zone=us-central1-a \
  --project=desarrolloswcloud

# Verificar conexión
kubectl get nodes
```

## 🔐 Configuración de Workload Identity

### 1. Crear Service Account para Workload Identity
```bash
# Crear service account
gcloud iam service-accounts create medisupply-workload-identity \
  --display-name="MediSupply Workload Identity"

# Asignar permisos necesarios
gcloud projects add-iam-policy-binding desarrolloswcloud \
  --member="serviceAccount:medisupply-workload-identity@desarrolloswcloud.iam.gserviceaccount.com" \
  --role="roles/pubsub.editor"

gcloud projects add-iam-policy-binding desarrolloswcloud \
  --member="serviceAccount:medisupply-workload-identity@desarrolloswcloud.iam.gserviceaccount.com" \
  --role="roles/pubsub.subscriber"

gcloud projects add-iam-policy-binding desarrolloswcloud \
  --member="serviceAccount:medisupply-workload-identity@desarrolloswcloud.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher"
```

### 2. Crear Kubernetes Service Account
```bash
# Crear service account en Kubernetes
kubectl create serviceaccount medisupply-ksa -n medisupply
```

### 3. Configurar Workload Identity Binding
```bash
# Obtener el nombre del service account del nodo
gcloud container clusters describe medisupply-cluster \
  --zone=us-central1-a \
  --format="value(nodeConfig.serviceAccount)"

# Crear binding (reemplazar SERVICE_ACCOUNT_NODE con el valor anterior)
gcloud iam service-accounts add-iam-policy-binding \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:desarrolloswcloud.svc.id.goog[medisupply/medisupply-ksa]" \
  medisupply-workload-identity@desarrolloswcloud.iam.gserviceaccount.com

# Anotar el service account de Kubernetes
kubectl annotate serviceaccount medisupply-ksa \
  -n medisupply \
  iam.gke.io/gcp-service-account=medisupply-workload-identity@desarrolloswcloud.iam.gserviceaccount.com
```

## 📦 Configuración de Google Cloud Storage

### Bucket de Evidencias de Visitas

#### 1. Crear Bucket (Si no existe)
```bash
# Crear bucket para evidencias
gcloud storage buckets create gs://evidencias-g12 \
  --location=US-EAST1 \
  --storage-class=NEARLINE \
  --uniform-bucket-level-access \
  --project=desarrolloswcloud
```

#### 2. Configurar Permisos
```bash
# Dar permisos al service account de Workload Identity
gcloud storage buckets add-iam-policy-binding gs://evidencias-g12 \
  --member="serviceAccount:medisupply-workload-prod@desarrolloswcloud.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Verificar permisos
gcloud storage buckets get-iam-policy gs://evidencias-g12
```

# Aplicar configuración
gcloud storage buckets update gs://evidencias-g12 --lifecycle-file=lifecycle.json
```

**Permisos Requeridos:**
- ✅ `storage.objects.create` - Crear evidencias
- ✅ `storage.objects.get` - Leer evidencias
- ✅ `storage.objects.update` - Actualizar evidencias
- ✅ `storage.objects.delete` - Eliminar evidencias

**Uso:**
- El servicio de Ventas usa este bucket para almacenar evidencias de visitas
- Las evidencias se suben mediante el endpoint: `POST /ventas/api/visitas/{visita_id}/evidencias`

## 🐳 Construcción de Imágenes Docker

### Construir Imágenes en Paralelo
```bash
# Navegar al directorio raíz del proyecto
cd "C:\Users\Usuario\OneDrive\Documentos\Maestria Uniandes\Proyecto 2\Backend-MediSupply"

# Construir todas las imágenes en paralelo (usar rutas absolutas)
docker build -f "Auth-Service/Dockerfile" -t gcr.io/desarrolloswcloud/auth-service:latest "Auth-Service" &
docker build -f "Productos/Dockerfile" -t gcr.io/desarrolloswcloud/productos:latest "Productos" &
docker build -f "Usuarios/Dockerfile" -t gcr.io/desarrolloswcloud/usuarios:latest "Usuarios" &
docker build -f "Ventas/Dockerfile" -t gcr.io/desarrolloswcloud/ventas:latest "Ventas" &
docker build -f "Logistica/Dockerfile" -t gcr.io/desarrolloswcloud/logistica:latest "Logistica" &

# Esperar a que terminen todas las construcciones
wait
```

### Verificar Construcción
```bash
# Verificar que las imágenes se construyeron correctamente
docker images | grep medisupply
```

### Subir Imágenes a GCR
```bash
# Subir todas las imágenes en paralelo
docker push gcr.io/desarrolloswcloud/auth-service:latest &
docker push gcr.io/desarrolloswcloud/productos:latest &
docker push gcr.io/desarrolloswcloud/usuarios:latest &
docker push gcr.io/desarrolloswcloud/ventas:latest &
docker push gcr.io/desarrolloswcloud/logistica:latest &

# Esperar a que terminen todas las subidas
wait
```

### Verificar Subida
```bash
# Verificar que las imágenes se subieron correctamente
gcloud container images list --repository=gcr.io/desarrolloswcloud
```

## ☸️ Despliegue en Kubernetes

### 1. Crear Namespace
```bash
# Aplicar namespace
kubectl apply -f k8s/namespace.yaml
```

### 2. Crear ConfigMap y Secrets
```bash
# Aplicar configuración
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
```

#### Configurar Variables de Entorno
```bash
# Crear ConfigMap con configuración de la aplicación
kubectl create configmap app-config \
  --from-literal=FLASK_ENV=production \
  --from-literal=PYTHONPATH=/app/src \
  --from-literal=DB_PORT=5432 \
  --from-literal=PRODUCTOS_DB_NAME=productos_db \
  --from-literal=USUARIOS_DB_NAME=usuarios_db \
  --from-literal=VENTAS_DB_NAME=ventas_db \
  --from-literal=LOGISTICA_DB_NAME=logistica_db \
  --from-literal=GCP_PROJECT_ID=desarrolloswcloud \
  -n medisupply
```

#### Verificar Configuración
```bash
# Verificar ConfigMap
kubectl get configmap app-config -n medisupply -o yaml

# Verificar Secrets
kubectl get secret db-credentials -n medisupply -o yaml
```

### 3. Configurar CORS (BackendConfig)
```bash
# Aplicar configuración de CORS para GKE
kubectl apply -f k8s/backend-config.yaml

# Verificar BackendConfig
kubectl get backendconfig medisupply-cors-config -n medisupply -o yaml
```

**Configuración de CORS incluida:**
- ✅ Dominios: `api.medisupplyg4.online`, `medisupplyg4.online`, localhost
- ✅ Métodos: GET, POST, PUT, PATCH, DELETE, OPTIONS
- ✅ Headers: Content-Type, Authorization, Accept, Origin, X-Requested-With
- ✅ Credentials: Habilitado
- ✅ Timeout: 60s (coherente con nginx.conf)

### 4. Desplegar Servicios
```bash
# Desplegar Auth-Service (PRIMERO - requerido para autenticación)
kubectl apply -f k8s/auth-configmap.yaml
kubectl apply -f k8s/auth-deployment.yaml

# Desplegar todos los microservicios
kubectl apply -f k8s/productos-deployment.yaml
kubectl apply -f k8s/usuarios-deployment.yaml
kubectl apply -f k8s/ventas-deployment.yaml
kubectl apply -f k8s/logistica-deployment.yaml
```

> **Nota**: Todos los Services incluyen la anotación `cloud.google.com/backend-config` que referencia el BackendConfig de CORS.

### 5. Verificar Despliegue
```bash
# Verificar pods
kubectl get pods -n medisupply

# Verificar servicios
kubectl get services -n medisupply

# Verificar logs si hay problemas
kubectl logs -f deployment/logistica-deployment -n medisupply
```

## 🌐 Configuración del Ingress

### 1. Crear IP Estática
```bash
# Crear IP estática global
gcloud compute addresses create medisupply-ip --global

# Verificar IP creada
gcloud compute addresses list --filter="name=medisupply-ip"
```

### 2. Aplicar Ingress
```bash
# Aplicar configuración del Ingress
kubectl apply -f k8s/ingress.yaml

# Verificar estado del Ingress
kubectl get ingress -n medisupply
```

### 3. Esperar Configuración (IMPORTANTE)
```bash
# El Ingress tarda aproximadamente 10 minutos en configurarse completamente
kubectl describe ingress medisupply-ingress -n medisupply
```

## ✅ Verificación del Despliegue

### 1. Verificar Estado de los Pods
```bash
# Todos los pods deben estar en estado "Running"
kubectl get pods -n medisupply
```

### 2. Verificar Ingress
```bash
# El Ingress debe tener una ADDRESS asignada
kubectl get ingress -n medisupply
```

### 3. Probar Endpoints
```bash
# Obtener la IP del Ingress
INGRESS_IP=$(kubectl get ingress medisupply-ingress -n medisupply -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Probar endpoints básicos
curl http://$INGRESS_IP/auth/health
curl http://$INGRESS_IP/usuarios/health
curl http://$INGRESS_IP/productos/health
curl http://$INGRESS_IP/ventas/health
curl http://$INGRESS_IP/logistica/health
```

### 4. Probar con Port Forward (Alternativa)
```bash
# Si el Ingress no está listo, usar port-forward para probar
kubectl port-forward service/usuarios-service 5001:5001 -n medisupply &
kubectl port-forward service/productos-service 5000:5000 -n medisupply &
kubectl port-forward service/ventas-service 5002:5002 -n medisupply &
kubectl port-forward service/logistica-service 5003:5003 -n medisupply &

# Probar endpoints locales
curl http://localhost:5001/
curl http://localhost:5000/
curl http://localhost:5002/
curl http://localhost:5003/
```


## 📊 Estructura de Archivos

```
k8s/
├── namespace.yaml                 # Namespace del proyecto
├── configmap.yaml                 # Configuración general de la aplicación
├── secret.yaml                    # Credenciales de BD y JWT Secret
├── backend-config.yaml            # 🌐 Configuración CORS para GKE
├── auth-configmap.yaml            # ⭐ ConfigMap con permisos de autorización
├── auth-deployment.yaml           # ⭐ Deployment y Service de Auth
├── productos-deployment.yaml      # Deployment y Service de Productos
├── usuarios-deployment.yaml       # Deployment y Service de Usuarios
├── ventas-deployment.yaml         # Deployment y Service de Ventas
├── logistica-deployment.yaml      # Deployment y Service de Logística
├── ingress.yaml                   # Configuración del Ingress
├── ssl-certificate.yaml           # Certificado SSL para HTTPS
└── README-DEPLOYMENT.md           # Esta guía
```

## 🔗 URLs de Acceso

Una vez desplegado correctamente, la aplicación estará disponible en:

### URLs Principales
- **🏠 Página Principal**: `http://[INGRESS_IP]/`
- **👥 Usuarios**: `http://[INGRESS_IP]/usuarios`
- **📦 Productos**: `http://[INGRESS_IP]/productos`
- **🛒 Ventas**: `http://[INGRESS_IP]/ventas`
- **🚚 Logística**: `http://[INGRESS_IP]/logistica`

### URLs de Salud
- **👥 Usuarios Health**: `http://[INGRESS_IP]/usuarios/health`
- **📦 Productos Health**: `http://[INGRESS_IP]/productos/health`
- **🛒 Ventas Health**: `http://[INGRESS_IP]/ventas/health`
- **🚚 Logística Health**: `http://[INGRESS_IP]/logistica/health`

### URLs de API
- **👥 Usuarios API**: `http://[INGRESS_IP]/usuarios/api/`
- **📦 Productos API**: `http://[INGRESS_IP]/productos/api/`
- **🛒 Ventas API**: `http://[INGRESS_IP]/ventas/api/`
- **🚚 Logística API**: `http://[INGRESS_IP]/logistica/api/`

### URLs de Port Forward (Desarrollo)
- **👥 Usuarios**: `http://localhost:5001/`
- **📦 Productos**: `http://localhost:5000/`
- **🛒 Ventas**: `http://localhost:5002/`
- **🚚 Logística**: `http://localhost:5003/`

## 🧹 Limpieza

Para eliminar todos los recursos:

```bash
# Eliminar Ingress
kubectl delete ingress medisupply-ingress -n medisupply

# Eliminar deployments y services
kubectl delete -f k8s/

# Eliminar namespace
kubectl delete namespace medisupply

# Eliminar cluster
gcloud container clusters delete medisupply-cluster --zone=us-central1-a

# Eliminar IP estática
gcloud compute addresses delete medisupply-ip --global

# Eliminar instancia de Cloud SQL (CUIDADO: Esto elimina TODOS los datos)
gcloud sql instances delete medisupply-db

# Eliminar service accounts
gcloud iam service-accounts delete medisupply-workload-identity@desarrolloswcloud.iam.gserviceaccount.com
gcloud iam service-accounts delete cloudsql-proxy@desarrolloswcloud.iam.gserviceaccount.com
gcloud iam service-accounts delete medisupply-pubsub@desarrolloswcloud.iam.gserviceaccount.com
```

## 📝 Notas Importantes

1. **Tiempo de Configuración**: El Ingress tarda ~10 minutos en estar completamente funcional
2. **Health Checks**: Todos los servicios deben responder en la ruta raíz `/`
3. **Permisos**: Workload Identity es más seguro que usar secrets con claves JSON
4. **Paralelización**: Construir y subir imágenes en paralelo ahorra tiempo significativo
5. **Monitoreo**: Siempre verificar logs cuando hay problemas
6. **Bases de Datos**: Cloud SQL tarda ~5-10 minutos en crearse completamente
7. **Conectividad**: Asegurar que la instancia de Cloud SQL esté en la misma región que el cluster GKE
8. **Seguridad**: Usar IP privada para Cloud SQL y configurar autorización de red apropiada
9. **Rutas**: Los blueprints deben definir rutas completas para evitar duplicación de prefijos
10. **Comunicación**: Usar URLs internas de Kubernetes para comunicación entre servicios
11. **Testing**: Usar port-forward para probar servicios antes de configurar el Ingress

## Testing y Validación

### Comandos de Prueba Rápida
```bash
# Verificar estado general
kubectl get all -n medisupply

# Probar salud de servicios
kubectl port-forward service/usuarios-service 5001:5001 -n medisupply &
curl http://localhost:5001/usuarios/health

# Verificar logs de errores
kubectl logs -f deployment/logistica-deployment -n medisupply | grep -i error
```

### Colecciones de Postman
- **MediSupply - Colección**: Para pruebas manuales de endpoints individuales
- **MediSupply - Flujo Completo**: Para pruebas automatizadas del flujo completo

### Variables de Entorno para Postman
- `base_url`: `http://[INGRESS_IP]` (producción) o `http://localhost` (desarrollo)
- `base_url_usuarios`: `http://[INGRESS_IP]:5001` o `http://localhost:5001`
- `base_url_productos`: `http://[INGRESS_IP]:5000` o `http://localhost:5000`
- `base_url_ventas`: `http://[INGRESS_IP]:5002` o `http://localhost:5002`
- `base_url_logistica`: `http://[INGRESS_IP]:5003` o `http://localhost:5003`

