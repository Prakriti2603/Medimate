#!/bin/bash

# MediMate AI System Startup Script
# Starts all services required for AI-powered medical form processing

echo "🚀 Starting MediMate AI System..."
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start AI Service
echo "🤖 Starting AI Service..."
cd medimate-ai-service
docker-compose up -d --build

if [ $? -eq 0 ]; then
    echo "✅ AI Service started successfully"
else
    echo "❌ Failed to start AI Service"
    exit 1
fi

cd ..

# Wait for AI service to be ready
echo "⏳ Waiting for AI service to initialize..."
sleep 10

# Check AI service health
AI_HEALTH=$(curl -s http://localhost:8001/health | grep -o '"status":"healthy"' || echo "")
if [ -n "$AI_HEALTH" ]; then
    echo "✅ AI Service is healthy"
else
    echo "⚠️  AI Service may still be initializing..."
fi

# Start Node.js backend
echo "🖥️  Starting Node.js backend..."
cd medimate-server
npm install > /dev/null 2>&1
npm start &
BACKEND_PID=$!

if [ $? -eq 0 ]; then
    echo "✅ Backend started successfully (PID: $BACKEND_PID)"
else
    echo "❌ Failed to start backend"
    exit 1
fi

cd ..

# Wait for backend to start
sleep 5

# Start React frontend
echo "🌐 Starting React frontend..."
cd medimate-ui
npm install > /dev/null 2>&1
npm start &
FRONTEND_PID=$!

if [ $? -eq 0 ]; then
    echo "✅ Frontend started successfully (PID: $FRONTEND_PID)"
else
    echo "❌ Failed to start frontend"
    exit 1
fi

cd ..

echo ""
echo "🎉 MediMate AI System Started Successfully!"
echo "=========================================="
echo ""
echo "📱 Frontend:           http://localhost:3000"
echo "🖥️  Backend API:        http://localhost:3001"
echo "🤖 AI Service:         http://localhost:8001"
echo "📊 AI Documentation:   http://localhost:8001/docs"
echo "🔍 MLflow UI:          http://localhost:5000"
echo "💾 Redis:              localhost:6379"
echo "🗄️  MongoDB:           localhost:27017"
echo ""
echo "🚀 Ready to process medical documents with AI!"
echo ""
echo "To access the AI Form Processor:"
echo "1. Open http://localhost:3000"
echo "2. Click 'AI Form Processor' module"
echo "3. Upload a medical document"
echo "4. Watch AI automatically fill forms!"
echo ""
echo "To stop all services:"
echo "  ./stop-ai-system.sh"
echo ""

# Save PIDs for cleanup
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo "✨ System is ready for AI-powered medical form processing!"