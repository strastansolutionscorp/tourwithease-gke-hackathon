#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
cd "$PROJECT_ROOT"

# --- Banner ---
echo "=================================================="
echo "      TourWithEase Build Script"
echo "=================================================="
echo

# --- Configuration ---
# These variables would typically be set in a CI/CD environment.
export PROJECT_ID="agentic-travel-ai-solutions"
export REGION="us-central1"
export REPOSITORY="tourwithease-repo"
export IMAGE_TAG="${SHORT_SHA:-latest}"

export API_GATEWAY_IMAGE_NAME="api-gateway"

export API_GATEWAY_IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${API_GATEWAY_IMAGE_NAME}:${IMAGE_TAG}"

# --- Authenticate to Google Cloud ---
echo "Authenticating to Google Cloud..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev
echo

# --- Build and Push API Gateway ---
echo "Building and pushing the API Gateway image..."
echo "Image URI: ${API_GATEWAY_IMAGE_URI}"
docker build -t "${API_GATEWAY_IMAGE_URI}" -f backend/api-gateway/Dockerfile .
docker push "${API_GATEWAY_IMAGE_URI}"
echo "API Gateway image pushed successfully."
echo

# --- Build Complete ---
echo "=================================================="
echo "      Build and Push Complete!"
echo "=================================================="
echo "Image pushed:"
echo "  - ${API_GATEWAY_IMAGE_URI}"
echo