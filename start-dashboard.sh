#!/bin/bash

# Smart Home Web Dashboard - Quick Start Script

echo "🏠 Starting Smart Home Web Dashboard..."
echo ""

# Check if web_ui directory exists
if [ ! -d "web_ui" ]; then
    echo "❌ Error: web_ui directory not found!"
    echo "   Please run this script from the project root directory."
    exit 1
fi

# Check if Docker containers are running
echo "📦 Checking Docker containers..."
if ! docker-compose ps | grep -q "mqtt_broker.*Up"; then
    echo "⚠️  MQTT Broker not running. Starting all containers..."
    docker-compose up -d
    echo "⏳ Waiting for services to start..."
    sleep 10
else
    echo "✅ Docker containers are running"
fi

# Check WebSocket port
echo ""
echo "🔌 Checking MQTT WebSocket port (9001)..."
if ss -tuln | grep -q ":9001"; then
    echo "✅ WebSocket port 9001 is open"
else
    echo "⚠️  WebSocket port 9001 not found. Restarting Mosquitto..."
    docker-compose restart mosquitto
    sleep 5
fi

# Start HTTP server for web dashboard
echo ""
echo "🌐 Starting Web Dashboard HTTP Server..."
cd web_ui

# Kill existing server if running
pkill -f "python3 -m http.server 8000" 2>/dev/null

# Start server in background
python3 -m http.server 8000 > /dev/null 2>&1 &
SERVER_PID=$!

sleep 2

# Check if server started successfully
if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "✅ HTTP Server started (PID: $SERVER_PID)"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎉 Smart Home Dashboard is ready!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📱 Web Dashboard:     http://localhost:8000"
    echo "🔧 Node-RED:          http://localhost:1880"
    echo "🔌 MQTT Broker:       mqtt://localhost:1883"
    echo "🌐 MQTT WebSocket:    ws://localhost:9001"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📋 Quick Commands:"
    echo "   Stop server:       pkill -f 'python3 -m http.server 8000'"
    echo "   View logs:         docker-compose logs -f"
    echo "   Stop all:          docker-compose down"
    echo ""
    
    # Try to open browser (if available)
    if command -v xdg-open &> /dev/null; then
        echo "🌐 Opening browser..."
        xdg-open "http://localhost:8000" 2>/dev/null &
    fi
    
    echo "✨ Press Ctrl+C to stop monitoring logs"
    echo ""
    
    # Show logs
    cd ..
    docker-compose logs -f --tail=10
    
else
    echo "❌ Failed to start HTTP server"
    exit 1
fi
