# terraform/gke.tf - FIXED VERSION
resource "google_container_cluster" "primary" {
  name     = "agentic-ai-cluster"
  location = var.zone  # Use zone instead of region
  
  # Remove default node pool
  remove_default_node_pool = true
  initial_node_count       = 1
  
  # Use default network to avoid conflicts
  network    = google_compute_network.vpc_network.name
  subnetwork = google_compute_subnetwork.vpc_subnetwork.name
  
  # FIXED: Non-overlapping IP allocation

  
  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  enable_shielded_nodes = true
  deletion_protection = false
  
  # Basic addons
  addons_config {
    http_load_balancing {
      disabled = false
    }
    horizontal_pod_autoscaling {
      disabled = false
    }
  }

  private_cluster_config {
    enable_private_nodes    = true
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }
  
  # Allow all networks for hackathon
  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "0.0.0.0/0"
      display_name = "All networks"
    }
  }
}

# Separate node pool
resource "google_container_node_pool" "primary_nodes" {
  name       = "primary-node-pool"
  location   = "us-central1-a"
  cluster    = google_container_cluster.primary.name
  node_count = 3

  node_config {
    machine_type = "e2-standard-4"
    disk_size_gb = 50
    disk_type    = "pd-ssd"
    
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
    
    labels = {
      workload = "adk-agents"
    }
  }
  
  autoscaling {
    min_node_count = 1
    max_node_count = 6
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}