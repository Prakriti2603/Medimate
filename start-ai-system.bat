@echo off
echo 🚀 Starting MediMate AI System...
echo ==================================

docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker not running. Start Docker Desktop first.
    pause
    exit /b 1
)

echo 🤖 Starting AI Service...
cd medimate-ai-service
docker-compose up -d --build
cd ..

echo 🖥️  Starting Backend...
cd medimate-server
start "Backend" cmd /k "npm install && npm start"
cd ..

echo 🌐 Starting Frontend...
cd medimate-ui  
start "Frontend" cmd /k "npm install && npm start"
cd ..

echo.
echo 🎉 MediMate AI System Started!
echo ==============================
echo 📱 Frontend: http://localhost:3000
echo 🤖 AI Service: http://localhost:8001/docs
echo 🔍 MLflow: http://localhost:5000
echo.
echo ✨ Ready for AI medical form processing!
pause