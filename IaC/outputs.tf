# Outputs del cluster GKE
output "cluster_name" {
  description = "Nombre del cluster GKE"
  value       = google_container_cluster.medisupply.name
}

output "cluster_endpoint" {
  description = "Endpoint del cluster GKE"
  value       = google_container_cluster.medisupply.endpoint
  sensitive   = true
}

output "cluster_ca_certificate" {
  description = "Certificado CA del cluster"
  value       = google_container_cluster.medisupply.master_auth[0].cluster_ca_certificate
  sensitive   = true
}

output "cluster_location" {
  description = "Ubicación del cluster"
  value       = google_container_cluster.medisupply.location
}

# Outputs de la base de datos
output "db_instance_name" {
  description = "Nombre de la instancia de Cloud SQL"
  value       = google_sql_database_instance.medisupply_db.name
}

output "db_connection_name" {
  description = "Connection name para Cloud SQL Proxy"
  value       = google_sql_database_instance.medisupply_db.connection_name
}

output "db_databases" {
  description = "Bases de datos creadas"
  value       = [for db in google_sql_database.databases : db.name]
}


# Outputs de service accounts
output "workload_service_account" {
  description = "Service account para Workload Identity"
  value       = google_service_account.medisupply_workload.email
}

output "kubernetes_service_account_name" {
  description = "Nombre de la cuenta de servicio de Kubernetes"
  value       = kubernetes_service_account.medisupply_ksa.metadata[0].name
}

output "workload_identity_pool" {
  description = "Pool de Workload Identity"
  value       = "${var.project_id}.svc.id.goog"
}

# Outputs de Pub/Sub
output "pubsub_topic" {
  description = "Topic de Pub/Sub para eventos"
  value       = google_pubsub_topic.medisupply_events.name
}

output "pubsub_subscription" {
  description = "Subscription de Pub/Sub"
  value       = google_pubsub_subscription.medisupply_subscription.name
}

# Outputs de configuración para kubectl
output "kubectl_config" {
  description = "Comando para configurar kubectl"
  value       = "gcloud container clusters get-credentials ${google_container_cluster.medisupply.name} --zone ${var.zone} --project ${var.project_id}"
}

# Outputs de información de despliegue
output "sql_connection_name" {
  description = "Connection name para Cloud SQL Proxy"
  value       = google_sql_database_instance.medisupply_db.connection_name
}

output "deployment_info" {
  description = "Información importante para el despliegue"
  value = {
    cluster_name     = google_container_cluster.medisupply.name
    db_host          = "localhost"  # Cloud SQL Proxy
    db_port          = "5432"
    project_id       = var.project_id
    region           = var.region
    zone             = var.zone
    connection_name  = google_sql_database_instance.medisupply_db.connection_name
  }
}

output "cloud_sql_proxy_info" {
  description = "Información para Cloud SQL Proxy"
  value = {
    connection_name = google_sql_database_instance.medisupply_db.connection_name
    cluster_name    = google_container_cluster.medisupply.name
    project_id      = var.project_id
    instructions    = "Usar Cloud SQL Proxy sidecar en los deployments - conectarse a localhost:5432"
  }
}

output "static_ip_address" {
  description = "IP estática global asignada al ingress"
  value       = google_compute_global_address.medisupply_static_ip.address
}

# Outputs de Storage
output "evidencias_bucket_name" {
  description = "Nombre del bucket para evidencias de visitas"
  value       = google_storage_bucket.evidencias.name
}

output "evidencias_bucket_url" {
  description = "URL del bucket de evidencias"
  value       = google_storage_bucket.evidencias.url
}

output "storage_info" {
  description = "Información del bucket de evidencias"
  value = {
    bucket_name    = google_storage_bucket.evidencias.name
    bucket_url     = google_storage_bucket.evidencias.url
    location       = google_storage_bucket.evidencias.location
    storage_class  = google_storage_bucket.evidencias.storage_class
    permissions    = "Service account tiene roles/storage.objectAdmin"
  }
}