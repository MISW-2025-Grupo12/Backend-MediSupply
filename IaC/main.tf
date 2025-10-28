# Configuración local para nombres de recursos
locals {
  common_labels = {
    environment = var.environment
    project     = var.app_name
    managed_by  = "terraform"
  }
  
  # Nombres de recursos con prefijo del ambiente
  cluster_name = "${var.cluster_name}-${var.environment}"
  db_name      = "${var.db_instance_name}-${var.environment}"
}

# Habilitar APIs necesarias
resource "google_project_service" "apis" {
  for_each = toset([
    "container.googleapis.com",
    "compute.googleapis.com",
    "sqladmin.googleapis.com",
    "pubsub.googleapis.com",
    "containerregistry.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com"
  ])
  
  project = var.project_id
  service = each.key
  
  disable_dependent_services = true
}



# Service Account simplificado para GKE (sin Pub/Sub)
resource "google_service_account" "medisupply_workload" {
  account_id   = "${var.app_name}-workload-${var.environment}"
  display_name = "MediSupply Workload Identity"
  
  depends_on = [google_project_service.apis]
}

# Permisos IAM con Pub/Sub y Workload Identity
resource "google_project_iam_member" "medisupply_workload_permissions" {
  for_each = toset([
    "roles/cloudsql.client",
    "roles/monitoring.metricWriter",
    "roles/logging.logWriter",
    "roles/pubsub.editor",
    "roles/pubsub.subscriber",
    "roles/pubsub.publisher",
    "roles/storage.objectViewer",
    "roles/artifactregistry.reader"
  ])
  
  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.medisupply_workload.email}"
}

# Crear cluster GKE con configuración optimizada para producción
resource "google_container_cluster" "medisupply" {
  name     = local.cluster_name
  location = var.zone
  
  # Configuración de Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }
  
  # Configuración de autoscaling
  node_pool {
    name       = "default-pool"
    node_count = var.node_count
    
    node_config {
      machine_type = var.machine_type
      disk_size_gb = var.disk_size_gb
      disk_type    = "pd-ssd"
      
      # Configuración de imagen
      image_type = "COS_CONTAINERD"
      
      # Configuración de service account
      service_account = google_service_account.medisupply_workload.email
      
      # Configuración de metadatos para Workload Identity
      workload_metadata_config {
        mode = "GKE_METADATA"
      }
      
      # Configuración de seguridad con Pub/Sub y Workload Identity
      oauth_scopes = [
        "https://www.googleapis.com/auth/cloud-platform"
      ]
      
      labels = local.common_labels
      
      tags = ["gke-node"]
    }
    
    autoscaling {
      min_node_count = 1
      max_node_count = 5
    }
    
    management {
      auto_repair  = true
      auto_upgrade = true
    }
  }
  
  
  # Desactivar temporalmente la protección para poder destruir
  deletion_protection = false
  
  depends_on = [
    google_project_service.apis,
    google_service_account.medisupply_workload
  ]
}

# IMPORTANTE: Los deployments de K8s deben configurarse para usar Cloud SQL Proxy
# o actualizar las IPs hardcodeadas con la IP pública de Cloud SQL
# Ejecutar: terraform output db_public_ip
# Actualizar k8s/*-deployment.yaml con la IP obtenida
# Alternativamente, configurar Cloud SQL Proxy sidecar en los deployments

# Crear instancia de Cloud SQL PostgreSQL (usando Cloud SQL Proxy)
resource "google_sql_database_instance" "medisupply_db" {
  name             = local.db_name
  database_version = "POSTGRES_15"
  region           = var.region
  
  settings {
    tier            = var.db_tier
    disk_size       = var.db_disk_size
    disk_type       = var.db_disk_type
    disk_autoresize = true
    
    # Configuración de backup básica
    backup_configuration {
      enabled    = true
      start_time = "03:00"
    }
    
    # Configuración de IP - Cloud SQL Proxy manejará la conexión
    ip_configuration {
      ipv4_enabled = true
      # Require SSL para mayor seguridad
      require_ssl = true
    }
  }
  
  deletion_protection = false
  
  depends_on = [google_project_service.apis]
}

# Crear bases de datos para cada microservicio
resource "google_sql_database" "databases" {
  for_each = toset([
    "usuarios_db",
    "productos_db", 
    "ventas_db",
    "logistica_db"
  ])
  
  name     = each.key
  instance = google_sql_database_instance.medisupply_db.name
  
  depends_on = [google_sql_database_instance.medisupply_db]
}

# Crear usuarios para cada base de datos
resource "google_sql_user" "db_users" {
  for_each = {
    usuarios   = { name = "usuarios_user", password = var.db_passwords.usuarios }
    productos  = { name = "productos_user", password = var.db_passwords.productos }
    ventas     = { name = "ventas_user", password = var.db_passwords.ventas }
    logistica  = { name = "logistica_user", password = var.db_passwords.logistica }
  }
  
  name     = each.value.name
  password = each.value.password
  instance = google_sql_database_instance.medisupply_db.name
  
  depends_on = [google_sql_database_instance.medisupply_db]
}

# Crear usuario root para administración
resource "google_sql_user" "root" {
  name     = "postgres"
  password = var.db_root_password
  instance = google_sql_database_instance.medisupply_db.name
  
  depends_on = [google_sql_database_instance.medisupply_db]
}

# Crear topic de Pub/Sub para eventos
resource "google_pubsub_topic" "medisupply_events" {
  name = "${var.app_name}-events-${var.environment}"
  
  depends_on = [google_project_service.apis]
}

# Crear subscription para el topic
resource "google_pubsub_subscription" "medisupply_subscription" {
  name  = "${var.app_name}-subscription-${var.environment}"
  topic = google_pubsub_topic.medisupply_events.name
  
  ack_deadline_seconds = 20
  
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }
  
  depends_on = [google_pubsub_topic.medisupply_events]
}

# IP estática global para el ingress
resource "google_compute_global_address" "medisupply_static_ip" {
  name = "medisupply-ip"
  
  lifecycle {
    prevent_destroy = true  # Proteger IP estática de terraform destroy
  }
}

# Kubernetes Service Account para Workload Identity
resource "kubernetes_service_account" "medisupply_ksa" {
  metadata {
    name      = "${var.app_name}-ksa"
    namespace = "medisupply"
    annotations = {
      "iam.gke.io/gcp-service-account" = google_service_account.medisupply_workload.email
    }
  }
  
  depends_on = [google_container_cluster.medisupply]
}

# Binding de Workload Identity
resource "google_service_account_iam_member" "workload_identity_binding" {
  service_account_id = google_service_account.medisupply_workload.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[medisupply/${kubernetes_service_account.medisupply_ksa.metadata[0].name}]"
  
  depends_on = [
    google_service_account.medisupply_workload,
    kubernetes_service_account.medisupply_ksa
  ]
}

