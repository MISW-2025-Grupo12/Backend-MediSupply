# MediSupply - Infraestructura como Código (IaC)

Este directorio contiene la configuración de Terraform para desplegar la infraestructura de MediSupply en Google Cloud Platform (GCP).

## 🏗️ Arquitectura

### Componentes Desplegados

- **☸️ GKE Cluster**: Kubernetes simplificado con VPC default
- **🗄️ Cloud SQL**: PostgreSQL con configuración básica
- **🔐 Workload Identity**: Autenticación segura sin claves
- **📡 Pub/Sub**: Sistema de eventos asíncronos con Workload Identity

### Recursos de Producción

| Componente | Especificación | Propósito |
|------------|----------------|-----------|
| **GKE Nodes** | e2-medium (1 vCPU, 4GB RAM) | Microservicios |
| **Cloud SQL** | db-f1-micro (1 vCPU, 0.6GB RAM) | Base de datos |
| **Storage** | 20GB SSD | Persistencia |
| **Network** | VPC default | Simplicidad |

## 🚀 Despliegue

### Prerrequisitos

1. **Google Cloud CLI** instalado y configurado
2. **Terraform** >= 1.0 instalado
3. **kubectl** instalado
4. **Docker** para construir imágenes

### Configuración Inicial

```bash
# 1. Autenticarse en Google Cloud
gcloud auth login
gcloud config set project desarrolloswcloud

# 2. Habilitar APIs necesarias (se hace automáticamente con Terraform)
gcloud services enable container.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable pubsub.googleapis.com

# 3. Configurar kubectl para Docker
gcloud auth configure-docker gcr.io
```

### Despliegue con Terraform

```bash
# 1. Navegar al directorio IaC
cd IaC

# 2. Inicializar Terraform
terraform init

# 3. Revisar el plan de despliegue
terraform plan

# 4. Aplicar la configuración
terraform apply

# 5. Configurar kubectl
gcloud container clusters get-credentials medisupply-cluster-prod --zone us-central1-a --project desarrolloswcloud
```

### Despliegue de Aplicaciones

Después de que Terraform complete la infraestructura:

```bash
# 1. Construir imágenes Docker (nombres sin prefijo "medisupply-")
docker build -f "Productos/Dockerfile" -t gcr.io/desarrolloswcloud/productos:latest "Productos" &
docker build -f "Usuarios/Dockerfile" -t gcr.io/desarrolloswcloud/usuarios:latest "Usuarios" &
docker build -f "Ventas/Dockerfile" -t gcr.io/desarrolloswcloud/ventas:latest "Ventas" &
docker build -f "Logistica/Dockerfile" -t gcr.io/desarrolloswcloud/logistica:latest "Logistica" &
wait

# 2. Subir imágenes a GCR
docker push gcr.io/desarrolloswcloud/productos:latest &
docker push gcr.io/desarrolloswcloud/usuarios:latest &
docker push gcr.io/desarrolloswcloud/ventas:latest &
docker push gcr.io/desarrolloswcloud/logistica:latest &
wait

# 3. Obtener IP de Cloud SQL y actualizar deployments
DB_IP=$(terraform output -raw db_public_ip)
echo "IP de Cloud SQL: $DB_IP"
# IMPORTANTE: Actualizar las IPs hardcodeadas en k8s/*-deployment.yaml

# 4. Desplegar aplicaciones en Kubernetes
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/productos-deployment.yaml
kubectl apply -f k8s/usuarios-deployment.yaml
kubectl apply -f k8s/ventas-deployment.yaml
kubectl apply -f k8s/logistica-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

## 📊 Monitoreo y Verificación

### Verificar Infraestructura

```bash
# Verificar cluster
kubectl get nodes
kubectl get pods -n medisupply

# Verificar servicios
kubectl get services -n medisupply

