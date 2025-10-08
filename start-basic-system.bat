@echo off
echo 🚀 Starting MediMate Basic System (without AI service)...
echo ========================================================

echo 🖥️  Starting Backend...
cd medimate-server
start "MediMate Backend" cmd /k "npm start"
cd ..

echo 🌐 Starting Frontend...
cd medimate-ui  
start "MediMate Frontend" cmd /k "npm start"
cd ..

echo.
echo 🎉 MediMate Basic System Started!
echo =================================
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend: http://localhost:5000
echo.
echo ⚠️  Note: AI service requires Docker to be running
echo    Use start-ai-system.bat once Docker is fixed
echo.
echo ✨ Ready for basic medical form processing!
pause