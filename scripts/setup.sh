#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Banner ---
echo "=================================================="
echo "      TourWithEase Project Setup Script"
echo "=================================================="
echo

# --- Check for prerequisites ---
echo "Checking for prerequisites (Node.js, npm, Lerna)..."
command -v node >/dev/null 2>&1 || { echo >&2 "Node.js is required but not installed. Aborting."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo >&2 "npm is required but not installed. Aborting."; exit 1; }
echo "All prerequisites are met."
echo

# --- Install Dependencies ---
echo "Installing root dependencies..."
npm install
echo

echo "Bootstrapping Lerna monorepo (installing package dependencies and linking them)..."
npm install -g lerna
lerna bootstrap
echo

# --- Setup Complete ---
echo "=================================================="
echo "      Setup Complete!"
echo "=================================================="
echo "You can now use the other scripts:"
echo "  - ./scripts/dev-start.sh: To start the local development environment."
echo "  - ./scripts/build.sh: To build the applications and Docker images."
echo "  - ./scripts/deploy.sh: To deploy the application to GKE."
echo

