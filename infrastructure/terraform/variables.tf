# terraform/variables.tf
variable "project_id" {
  description = "agentic-travel-ai-solutions"
  type        = string
  default     = "agentic-travel-ai-solutions"
}

variable "region" {
  description = "GCP Region"  
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone for GKE cluster"
  type        = string
  default     = "us-central1-a"
}