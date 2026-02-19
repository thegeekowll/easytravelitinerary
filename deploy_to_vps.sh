#!/bin/bash

# Deploy to Hostinger VPS Script
# Usage: ./deploy_to_vps.sh [VPS_IP]

echo "========================================"
echo "    Travel Agency VPS Deployer"
echo "========================================"

# 1. Configuration
VPS_USER="root"
PROJECT_NAME="easytravelitinerary"
REPO_URL="https://github.com/thegeekowll/easytravelitinerary.git"

# Get VPS IP
if [ -z "$1" ]; then
    read -p "Enter your VPS IP Address: " VPS_IP
else
    VPS_IP=$1
fi

if [ -z "$VPS_IP" ]; then
    echo "Error: IP address is required."
    exit 1
fi

echo ""
echo "🚀 Target: $VPS_USER@$VPS_IP"
echo "⚠️  You may be prompted for your VPS password multiple times."
echo "   (Tip: Set up SSH keys to avoid typing passwords: ssh-copy-id $VPS_USER@$VPS_IP)"
echo ""
read -p "Press Enter to start deployment..."
echo ""

# 2. Prepare Remote Server (Install Dependencies)
echo "----------------------------------------"
echo "Step 1: Preparing Remote Server..."
echo "----------------------------------------"

ssh $VPS_USER@$VPS_IP << 'ENDSSH'
    # Update system
    echo "Updating system packages..."
    export DEBIAN_FRONTEND=noninteractive
    apt-get update > /dev/null
    
    # Check/Install Docker
    if ! command -v docker &> /dev/null; then
        echo "Installing Docker..."
        apt-get install -y docker.io docker-compose-plugin > /dev/null
        systemctl start docker
        systemctl enable docker
    else
        echo "Docker is already installed."
    fi

    # Check/Install Git
    if ! command -v git &> /dev/null; then
        echo "Installing Git..."
        apt-get install -y git > /dev/null
    fi
ENDSSH

if [ $? -ne 0 ]; then
    echo "❌ SSH connection failed. Check your IP and Password."
    exit 1
fi

# 3. Setup Project on VPS
echo ""
echo "----------------------------------------"
echo "Step 2: Syncing Codebase..."
echo "----------------------------------------"

ssh $VPS_USER@$VPS_IP "
    if [ ! -d $PROJECT_NAME ]; then
        echo 'Cloning repository...'
        git clone $REPO_URL $PROJECT_NAME
    else
        echo 'Pulling latest changes...'
        cd $PROJECT_NAME
        # Reset local changes to ensure clean pull (cautious approach)
        git reset --hard
        git pull origin main
    fi
"

# 4. Transfer Environment Configuration
echo ""
echo "----------------------------------------"
echo "Step 3: Uploading Configuration & Secrets..."
echo "----------------------------------------"

# Check local files
if [ ! -f .env ] || [ ! -f backend/.env ] || [ ! -f frontend/.env.local ]; then
    echo "❌ Error: Missing local .env files. Please ensure you have:"
    echo "  - .env"
    echo "  - backend/.env"
    echo "  - frontend/.env.local"
    exit 1
fi

# Create remote directories if needed
ssh $VPS_USER@$VPS_IP "mkdir -p $PROJECT_NAME/backend $PROJECT_NAME/frontend"

# Upload files using SCP
echo "Uploading .env..."
scp .env $VPS_USER@$VPS_IP:~/$PROJECT_NAME/.env
echo "Uploading backend/.env..."
scp backend/.env $VPS_USER@$VPS_IP:~/$PROJECT_NAME/backend/.env
echo "Uploading frontend/.env.local..."
scp frontend/.env.local $VPS_USER@$VPS_IP:~/$PROJECT_NAME/frontend/.env.local

# Also upload the optimized docker-compose.yml explicitly to override any old copy
echo "Uploading optimized docker-compose.yml..."
scp docker-compose.yml $VPS_USER@$VPS_IP:~/$PROJECT_NAME/docker-compose.yml

# 5. Build and Start Services
echo ""
echo "----------------------------------------"
echo "Step 4: Starting Application..."
echo "----------------------------------------"

ssh $VPS_USER@$VPS_IP "
    cd $PROJECT_NAME
    
    echo 'Building and starting containers...'
    # Force recreate to pick up new config/images
    docker compose up -d --build --force-recreate
    
    echo 'Waiting for database to be ready...'
    sleep 10
    
    echo 'Running database migrations...'
    docker compose exec -T backend alembic upgrade head
    
    echo 'Seeding initial data...'
    docker compose exec -T backend python -m app.db.init_db
    
    echo 'Checking services...'
    docker compose ps
"

echo ""
echo "========================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "========================================"
echo "Access your app at: http://$VPS_IP"
echo "API Documentation:  http://$VPS_IP/docs (or http://$VPS_IP:8000/docs)"
echo ""
