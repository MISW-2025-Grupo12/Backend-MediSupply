# MediSupply - Script de Despliegue en PowerShell
# Este script automatiza el despliegue de la infraestructura y aplicaciones

param(
    [Parameter(Position=0)]
    [ValidateSet("all", "infra", "apps", "verify", "clean", "help")]
    [string]$Action = "all"
)

# Configuración de colores para PowerShell
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    White = "White"
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Colors.Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Colors.Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Colors.Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Colors.Red
}

# Función para verificar prerrequisitos
function Test-Prerequisites {
    Write-Info "Verificando prerrequisitos..."
    
    # Verificar gcloud
    if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
        Write-Error "gcloud CLI no está instalado"
        exit 1
    }
    
    # Verificar terraform
    if (-not (Get-Command terraform -ErrorAction SilentlyContinue)) {
        Write-Error "Terraform no está instalado"
        exit 1
    }
    
    # Verificar kubectl
    if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
        Write-Error "kubectl no está instalado"
        exit 1
    }
    
    # Verificar docker
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker no está instalado"
        exit 1
    }
    
    Write-Success "Todos los prerrequisitos están instalados"
}

# Función para configurar Google Cloud
function Setup-GoogleCloud {
    Write-Info "Configurando Google Cloud..."
    
    # Verificar autenticación
    $authAccounts = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
    if (-not $authAccounts) {
        Write-Warning "No hay sesión activa en gcloud, iniciando autenticación..."
        gcloud auth login
    }
    
    # Configurar Application Default Credentials
    Write-Info "Configurando Application Default Credentials..."
    $adcCheck = gcloud auth application-default print-access-token 2>$null
    if (-not $adcCheck) {
        Write-Warning "Application Default Credentials no configuradas..."
        Write-Info "Iniciando configuración interactiva de ADC..."
        Write-Host "Se abrirá una ventana del navegador para autenticación." -ForegroundColor Yellow
        Write-Host "Presiona Enter para continuar..." -ForegroundColor Yellow
        Read-Host
        gcloud auth application-default login
    }
    
    # Configurar proyecto
    gcloud config set project desarrolloswcloud
    
    # Habilitar APIs
    Write-Info "Habilitando APIs necesarias..."
    $apis = @(
        "container.googleapis.com",
        "compute.googleapis.com",
        "sqladmin.googleapis.com",
        "pubsub.googleapis.com",
        "containerregistry.googleapis.com",
        "iam.googleapis.com",
        "cloudresourcemanager.googleapis.com",
        "servicenetworking.googleapis.com"
    )
    
    foreach ($api in $apis) {
        gcloud services enable $api
    }
    
    # Configurar Docker para GCR
    gcloud auth configure-docker gcr.io
    
    Write-Success "Google Cloud configurado correctamente"
}

