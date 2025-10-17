terraform {
  required_version = ">= 1.0"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
  
  # Backend para almacenar el estado
  # backend "gcs" {
  #   bucket = "medisupply-terraform-state"
  #   prefix = "prod"
  # }
}
