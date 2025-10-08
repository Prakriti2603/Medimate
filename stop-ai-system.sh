#!/bin/bash

# MediMate AI System Shutdown Script
# Stops all AI system services

echo "🛑 Stopping MediMate AI System..."
echo "================================="

# Stop frontend
if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "🌐 Stopping React frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        echo "✅ Frontend stopped"
    fi
    rm -f .frontend.pid
fi

# Stop backend
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🖥️  Stopping Node.js backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        echo "✅ Backend stopped"
    fi
    rm -f .backend.pid
fi

# Stop AI service containers
echo "🤖 Stopping AI Service containers..."
cd medimate-ai-service
docker-compose down

if [ $? -eq 0 ]; then
    echo "✅ AI Service containers stopped"
else
    echo "⚠️  Some containers may still be running"
fi

cd ..

# Clean up any remaining processes
echo "🧹 Cleaning up remaining processes..."
pkill -f "npm start" 2>/dev/null || true
pkill -f "node.*server" 2>/dev/null || true

echo ""
echo "✅ MediMate AI System stopped successfully!"
echo "========================================="
echo ""
echo "All services have been shut down:"
echo "• React frontend stopped"
echo "• Node.js backend stopped"
echo "• AI service containers stopped"
echo "• Database containers stopped"
echo ""
echo "To restart the system:"
echo "  ./start-ai-system.sh"
echo ""