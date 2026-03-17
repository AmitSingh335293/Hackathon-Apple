#!/bin/bash

# Startup script for NLP to SQL Analytics System
# This script helps you start both frontend and backend services

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}NLP to SQL Analytics System - Startup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if running in Docker mode
if [ "$1" == "docker" ]; then
    echo -e "${GREEN}Starting services with Docker Compose...${NC}"
    docker-compose up --build
    exit 0
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}Error: npm is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Backend setup
echo -e "${BLUE}Setting up backend...${NC}"

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing backend dependencies..."
pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

echo -e "${GREEN}✓ Backend setup complete${NC}"
echo ""

# Frontend setup
echo -e "${BLUE}Setting up frontend...${NC}"

cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file..."
    cp .env.example .env.local
fi

echo -e "${GREEN}✓ Frontend setup complete${NC}"
echo ""

cd ..

# Start services
echo -e "${BLUE}Starting services...${NC}"
echo ""

# Start backend in background
echo -e "${YELLOW}Starting backend on port 8000...${NC}"
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend in background
echo -e "${YELLOW}Starting frontend on port 3000...${NC}"
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

cd ..

# Wait for services to start
sleep 3

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Services started successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Frontend: ${NC}http://localhost:3000"
echo -e "${BLUE}Backend API: ${NC}http://localhost:8000"
echo -e "${BLUE}API Docs: ${NC}http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Logs:${NC}"
echo -e "  Backend: tail -f backend.log"
echo -e "  Frontend: tail -f frontend.log"
echo ""
echo -e "${YELLOW}To stop services:${NC}"
echo -e "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo -e "${YELLOW}Process IDs:${NC}"
echo -e "  Backend PID: $BACKEND_PID"
echo -e "  Frontend PID: $FRONTEND_PID"
echo ""

# Save PIDs to file for easy cleanup
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid

# Wait for user to stop
echo -e "${GREEN}Press Ctrl+C to stop all services${NC}"
echo ""

# Trap Ctrl+C
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f .backend.pid .frontend.pid; echo 'Services stopped'; exit" INT

# Wait indefinitely
wait
