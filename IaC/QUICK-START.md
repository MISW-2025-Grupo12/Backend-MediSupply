# 🚀 MediSupply - Despliegue Rápido

Guía rápida para desplegar MediSupply en producción usando Terraform.

## ⚡ Despliegue en 3 Pasos

### 1. Prerrequisitos
```bash
# Instalar herramientas (si no las tienes)
# - Google Cloud CLI
# - Terraform >= 1.0
# - kubectl
# - Docker
```

### 2. Configurar Google Cloud
```bash
# Autenticarse
gcloud auth login
gcloud config set project desarrolloswcloud

# Habilitar APIs
gcloud services enable container.googleapis.com compute.googleapis.com sqladmin.googleapis.com pubsub.googleapis.com containerregistry.googleapis.com
```

### 3. Desplegar Todo
```bash
# Opción 1: Script automatizado (recomendado)
cd IaC
.\deploy.ps1 all

# Opción 2: Manual
terraform init
terraform apply
# ... seguir pasos del README completo
```

## 📊 Recursos Creados

| Componente | Especificación | Costo Mensual |
|------------|----------------|---------------|
| **GKE Cluster** | 1x e2-medium | ~$25 |
| **Cloud SQL** | db-f1-micro, 20GB SSD | ~$7 |
| **Storage** | 20GB SSD | ~$4 |
| **Pub/Sub** | Topic + Subscription | ~$1 |
| **Total** | | **~$37/mes** |

## 🌐 Acceso a la Aplicación

Después del despliegue, la aplicación estará disponible en:

```bash
# Obtener IP del Ingress
INGRESS_IP=$(kubectl get ingress medisupply-ingress -n medisupply -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# URLs de acceso
echo "Usuarios: http://$INGRESS_IP/usuarios"
echo "Productos: http://$INGRESS_IP/productos"
echo "Ventas: http://$INGRESS_IP/ventas"
echo "Logística: http://$INGRESS_IP/logistica"
```

## 🏥 Health Checks

```bash
curl http://$INGRESS_IP/usuarios/health
curl http://$INGRESS_IP/productos/health
curl http://$INGRESS_IP/ventas/health
curl http://$INGRESS_IP/logistica/health
```

## 🔧 Comandos Útiles

```bash
# Ver estado
kubectl get pods -n medisupply
kubectl get services -n medisupply
kubectl get ingress -n medisupply

# Ver logs
kubectl logs -f deployment/productos-deployment -n medisupply

# Escalar servicios
kubectl scale deployment productos-deployment --replicas=3 -n medisupply
```

## 🧹 Limpieza

```bash
# Eliminar todo
cd IaC
terraform destroy

# Eliminar imágenes
gcloud container images delete gcr.io/desarrolloswcloud/productos:latest
gcloud container images delete gcr.io/desarrolloswcloud/usuarios:latest
gcloud container images delete gcr.io/desarrolloswcloud/ventas:latest
gcloud container images delete gcr.io/desarrolloswcloud/logistica:latest
```

## 🆘 Troubleshooting

### Problemas Comunes

1. **Pods no inician**
   ```bash
   kubectl describe pod <pod-name> -n medisupply
   kubectl logs <pod-name> -n medisupply
   ```

2. **Ingress sin IP**
   ```bash
   kubectl describe ingress medisupply-ingress -n medisupply
   # Esperar ~10 minutos para asignación de IP
   ```

3. **Error de conexión a BD**
   ```bash
   # Verificar IP de Cloud SQL
   terraform output db_private_ip
   # Actualizar deployments si es necesario
   ```

4. **Imágenes no se suben**
   ```bash
   gcloud auth configure-docker gcr.io
   docker login gcr.io
   ```

### Logs Importantes

```bash
# Logs de Terraform
terraform show

# Logs de aplicaciones
kubectl logs -f deployment/productos-deployment -n medisupply
kubectl logs -f deployment/usuarios-deployment -n medisupply
kubectl logs -f deployment/ventas-deployment -n medisupply
kubectl logs -f deployment/logistica-deployment -n medisupply

# Logs de eventos
kubectl get events -n medisupply --sort-by='.lastTimestamp'
```

## 📞 Soporte

- **Documentación completa**: [README.md](README.md)
- **Configuración K8s**: [../k8s/README-DEPLOYMENT.md](../k8s/README-DEPLOYMENT.md)
- **Troubleshooting**: Revisar logs y eventos de Kubernetes

---

**Tiempo estimado de despliegue**: 15-20 minutos
**Costo mensual**: ~$37 USD
**Disponibilidad**: 99.9% (con configuración de producción)