# Función para desplegar infraestructura con Terraform
function Deploy-Infrastructure {
    Write-Info "Desplegando infraestructura con Terraform..."
    
    # Inicializar Terraform
    Write-Info "Inicializando Terraform..."
    terraform init
    
    # Validar configuración
    Write-Info "Validando configuración de Terraform..."
    terraform validate
    
    # Planificar despliegue
    Write-Info "Planificando despliegue..."
    terraform plan
    
    # Aplicar configuración
    Write-Info "Aplicando configuración de infraestructura..."
    $applyResult = terraform apply -auto-approve 2>&1
    
    # Verificar si hay recursos que necesitan ser importados (solo si el apply inicial falla)
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "El apply inicial falló, verificando si hay recursos existentes..."
        
        # Intentar importar recursos que pueden existir
        try {
            Write-Info "Importando recursos existentes si es necesario..."
            terraform import google_pubsub_subscription.medisupply_subscription projects/desarrolloswcloud/subscriptions/medisupply-subscription-prod 2>$null
            terraform import kubernetes_service_account.medisupply_ksa medisupply/medisupply-ksa 2>$null
            terraform import google_service_account_iam_member.workload_identity_binding "projects/desarrolloswcloud/serviceAccounts/medisupply-workload-prod@desarrolloswcloud.iam.gserviceaccount.com roles/iam.workloadIdentityUser serviceAccount:desarrolloswcloud.svc.id.goog[medisupply/medisupply-ksa]" 2>$null
            terraform import google_compute_global_address.medisupply_static_ip projects/desarrolloswcloud/global/addresses/medisupply-ip 2>$null
            
            # Aplicar cambios adicionales si hay importaciones
            Write-Info "Aplicando configuración después de importaciones..."
            terraform apply -auto-approve
        }
        catch {
            Write-Error "Error durante la importación de recursos existentes"
            Write-Info "Ejecuta manualmente: terraform import <recurso> <id>"
            exit 1
        }
    } else {
        Write-Success "Infraestructura aplicada correctamente"
    }
    
    # Obtener outputs importantes
    $clusterName = terraform output -raw cluster_name
    $zone = terraform output -raw cluster_location
    $connectionName = terraform output -raw db_connection_name
    
    Write-Success "Infraestructura desplegada correctamente"
    Write-Info "Cluster: $clusterName en zona: $zone"
    Write-Info "Connection name para Cloud SQL Proxy: $connectionName"
    
    # Los deployments usarán Cloud SQL Proxy
    Write-Info "Los deployments de k8s están configurados para usar Cloud SQL Proxy (localhost:5432)"
}

# Función para verificar configuración de Cloud SQL Proxy
function Verify-CloudSQLProxyConfig {
    Write-Info "Verificando configuración de Cloud SQL Proxy..."
    
    # Navegar al directorio k8s
    $k8sDir = Join-Path (Split-Path -Parent $PSScriptRoot) "k8s"
    
    # Verificar que los deployments tengan Cloud SQL Proxy configurado
    $deployments = @("productos", "usuarios", "ventas", "logistica")
    $allConfigured = $true
    
    foreach ($deployment in $deployments) {
        $deploymentFile = Join-Path $k8sDir "$deployment-deployment.yaml"
        
        if (Test-Path $deploymentFile) {
            $content = Get-Content $deploymentFile -Raw
            
            # Verificar que tenga Cloud SQL Proxy
            if ($content -match "cloud-sql-proxy") {
                Write-Success "$deployment tiene Cloud SQL Proxy configurado"
            } else {
                Write-Warning "$deployment NO tiene Cloud SQL Proxy configurado"
                $allConfigured = $false
            }
            
            # Verificar que DB_HOST sea localhost
            if ($content -match 'DB_HOST.*localhost') {
                Write-Success "$deployment configurado para usar localhost"
            } else {
                Write-Warning "$deployment NO está configurado para usar localhost"
                $allConfigured = $false
            }
        }
    }
    
    if ($allConfigured) {
        Write-Success "Todos los deployments están configurados correctamente para Cloud SQL Proxy"
    } else {
        Write-Error "Algunos deployments necesitan configuración adicional"
        exit 1
    }
}

# Función para configurar kubectl
function Setup-Kubectl {
    Write-Info "Configurando kubectl..."
    
    # Obtener credenciales del cluster
    gcloud container clusters get-credentials medisupply-cluster-prod --zone us-central1-a --project desarrolloswcloud
    
    # Verificar conexión
    try {
        kubectl cluster-info | Out-Null
        Write-Success "kubectl configurado correctamente"
    }
    catch {
        Write-Error "Error configurando kubectl"
        exit 1
    }
}

