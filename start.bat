@echo off
REM Startup script for NLP to SQL Analytics System (Windows)

echo ========================================
echo NLP to SQL Analytics System - Startup
echo ========================================
echo.

REM Check if Docker mode
if "%1"=="docker" (
    echo Starting services with Docker Compose...
    docker-compose up --build
    exit /b 0
)

REM Backend setup
echo Setting up backend...

if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing backend dependencies...
pip install -q -r requirements.txt

if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
)

echo Backend setup complete
echo.

REM Frontend setup
echo Setting up frontend...

cd frontend

if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

if not exist ".env.local" (
    echo Creating .env.local file...
    copy .env.example .env.local
)

echo Frontend setup complete
echo.

cd ..

REM Start services
echo Starting services...
echo.

echo Starting backend on port 8000...
start "Backend" cmd /c "venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo Starting frontend on port 3000...
cd frontend
start "Frontend" cmd /c "npm run dev"
cd ..

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo Services started successfully!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to view instructions...
pause >nul
