#!/bin/bash

# Quick Start Script untuk Smart Home System
# Autor: Smart Home Project
# Deskripsi: Script untuk memudahkan start/stop/restart system

set -e

# Colors untuk output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Smart Home Automation System${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Function to check if docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running!${NC}"
        echo "Please start Docker and try again."
        exit 1
    fi
}

# Function to start system
start_system() {
    echo -e "${YELLOW}🚀 Starting all containers...${NC}"
    docker-compose up --build -d
    echo ""
    echo -e "${GREEN}✅ System started!${NC}"
    echo ""
    echo "Access points:"
    echo "  - Node-RED: http://localhost:1880"
    echo "  - Dashboard: http://localhost:1880/ui"
    echo "  - MQTT Broker: localhost:1883"
    echo ""
    echo "View logs with: docker-compose logs -f"
}

# Function to stop system
stop_system() {
    echo -e "${YELLOW}🛑 Stopping all containers...${NC}"
    docker-compose stop
    echo -e "${GREEN}✅ System stopped!${NC}"
}

# Function to restart system
restart_system() {
    echo -e "${YELLOW}🔄 Restarting system...${NC}"
    docker-compose restart
    echo -e "${GREEN}✅ System restarted!${NC}"
}

# Function to view logs
view_logs() {
    echo -e "${YELLOW}📋 Viewing logs (Ctrl+C to exit)...${NC}"
    docker-compose logs -f
}

# Function to check status
check_status() {
    echo -e "${YELLOW}📊 System Status:${NC}"
    echo ""
    docker-compose ps
}

# Function to clean system
clean_system() {
    echo -e "${RED}🧹 WARNING: This will remove all containers and volumes!${NC}"
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
        echo -e "${GREEN}✅ System cleaned!${NC}"
    else
        echo -e "${YELLOW}Cancelled.${NC}"
    fi
}

# Function to test MQTT
test_mqtt() {
    echo -e "${YELLOW}🧪 Testing MQTT connectivity...${NC}"
    echo ""
    echo "Subscribing to all topics (Ctrl+C to stop):"
    mosquitto_sub -h localhost -t '#' -v
}

# Main menu
check_docker

case "$1" in
    start)
        start_system
        ;;
    stop)
        stop_system
        ;;
    restart)
        restart_system
        ;;
    logs)
        view_logs
        ;;
    status)
        check_status
        ;;
    clean)
        clean_system
        ;;
    test)
        test_mqtt
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|status|clean|test}"
        echo ""
        echo "Commands:"
        echo "  start   - Build and start all containers"
        echo "  stop    - Stop all containers"
        echo "  restart - Restart all containers"
        echo "  logs    - View real-time logs"
        echo "  status  - Check container status"
        echo "  clean   - Remove all containers and volumes"
        echo "  test    - Test MQTT broker connection"
        exit 1
        ;;
esac
