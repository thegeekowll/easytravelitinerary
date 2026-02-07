#!/bin/bash

# Quick Setup Script for Travel Agency Management System
# This script automates the entire setup process

set -e  # Exit on error

echo "========================================================================"
echo " Travel Agency Management System - Quick Setup"
echo "========================================================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC}  $1"
}

# Step 1: Check prerequisites
echo "Step 1: Checking prerequisites..."
echo "----------------------------------------"

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi
print_status "Python 3 found: $(python3 --version)"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    print_warning "PostgreSQL client not found in PATH"
    print_warning "Make sure PostgreSQL is installed and running"
else
    print_status "PostgreSQL client found"
fi

# Check pip
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    print_error "pip is not installed"
    exit 1
fi
print_status "pip found"

echo

# Step 2: Install dependencies
echo "Step 2: Installing Python dependencies..."
echo "----------------------------------------"
pip install -r requirements.txt -q
print_status "Dependencies installed"
echo

# Step 3: Check database
echo "Step 3: Checking database..."
echo "----------------------------------------"

# Try to connect
if psql -U postgres -d travel_agency -c "SELECT 1;" &> /dev/null; then
    print_status "Database 'travel_agency' exists"
else
    print_warning "Database 'travel_agency' not found"
    echo "Creating database..."
    
    if createdb -U postgres travel_agency 2>/dev/null; then
        print_status "Database created successfully"
    else
        print_error "Failed to create database"
        echo "Please create it manually: createdb -U postgres travel_agency"
        exit 1
    fi
fi
echo

# Step 4: Verify setup
echo "Step 4: Verifying setup..."
echo "----------------------------------------"
python verify_setup.py || {
    print_error "Setup verification failed"
    echo "Please check the errors above and fix them"
    exit 1
}
echo

# Step 5: Initialize database
echo "Step 5: Initializing database..."
echo "----------------------------------------"
python app/db/init_db.py || {
    print_error "Database initialization failed"
    exit 1
}
echo

# Step 6: Run tests
echo "Step 6: Running model tests..."
echo "----------------------------------------"
python test_models.py || {
    print_error "Model tests failed"
    exit 1
}
echo

# Success!
echo "========================================================================"
echo -e " ${GREEN}✅ SETUP COMPLETE!${NC}"
echo "========================================================================"
echo
echo "Your Travel Agency Management System is ready!"
echo
echo "Next steps:"
echo "  1. Start the application:"
echo "     uvicorn app.main:app --reload"
echo
echo "  2. Visit the API documentation:"
echo "     http://localhost:8000/docs"
echo
echo "  3. Check the health endpoint:"
echo "     curl http://localhost:8000/health"
echo
echo "For more information, see README_TESTING.md"
echo