# Verificar ingress
kubectl get ingress -n medisupply
```

### Obtener URLs de Acceso

```bash
# Obtener IP del Ingress
INGRESS_IP=$(kubectl get ingress medisupply-ingress -n medisupply -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# URLs de acceso
echo "Usuarios: http://$INGRESS_IP/usuarios"
echo "Productos: http://$INGRESS_IP/productos"
echo "Ventas: http://$INGRESS_IP/ventas"
echo "Logística: http://$INGRESS_IP/logistica"
```

### Probar Endpoints

```bash
# Health checks
curl http://$INGRESS_IP/usuarios/health
curl http://$INGRESS_IP/productos/health
curl http://$INGRESS_IP/ventas/health
curl http://$INGRESS_IP/logistica/health
```

## 💰 Estimación de Costos

### Costos Mensuales Aproximados (us-central1)

| Recurso | Especificación | Costo Mensual |
|---------|----------------|---------------|
| **GKE Node (1x)** | e2-medium | ~$25 |
| **Cloud SQL** | db-f1-micro | ~$7 |
| **Storage (20GB)** | SSD | ~$4 |
| **Workload Identity** | Sin costo adicional | $0 |
| **Pub/Sub** | Topic + Subscription | ~$1 |
| **Total** | | **~$37/mes** |

### Optimizaciones de Costo

- **Auto-scaling**: Los nodos se escalan según la demanda
- **Spot instances**: Usar nodos spot para cargas de trabajo no críticas
- **Committed use discounts**: Descuentos por uso comprometido
- **Preemptible nodes**: Para entornos de desarrollo

## 🔐 Configuración de Cloud SQL Proxy

### Opción 1: Usar IP Pública (Simple pero menos seguro)
```bash
# Obtener IP de Cloud SQL
DB_IP=$(terraform output -raw db_public_ip)

# Actualizar deployments manualmente
sed -i "s/10\.74\.0\.[0-9]/$DB_IP/g" k8s/*-deployment.yaml
```

### Opción 2: Cloud SQL Proxy (Recomendado para producción)
```bash
# Obtener connection name
CONNECTION_NAME=$(terraform output -raw sql_connection_name)

# Agregar sidecar a cada deployment:
# - Agregar initContainer con gcr.io/cloudsql-docker/gce-proxy:latest
# - Configurar args con --port=5432 --instances=$CONNECTION_NAME
# - Cambiar DB_HOST a localhost:5432
# - Agregar serviceAccountName: medisupply-ksa
```

### Ejemplo de Cloud SQL Proxy en deployment
```yaml
spec:
  template:
    spec:
      serviceAccountName: medisupply-ksa
      initContainers:
      - name: cloudsql-proxy
        image: gcr.io/cloudsql-docker/gce-proxy:latest
        command:
        - "/cloud_sql_proxy"
        - "-instances=CONNECTION_NAME=tcp:5432"
        securityContext:
          runAsNonRoot: true
      containers:
      - name: productos
        env:
        - name: DB_HOST
          value: "localhost"
        - name: DB_PORT
          value: "5432"
```

## 🔧 Configuración Avanzada

### Variables Personalizables

Edita `terraform.tfvars` para personalizar:

```hcl
# Escalado
node_count   = 5        # Más nodos para mayor capacidad
machine_type = "e2-standard-4"  # Más CPU/RAM

# Base de datos
db_tier      = "db-standard-2"  # Más recursos para BD
db_disk_size = 200             # Más almacenamiento

# Red
vpc_cidr     = "10.0.0.0/8"    # Red más grande
```

### Backup y Recovery

```bash
# Backup manual de la BD
gcloud sql backups create --instance=medisupply-db-prod

# Restaurar desde backup
gcloud sql backups restore BACKUP_ID --instance=medisupply-db-prod
```

## 🧹 Limpieza

### Eliminar Infraestructura

```bash
# ⚠️ CUIDADO: Esto elimina TODOS los recursos
terraform destroy

# Eliminar imágenes Docker
gcloud container images delete gcr.io/desarrolloswcloud/productos:latest
gcloud container images delete gcr.io/desarrolloswcloud/usuarios:latest
gcloud container images delete gcr.io/desarrolloswcloud/ventas:latest
gcloud container images delete gcr.io/desarrolloswcloud/logistica:latest
```

## 🔐 Seguridad

### Configuraciones de Seguridad Implementadas

- ✅ **VPC privada** con subnets aisladas
- ✅ **Workload Identity** sin claves en el código
- ✅ **Cloud SQL** con IP privada
- ✅ **Firewall rules** restrictivas
- ✅ **Network policies** en Kubernetes
- ✅ **SSL/TLS** habilitado en Cloud SQL
- ✅ **Backup automático** con retención de 30 días

### Mejores Prácticas

1. **Rotar passwords** regularmente
2. **Monitorear logs** de acceso
3. **Actualizar imágenes** de contenedores
4. **Revisar permisos IAM** periódicamente
5. **Usar secrets management** para datos sensibles

## 📞 Soporte

Para problemas o consultas:

1. **Revisar logs**: `kubectl logs -f deployment/[servicio] -n medisupply`
2. **Verificar estado**: `kubectl describe pod [pod-name] -n medisupply`
3. **Monitorear recursos**: Google Cloud Console > Monitoring
4. **Consultar documentación**: [README-DEPLOYMENT.md](../k8s/README-DEPLOYMENT.md)

---

**Nota**: Esta configuración está optimizada para producción con recursos suficientes para manejar carga real. Para desarrollo, considera usar configuraciones más pequeñas.
