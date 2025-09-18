# Service account for GKE workloads
resource "google_service_account" "gke_workload_sa" {
    account_id = "gke-workload-identity"
    display_name = "GKE Workload Identity Service Account"
    description = "Service account for ADK agents running on GKE"
    project = google_project.tourwithease_hackathon.project_id
}

# Workload Identity binding
resource "google_service_account_iam_binding" "workload_identity_binding" {
    service_account_id = google_service_account.gke_workload_sa.name
    role = "roles/iam.workloadIdentityUser"

    members = [
        "serviceAccount:${google_project.tourwithease_hackathon.project_id}.svc.id.goog[default/adk-agent-ksa]"
    ]
}

# Grant necessary permissions to service account
resource "google_project_iam_member" "gke_sa_permissions" {
    for_each = toset([
        "roles/aiplatform.user", # Vertex AI access
        "roles/secretmanager.secretAccessor", # Access secrets
        "roles/cloudsql.client", # Cloud SQL access
        "roles/storage.objectViewer", # Storage access
        "roles/monitoring.metricWriter", # Write metrics
        "roles/logging.logWriter" # Write logs
    ])

    project = google_project.tourwithease_hackathon.project_id
    role = each.key
    member = "serviceAccount:${google_service_account.gke_workload_sa.email}"
}

# Team member IAM (replace with actual email addresses)
locals {
    team_members = [
    "dev1@yourdomain.com", # AI Developer 1
    "dev2@yourdomain.com", # AI Developer 2
    "dev3@yourdomain.com", # Fullstack Developer 1
    "dev4@yourdomain.com" # Fullstack Developer 2
    ]
    team_roles = [
    "roles/container.developer", # GKE access
    "roles/aiplatform.user", # Vertex AI access
    "roles/cloudbuild.builds.editor", # Build access
    "roles/secretmanager.admin", # Secret management
    "roles/monitoring.editor", # Monitoring access
    "roles/logging.viewer", # Log viewing
    "roles/source.admin" # Source repository access
    ]
}

resource "google_project_iam_member" "team_member_access" {
    for_each = {
        for pair in setproduct(local.team_members, local.team_roles) :
        "${pair[0]}-${pair[1]}" => {
            member = "user:${pair[0]}"
            role = pair[1]
        }
    }

    project = google_project.tourwithease_hackathon.project_id
    role = each.value.role
    member = each.value.member
}