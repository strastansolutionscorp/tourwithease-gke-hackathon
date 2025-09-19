#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Change to the project root directory
cd "$(dirname "$0")"/..

# --- Banner ---
echo "=================================================="
echo "      TourWithEase Deploy Script"
echo "=================================================="
echo

# --- Configuration ---
export PROJECT_ID="agentic-travel-ai-solutions"
export ZONE="us-central1-a"
export CLUSTER_NAME="agentic-ai-cluster" # Change this to your GKE cluster name
export REPOSITORY="tourwithease-repo"
export IMAGE_TAG="${SHORT_SHA:-latest}"

export API_GATEWAY_IMAGE_NAME="api-gateway"


# --- Authenticate to GKE ---
echo "Authenticating to GKE cluster: ${CLUSTER_NAME}..."
gcloud container clusters get-credentials "${CLUSTER_NAME}" --zone "${ZONE}"
echo

# --- Update Kustomization ---
echo "Updating kustomization with new image tags..."
cd infrastructure/k8s
kustomize edit set image api-gateway-image-placeholder="${API_GATEWAY_IMAGE_URI}:${IMAGE_TAG}"

echo "Kustomization updated."
cd ../..
echo

# --- Deploy to GKE ---
echo "Deploying to GKE cluster using Kustomize..."
kubectl apply -k infrastructure/k8s/
echo

# --- Deployment Complete ---
echo "=================================================="
echo "      Deployment to GKE Complete!"
echo "=================================================="
echo
