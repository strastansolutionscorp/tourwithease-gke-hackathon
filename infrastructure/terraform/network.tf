resource "google_compute_network" "vpc_network" {
  name                    = "tourwithease-vpc"
  auto_create_subnetworks = false
  project                 = var.project_id
}

resource "google_compute_subnetwork" "vpc_subnetwork" {
  name          = "gke-subnet"
  ip_cidr_range = "10.10.0.0/24"
  private_ip_google_access = true
  region        = var.region
  network       = google_compute_network.vpc_network.id
  project       = var.project_id
}



