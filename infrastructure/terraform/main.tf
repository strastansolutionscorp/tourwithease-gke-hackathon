terraform {
    required_providers {
        google = {
            source = "hashicorp/google"
            version = "~> 5.0"
        }
    }
}

provider "google" {
    project = var.project_id
    region = var.region
}

# Create the project
resource "google_project" "tourwithease_hackathon" {
    name = "TourWithEase GKE Hackathon"
    project_id = var.project_id
    org_id = var.org_id # Your organization ID

    labels = {
        environment = "hackathon"
        team = "ai-agents"
        purpose = "gke-hackathon-2024"
    }
}

# Enable required APIs
resource "google_project_service" "required_apis" {
    for_each = toset([
        "container.googleapis.com", # GKE
        "aiplatform.googleapis.com", # Vertex AI
        "cloudbuild.googleapis.com", # Container builds
        "artifactregistry.googleapis.com", # Container registry
        "secretmanager.googleapis.com", # Secrets
        "sql-component.googleapis.com", # Cloud SQL
        "storage-component.googleapis.com", # Cloud Storage
        "monitoring.googleapis.com", # Monitoring
        "logging.googleapis.com", # Logging
        "cloudresourcemanager.googleapis.com" # Resource management
    ])

    project = google_project.tourwithease_hackathon.project_id
    service = each.key
    disable_on_destroy = false
}

# Variables
variable "project_id" {
    description = "GCP Project ID"
    type = string
    default = "twe-gke-hackathon-2024"
}

variable "region" {
    description = "GCP Region"
    type = string
    default = "us-central1"
}

variable "org_id" {
    description = "GCP Organization ID"
    type = string
}
