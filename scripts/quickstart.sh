#!/bin/bash

# Quick Start Script for NLP to SQL System
# This script helps you quickly set up and run the system in mock mode

set -e

echo "=================================================="
echo "  NLP to SQL Analytics - Quick Start"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}❌ Python 3.10+ is required. You have Python $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
    exit 1
fi
echo ""

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo -e "${GREEN}✅ .env file created${NC}"
else
    echo -e "${YELLOW}.env file already exists${NC}"
fi
echo ""

# Check if data directory exists
if [ ! -d "data/mock" ]; then
    echo "Creating data directories..."
    mkdir -p data/mock
    mkdir -p data/templates
    echo -e "${GREEN}✅ Data directories created${NC}"
fi
echo ""

# Run local tests
echo "Running local tests..."
echo ""
python test_local.py

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo "=================================================="
    echo "  Setup Complete!"
    echo "=================================================="
    echo ""
    echo "You can now:"
    echo ""
    echo "  1. Start the API server:"
    echo -e "     ${GREEN}python -m app.main${NC}"
    echo ""
    echo "  2. View API docs at:"
    echo -e "     ${GREEN}http://localhost:8000/docs${NC}"
    echo ""
    echo "  3. Test with curl:"
    echo '     curl -X POST "http://localhost:8000/api/v1/ask" \'
    echo '       -H "Content-Type: application/json" \'
    echo '       -d '"'"'{"user_id": "test", "query": "What was iPhone revenue in India last quarter?", "auto_execute": true}'"'"''
    echo ""
    echo "  4. Run API tests:"
    echo -e "     ${GREEN}python scripts/test_api.py${NC}"
    echo ""
    echo "  5. Frontend (React):"
    echo -e "     ${GREEN}cd frontend && npm install && npm run dev${NC}"
    echo ""
    echo "=================================================="
else
    echo ""
    echo -e "${RED}❌ Tests failed. Please check the errors above.${NC}"
    exit 1
fi
