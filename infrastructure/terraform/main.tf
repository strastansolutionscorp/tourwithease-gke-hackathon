provider "google" {
    project = var.project_id
    region = var.region
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

    project = var.project_id
    service = each.key
    disable_on_destroy = false
}


variable "org_id" {
    description = "GCP Organization ID"
    type = string
}
