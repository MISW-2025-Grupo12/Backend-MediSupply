# Variables de configuración del proyecto
variable "project_id" {
  description = "ID del proyecto de Google Cloud"
  type        = string
  default     = "desarrolloswcloud"
}

variable "region" {
  description = "Región de Google Cloud"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Zona de Google Cloud"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Ambiente de despliegue"
  type        = string
  default     = "prod"
}

# Variables del cluster GKE
variable "cluster_name" {
  description = "Nombre del cluster GKE"
  type        = string
  default     = "medisupply-cluster"
}

variable "node_count" {
  description = "Número de nodos en el cluster"
  type        = number
  default     = 1
}

variable "machine_type" {
  description = "Tipo de máquina para los nodos"
  type        = string
  default     = "e2-medium"  # 1 vCPU, 4 GB RAM
}

variable "disk_size_gb" {
  description = "Tamaño del disco en GB"
  type        = number
  default     = 20
}

# Variables de Cloud SQL
variable "db_instance_name" {
  description = "Nombre de la instancia de Cloud SQL"
  type        = string
  default     = "medisupply-db"
}

variable "db_tier" {
  description = "Tier de la instancia de Cloud SQL"
  type        = string
  default     = "db-f1-micro"
}

variable "db_disk_size" {
  description = "Tamaño del disco de la base de datos en GB"
  type        = number
  default     = 100
}

variable "db_disk_type" {
  description = "Tipo de disco para la base de datos"
  type        = string
  default     = "PD_SSD"
}

# Variables de passwords
variable "db_root_password" {
  description = "Password root de la base de datos"
  type        = string
  sensitive   = true
  default     = "medisupply123!Prod"
}

variable "db_passwords" {
  description = "Passwords para los usuarios de las bases de datos"
  type        = map(string)
  sensitive   = true
  default = {
    usuarios   = "usuarios123!Prod"
    productos  = "productos123!Prod"
    ventas     = "ventas123!Prod"
    logistica  = "logistica123!Prod"
  }
}

# Variables de aplicación
variable "app_name" {
  description = "Nombre de la aplicación"
  type        = string
  default     = "medisupply"
}

variable "app_domain" {
  description = "Dominio de la aplicación"
  type        = string
  default     = "medisupply.com"
}

# Variables de recursos
variable "min_replicas" {
  description = "Número mínimo de réplicas por servicio"
  type        = number
  default     = 1 
}

variable "max_replicas" {
  description = "Número máximo de réplicas por servicio"
  type        = number
  default     = 5
}