# Función para construir y subir imágenes Docker
function Build-AndPush-Images {
    Write-Info "Construyendo y subiendo imágenes Docker..."
    
    # Navegar al directorio raíz del proyecto (desde IaC/)
    $projectRoot = Split-Path -Parent $PSScriptRoot
    Set-Location $projectRoot
    Write-Info "Navegando al directorio raíz: $projectRoot"
    
    # Construir todas las imágenes
    Write-Info "Construyendo imágenes..."
    $buildJobs = @()
    
    $buildJobs += Start-Job -ScriptBlock { Set-Location $using:projectRoot; docker build -f "Productos/Dockerfile" -t gcr.io/desarrolloswcloud/productos:latest "Productos" }
    $buildJobs += Start-Job -ScriptBlock { Set-Location $using:projectRoot; docker build -f "Usuarios/Dockerfile" -t gcr.io/desarrolloswcloud/usuarios:latest "Usuarios" }
    $buildJobs += Start-Job -ScriptBlock { Set-Location $using:projectRoot; docker build -f "Ventas/Dockerfile" -t gcr.io/desarrolloswcloud/ventas:latest "Ventas" }
    $buildJobs += Start-Job -ScriptBlock { Set-Location $using:projectRoot; docker build -f "Logistica/Dockerfile" -t gcr.io/desarrolloswcloud/logistica:latest "Logistica" }
    
    # Esperar a que terminen todas las construcciones
    $buildJobs | Wait-Job | Receive-Job
    $buildJobs | Remove-Job
    
    Write-Success "Imágenes construidas correctamente"
    
    # Subir todas las imágenes
    Write-Info "Subiendo imágenes a Google Container Registry..."
    $pushJobs = @()
    
    $pushJobs += Start-Job -ScriptBlock { docker push gcr.io/desarrolloswcloud/productos:latest }
    $pushJobs += Start-Job -ScriptBlock { docker push gcr.io/desarrolloswcloud/usuarios:latest }
    $pushJobs += Start-Job -ScriptBlock { docker push gcr.io/desarrolloswcloud/ventas:latest }
    $pushJobs += Start-Job -ScriptBlock { docker push gcr.io/desarrolloswcloud/logistica:latest }
    
    # Esperar a que terminen todas las subidas
    $pushJobs | Wait-Job | Receive-Job
    $pushJobs | Remove-Job
    
    Write-Success "Imágenes subidas correctamente"
}

# Función para desplegar aplicaciones en Kubernetes
function Deploy-Applications {
    Write-Info "Desplegando aplicaciones en Kubernetes..."
    
    # Navegar al directorio k8s
    $k8sDir = Join-Path (Split-Path -Parent $PSScriptRoot) "k8s"
    Set-Location $k8sDir
    
    # Verificar configuración de Cloud SQL Proxy antes del despliegue
    Verify-CloudSQLProxyConfig
    
    # Crear namespace
    kubectl apply -f namespace.yaml
    
    # Crear configuración
    kubectl apply -f configmap.yaml
    kubectl apply -f secret.yaml
    
    # Desplegar servicios
    kubectl apply -f productos-deployment.yaml
    kubectl apply -f usuarios-deployment.yaml
    kubectl apply -f ventas-deployment.yaml
    kubectl apply -f logistica-deployment.yaml
    
    # Desplegar ingress
    kubectl apply -f ingress.yaml
    
    Write-Success "Aplicaciones desplegadas correctamente"
    
    # Verificar que los pods estén iniciando
    Write-Info "Verificando estado inicial de los pods..."
    Start-Sleep -Seconds 10
    kubectl get pods -n medisupply
}

