#!/bin/bash
set -e
echo "🚀 Setting up TourWithEase GKE Hackathon Development Environment"
# Check prerequisites
echo "📋 Checking prerequisites..."
# Node.js version check
NODE_VERSION=$(node -v | cut -d'v' -f2)
REQUIRED_NODE="18.0.0"
if [ "$(printf '%s\n' "$REQUIRED_NODE" "$NODE_VERSION" | sort -V | head -n1)"
!= "$REQUIRED_NODE" ]; then
echo "❌ Node.js version $REQUIRED_NODE or higher required. Found:
$NODE_VERSION"
exit 1
fi
echo "✅ Node.js version: $NODE_VERSION"
# Python check (for ADK agents)
if ! command -v python3 &> /dev/null; then
echo "❌ Python 3 is required for ADK agents"
exit 1
fi
echo "✅ Python 3 available"
# Docker check
if ! command -v docker &> /dev/null; then
echo "❌ Docker is required"
exit 1
fi
echo "✅ Docker available"
# Google Cloud CLI check
if ! command -v gcloud &> /dev/null; then
echo "❌ Google Cloud CLI is required"
echo "📥 Install from: https://cloud.google.com/sdk/docs/install"
exit 1
fi
echo "✅ Google Cloud CLI available"

# kubectl check
if ! command -v kubectl &> /dev/null; then
echo "❌ kubectl is required"
echo "📥 Install with: gcloud components install kubectl"
exit 1
fi
echo "✅ kubectl available"
echo ""
echo "📦 Installing dependencies..."
# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install
# Bootstrap Lerna monorepo
echo "🔗 Setting up monorepo..."
npx lerna bootstrap
# Set up Python virtual environment for ADK agents
echo "🐍 Setting up Python environment for ADK agents..."
cd backend/api-gateway/python-agents
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ../../..
# Create necessary directories
echo "📁 Creating directory structure..."
mkdir -p logs
mkdir -p data/redis
mkdir -p data/uploads
mkdir -p .secrets
# Set up Git hooks
echo "🔧 Setting up Git hooks..."
npm run prepare
# Create environment files
echo "📝 Creating environment files..."
# Backend environment
cat > backend/api-gateway/.env.development << EOF
NODE_ENV=development

PORT=8000
REDIS_URL=redis://localhost:6379
AWS_API_GATEWAY_URL=https://your-api-gateway-url/prod
AWS_API_KEY=your-api-key-here
GOOGLE_CLOUD_PROJECT=tourwithease-gke-hackathon-2024
JWT_SECRET=your-jwt-secret-here
FRONTEND_URL=http://localhost:3000
LOG_LEVEL=info
EOF
# Frontend environment
cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000
EOF
# Python agents environment
cat > backend/api-gateway/python-agents/.env << EOF
REDIS_URL=redis://localhost:6379
AWS_API_GATEWAY_URL=https://your-api-gateway-url/prod
AWS_API_KEY=your-api-key-here
GOOGLE_CLOUD_PROJECT=tourwithease-gke-hackathon-2024
LOG_LEVEL=INFO
EOF
echo ""
echo "🔐 Google Cloud Setup"
echo "📋 Run these commands to set up GCP:"
echo " gcloud auth login"
echo " gcloud config set project tourwithease-gke-hackathon-2024"
echo " gcloud auth application-default login"
echo ""
echo "🐳 Docker Setup"
echo "📋 Run these commands to start local services:"
echo " docker-compose up -d redis"
echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Configure your AWS API Gateway URL and API key in .env files"
echo "2. Set up your Google Cloud project and authentication"
echo "3. Start development with: npm run dev"
echo ""
echo "📚 Available commands:"
echo " npm run dev - Start all services in development mode"
echo " npm run build - Build all packages"
echo " npm run test - Run all tests"
echo " npm run docker:up - Start Docker services"
echo " npm run k8s:deploy - Deploy to Kubernetes"