#!/bin/bash

# Quick Start Script for Travel Agency Management System
# This script helps you get started quickly

set -e

echo "=========================================="
echo "Travel Agency Management System"
echo "Quick Start Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker is installed${NC}"
echo -e "${GREEN}✓ Docker Compose is installed${NC}"
echo ""

# Step 1: Set up environment variables
echo "Step 1: Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file${NC}"
else
    echo -e "${YELLOW}⚠ .env file already exists, skipping${NC}"
fi

if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo -e "${GREEN}✓ Created backend/.env file${NC}"
else
    echo -e "${YELLOW}⚠ backend/.env file already exists, skipping${NC}"
fi

if [ ! -f frontend/.env.local ]; then
    cp frontend/.env.local.example frontend/.env.local
    echo -e "${GREEN}✓ Created frontend/.env.local file${NC}"
else
    echo -e "${YELLOW}⚠ frontend/.env.local file already exists, skipping${NC}"
fi

echo ""
echo -e "${YELLOW}IMPORTANT: Please edit the .env files with your actual credentials:${NC}"
echo "  - SECRET_KEY (generate a secure key)"
echo "  - SENDGRID_API_KEY (if using email features)"
echo "  - AZURE_STORAGE_CONNECTION_STRING (if using Azure storage)"
echo ""
read -p "Have you configured the environment variables? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Please configure the environment variables and run this script again${NC}"
    exit 1
fi

# Step 2: Build and start services
echo ""
echo "Step 2: Building and starting Docker services..."
echo "This may take a few minutes on the first run..."
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Step 3: Check if services are running
echo ""
echo "Step 3: Checking service health..."
if docker-compose ps | grep -q "Up"; then
    echo -e "${GREEN}✓ Services are running${NC}"
else
    echo -e "${RED}✗ Some services failed to start${NC}"
    echo "Please check the logs with: docker-compose logs"
    exit 1
fi

# Step 4: Run database migrations
echo ""
echo "Step 4: Running database migrations..."
docker-compose exec -T backend alembic upgrade head
echo -e "${GREEN}✓ Database migrations completed${NC}"

# Step 5: Create admin user
echo ""
echo "Step 5: Creating admin user..."
echo "Note: If the create_admin script doesn't exist yet, you'll need to create it"
# docker-compose exec -T backend python -m app.scripts.create_admin || echo -e "${YELLOW}⚠ Admin user creation script not found, you'll need to create it manually${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Your application is now running:"
echo ""
echo "  Frontend:        http://localhost:3000"
echo "  Backend API:     http://localhost:8000"
echo "  API Docs:        http://localhost:8000/api/v1/docs"
echo "  ReDoc:           http://localhost:8000/api/v1/redoc"
echo ""
echo "Useful commands:"
echo "  View logs:       docker-compose logs -f"
echo "  Stop services:   docker-compose down"
echo "  Restart:         docker-compose restart"
echo ""
echo "Next steps:"
echo "  1. Visit http://localhost:3000 to see the frontend"
echo "  2. Visit http://localhost:8000/api/v1/docs to explore the API"
echo "  3. Check the README.md for more information"
echo ""
echo "For detailed setup instructions, see SETUP_GUIDE.md"
echo ""