# Función para verificar el despliegue
function Verify-Deployment {
    Write-Info "Verificando despliegue..."
    
    # Verificar estado de los pods
    Write-Info "Estado de los pods:"
    kubectl get pods -n medisupply
    
    # Verificar que Cloud SQL Proxy esté funcionando
    Write-Info "Verificando Cloud SQL Proxy en los pods..."
    $pods = kubectl get pods -n medisupply -o name
    foreach ($pod in $pods) {
        $podName = $pod -replace "pod/", ""
        Write-Info "Verificando $podName..."
        
        # Verificar contenedores en el pod
        $containers = kubectl get pod $podName -n medisupply -o jsonpath='{.spec.containers[*].name}'
        if ($containers -match "cloud-sql-proxy") {
            Write-Success "  ✓ Cloud SQL Proxy configurado en $podName"
        } else {
            Write-Warning "  ✗ Cloud SQL Proxy NO configurado en $podName"
        }
    }
    
    # Esperar a que los pods estén listos (con timeout más largo para Cloud SQL Proxy)
    Write-Info "Esperando a que los pods estén listos (esto puede tomar varios minutos)..."
    kubectl wait --for=condition=ready pod -l app=productos -n medisupply --timeout=600s
    kubectl wait --for=condition=ready pod -l app=usuarios -n medisupply --timeout=600s
    kubectl wait --for=condition=ready pod -l app=ventas -n medisupply --timeout=600s
    kubectl wait --for=condition=ready pod -l app=logistica -n medisupply --timeout=600s
    
    # Verificar estado final de los pods
    Write-Info "Estado final de los pods:"
    kubectl get pods -n medisupply
    
    # Verificar servicios
    Write-Info "Estado de los servicios:"
    kubectl get services -n medisupply
    
    # Verificar ingress
    Write-Info "Estado del ingress:"
    kubectl get ingress -n medisupply
    
    # Obtener IP del ingress
    try {
        $ingressIP = kubectl get ingress medisupply-ingress -n medisupply -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
        
        if ($ingressIP) {
            Write-Success "Despliegue completado exitosamente!"
            Write-Host ""
            Write-Host "🌐 URLs de acceso:" -ForegroundColor $Colors.Green
            Write-Host "   Usuarios:   http://$ingressIP/usuarios" -ForegroundColor $Colors.White
            Write-Host "   Productos:  http://$ingressIP/productos" -ForegroundColor $Colors.White
            Write-Host "   Ventas:     http://$ingressIP/ventas" -ForegroundColor $Colors.White
            Write-Host "   Logística:  http://$ingressIP/logistica" -ForegroundColor $Colors.White
            Write-Host ""
            Write-Host "🏥 Health checks:" -ForegroundColor $Colors.Green
            Write-Host "   curl http://$ingressIP/usuarios/health" -ForegroundColor $Colors.White
            Write-Host "   curl http://$ingressIP/productos/health" -ForegroundColor $Colors.White
            Write-Host "   curl http://$ingressIP/ventas/health" -ForegroundColor $Colors.White
            Write-Host "   curl http://$ingressIP/logistica/health" -ForegroundColor $Colors.White
            Write-Host ""
            Write-Host "🔧 Información técnica:" -ForegroundColor $Colors.Green
            Write-Host "   • Cloud SQL Proxy: localhost:5432 en cada pod" -ForegroundColor $Colors.White
            Write-Host "   • Workload Identity configurado" -ForegroundColor $Colors.White
            Write-Host "   • Conexión segura a Cloud SQL" -ForegroundColor $Colors.White
        }
        else {
            Write-Warning "El ingress aún no tiene IP asignada. Puede tardar unos minutos."
            Write-Info "Verifica el estado con: kubectl get ingress -n medisupply"
        }
    }
    catch {
        Write-Warning "No se pudo obtener la IP del ingress"
    }
}

