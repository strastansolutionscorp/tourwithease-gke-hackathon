# terraform/iam.tf - CORRECTED VERSION
# Create service account first
resource "google_service_account" "gke_workload_sa" {
  account_id   = "gke-workload-identity"
  display_name = "GKE Workload Identity Service Account"
  description  = "Service account for ADK agents"
  project      = var.project_id
}

# Wait for service account creation before binding
resource "time_sleep" "wait_for_sa" {
  depends_on      = [google_service_account.gke_workload_sa]
  create_duration = "10s"
}

# Workload Identity binding - FIXED
resource "google_service_account_iam_binding" "workload_identity_binding" {
  depends_on         = [time_sleep.wait_for_sa, google_container_cluster.primary]
  service_account_id = google_service_account.gke_workload_sa.name
  role               = "roles/iam.workloadIdentityUser"
  
  members = [
    "serviceAccount:${var.project_id}.svc.id.goog[agentic-ai/adk-agent-ksa]"
  ]
}

# Grant permissions to service account
resource "google_project_iam_member" "gke_sa_permissions" {
  for_each = toset([
    "roles/aiplatform.user",
    "roles/secretmanager.secretAccessor",
    "roles/storage.objectViewer",
    "roles/monitoring.metricWriter",
    "roles/logging.logWriter"
  ])
  
  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.gke_workload_sa.email}"
  
  depends_on = [google_service_account.gke_workload_sa]
}