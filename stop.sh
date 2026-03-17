#!/bin/bash

# Stop script for NLP to SQL Analytics System

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Stopping NLP to SQL Analytics System...${NC}"

# Stop using saved PIDs
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    echo -e "Stopping backend (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || echo "Backend already stopped"
    rm -f .backend.pid
fi

if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    echo -e "Stopping frontend (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null || echo "Frontend already stopped"
    rm -f .frontend.pid
fi

# Also try to kill by port (backup method)
echo -e "Checking for processes on ports 8000 and 3000..."

# Kill backend on port 8000
BACKEND_PORT_PID=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$BACKEND_PORT_PID" ]; then
    echo -e "Killing process on port 8000 (PID: $BACKEND_PORT_PID)..."
    kill $BACKEND_PORT_PID 2>/dev/null
fi

# Kill frontend on port 3000
FRONTEND_PORT_PID=$(lsof -ti:3000 2>/dev/null)
if [ ! -z "$FRONTEND_PORT_PID" ]; then
    echo -e "Killing process on port 3000 (PID: $FRONTEND_PORT_PID)..."
    kill $FRONTEND_PORT_PID 2>/dev/null
fi

# Clean up log files
if [ -f "backend.log" ]; then
    rm backend.log
fi

if [ -f "frontend.log" ]; then
    rm frontend.log
fi

echo -e "${GREEN}All services stopped${NC}"