# Función para limpiar recursos
function Clean-Resources {
    Write-Warning "⚠️  ADVERTENCIA: Esta operación eliminará TODOS los recursos de MediSupply"
    Write-Host "Esto incluye:" -ForegroundColor $Colors.Yellow
    Write-Host "  • Cluster GKE y todos los nodos" -ForegroundColor $Colors.Yellow
    Write-Host "  • Cloud SQL y todas las bases de datos" -ForegroundColor $Colors.Yellow
    Write-Host "  • Todas las imágenes Docker en GCR" -ForegroundColor $Colors.Yellow
    Write-Host "  • IP estática y otros recursos" -ForegroundColor $Colors.Yellow
    Write-Host ""
    
    $confirmation = Read-Host "¿Estás seguro de que quieres continuar? Escribe 'ELIMINAR' para confirmar"
    if ($confirmation -ne "ELIMINAR") {
        Write-Info "Operación cancelada"
        return
    }
    
    Write-Info "Iniciando limpieza de recursos..."
    
    # Eliminar recursos de Kubernetes
    Write-Info "Eliminando recursos de Kubernetes..."
    $k8sDir = Join-Path (Split-Path -Parent $PSScriptRoot) "k8s"
    if (Test-Path $k8sDir) {
        Set-Location $k8sDir
        kubectl delete -f ingress.yaml 2>$null
        kubectl delete -f productos-deployment.yaml 2>$null
        kubectl delete -f usuarios-deployment.yaml 2>$null
        kubectl delete -f ventas-deployment.yaml 2>$null
        kubectl delete -f logistica-deployment.yaml 2>$null
        kubectl delete -f configmap.yaml 2>$null
        kubectl delete -f secret.yaml 2>$null
        kubectl delete -f namespace.yaml 2>$null
    }
    
    # Eliminar infraestructura con Terraform
    Write-Info "Eliminando infraestructura con Terraform..."
    Set-Location (Split-Path -Parent $PSScriptRoot)
    terraform destroy -auto-approve
    
    # Limpiar imágenes Docker
    Write-Info "Eliminando imágenes Docker..."
    $images = @("productos", "usuarios", "ventas", "logistica")
    foreach ($image in $images) {
        try {
            gcloud container images delete gcr.io/desarrolloswcloud/$image --quiet 2>$null
        } catch {
            Write-Warning "No se pudo eliminar la imagen $image"
        }
    }
    
    # Limpiar archivos de estado de Terraform
    Write-Info "Limpiando archivos de estado de Terraform..."
    Remove-Item *.tfstate* -Force -ErrorAction SilentlyContinue
    Remove-Item .terraform -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item .terraform.lock.hcl -Force -ErrorAction SilentlyContinue
    Remove-Item tfplan -Force -ErrorAction SilentlyContinue
    
    Write-Success "Limpieza completada. El proyecto está listo para un nuevo despliegue."
}

# Función para mostrar ayuda
function Show-Help {
    Write-Host "MediSupply - Script de Despliegue en PowerShell" -ForegroundColor $Colors.Green
    Write-Host ""
    Write-Host "Uso: .\deploy.ps1 [OPCIÓN]"
    Write-Host ""
    Write-Host "Opciones:"
    Write-Host "  all       Desplegar todo (infraestructura + aplicaciones)"
    Write-Host "  infra     Desplegar solo infraestructura"
    Write-Host "  apps      Desplegar solo aplicaciones (requiere infraestructura existente)"
    Write-Host "  verify    Verificar despliegue existente"
    Write-Host "  clean     Limpiar recursos (CUIDADO: Elimina todo)"
    Write-Host "  help      Mostrar esta ayuda"
    Write-Host ""
    Write-Host "Ejemplos:"
    Write-Host "  .\deploy.ps1 all      # Despliegue completo"
    Write-Host "  .\deploy.ps1 infra    # Solo infraestructura"
    Write-Host "  .\deploy.ps1 apps     # Solo aplicaciones"
}

# Función principal
function Main {
    switch ($Action) {
        "all" {
            Test-Prerequisites
            Setup-GoogleCloud
            Deploy-Infrastructure
            Setup-Kubectl
            Build-AndPush-Images
            Deploy-Applications
            Verify-Deployment
        }
        "infra" {
            Test-Prerequisites
            Setup-GoogleCloud
            Deploy-Infrastructure
            Setup-Kubectl
        }
        "apps" {
            Test-Prerequisites
            Setup-GoogleCloud
            Setup-Kubectl
            Build-AndPush-Images
            Deploy-Applications
            Verify-Deployment
        }
        "verify" {
            Verify-Deployment
        }
        "clean" {
            Clean-Resources
        }
        "help" {
            Show-Help
        }
        default {
            Write-Error "Opción no válida: $Action"
            Show-Help
            exit 1
        }
    }
}

# Ejecutar función principal
Main
