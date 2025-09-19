#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Banner ---
echo "=================================================="
echo "  Starting TourWithEase Local Development Env"
echo "=================================================="
echo

# --- Check for Docker ---
echo "Checking for Docker and Docker Compose..."
command -v docker >/dev/null 2>&1 || { echo >&2 "Docker is required but not installed. Aborting."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo >&2 "Docker Compose is required but not installed. Aborting."; exit 1; }
echo "Docker and Docker Compose are available."
echo

# --- Start Docker Compose ---
echo "Starting services with docker-compose..."
docker-compose up --build

# --- End of Script ---
echo "=================================================="
echo "  Development Environment Stopped"
echo "=================================================="
echo
