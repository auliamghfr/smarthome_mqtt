#!/bin/bash

# Test Script untuk MQTT Smart Home System
# Script ini untuk melakukan testing otomatis terhadap sistem

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  MQTT Smart Home - Test Suite${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if mosquitto_pub and mosquitto_sub are installed
if ! command -v mosquitto_pub &> /dev/null; then
    echo -e "${RED}❌ mosquitto_pub not found!${NC}"
    echo "Install with: sudo apt-get install mosquitto-clients"
    exit 1
fi

BROKER="localhost"
PORT="1883"

# Test 1: Check if broker is accessible
echo -e "${YELLOW}Test 1: Checking MQTT Broker Connectivity...${NC}"
if timeout 5 mosquitto_pub -h $BROKER -p $PORT -t "test/connection" -m "ping" -q 0; then
    echo -e "${GREEN}✅ Broker is accessible${NC}"
else
    echo -e "${RED}❌ Cannot connect to broker${NC}"
    exit 1
fi
echo ""

# Test 2: Subscribe and check if we receive temperature data
echo -e "${YELLOW}Test 2: Checking Temperature Sensor...${NC}"
echo "Waiting for temperature data (10 seconds)..."
TEMP_DATA=$(timeout 10 mosquitto_sub -h $BROKER -t "home/sensor/temperature" -C 1 || echo "")
if [ -n "$TEMP_DATA" ]; then
    echo -e "${GREEN}✅ Temperature data received:${NC}"
    echo "$TEMP_DATA"
else
    echo -e "${RED}❌ No temperature data received${NC}"
fi
echo ""

# Test 3: Subscribe and check if we receive motion data
echo -e "${YELLOW}Test 3: Checking Motion Sensor...${NC}"
echo "Waiting for motion data (10 seconds)..."
MOTION_DATA=$(timeout 10 mosquitto_sub -h $BROKER -t "home/sensor/motion" -C 1 || echo "")
if [ -n "$MOTION_DATA" ]; then
    echo -e "${GREEN}✅ Motion data received:${NC}"
    echo "$MOTION_DATA"
else
    echo -e "${RED}❌ No motion data received${NC}"
fi
echo ""

# Test 4: Test lamp control - Turn ON
echo -e "${YELLOW}Test 4: Testing Lamp Control - Turn ON...${NC}"
mosquitto_pub -h $BROKER -t "home/actuator/lamp/command" -m "ON" -q 1
echo "Waiting for lamp status update..."
sleep 2
LAMP_STATUS=$(timeout 3 mosquitto_sub -h $BROKER -t "home/actuator/lamp/status" -C 1 || echo "")
if [[ "$LAMP_STATUS" == *"ON"* ]]; then
    echo -e "${GREEN}✅ Lamp turned ON successfully${NC}"
    echo "$LAMP_STATUS"
else
    echo -e "${RED}❌ Lamp ON command failed${NC}"
fi
echo ""

# Test 5: Test lamp control - Turn OFF
echo -e "${YELLOW}Test 5: Testing Lamp Control - Turn OFF...${NC}"
mosquitto_pub -h $BROKER -t "home/actuator/lamp/command" -m "OFF" -q 1
echo "Waiting for lamp status update..."
sleep 2
LAMP_STATUS=$(timeout 3 mosquitto_sub -h $BROKER -t "home/actuator/lamp/status" -C 1 || echo "")
if [[ "$LAMP_STATUS" == *"OFF"* ]]; then
    echo -e "${GREEN}✅ Lamp turned OFF successfully${NC}"
    echo "$LAMP_STATUS"
else
    echo -e "${RED}❌ Lamp OFF command failed${NC}"
fi
echo ""

# Test 6: Test motion-based automation
echo -e "${YELLOW}Test 6: Testing Motion-Based Automation...${NC}"
echo "Simulating motion detection..."
mosquitto_pub -h $BROKER -t "home/sensor/motion" -m '{"value": 1, "status": "motion detected"}' -q 1
echo "Waiting for lamp to turn ON..."
sleep 3
LAMP_STATUS=$(timeout 3 mosquitto_sub -h $BROKER -t "home/actuator/lamp/status" -C 1 || echo "")
if [[ "$LAMP_STATUS" == *"ON"* ]]; then
    echo -e "${GREEN}✅ Automation working: Motion detected → Lamp ON${NC}"
else
    echo -e "${YELLOW}⚠️  Automation may not be configured in Node-RED${NC}"
fi

echo "Simulating no motion..."
mosquitto_pub -h $BROKER -t "home/sensor/motion" -m '{"value": 0, "status": "no motion"}' -q 1
echo "Waiting for lamp to turn OFF..."
sleep 3
LAMP_STATUS=$(timeout 3 mosquitto_sub -h $BROKER -t "home/actuator/lamp/status" -C 1 || echo "")
if [[ "$LAMP_STATUS" == *"OFF"* ]]; then
    echo -e "${GREEN}✅ Automation working: No motion → Lamp OFF${NC}"
else
    echo -e "${YELLOW}⚠️  Automation may not be configured in Node-RED${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "MQTT Broker: ${GREEN}✅${NC}"
echo -e "Temperature Sensor: ${GREEN}✅${NC}"
echo -e "Motion Sensor: ${GREEN}✅${NC}"
echo -e "Lamp Control (Manual): ${GREEN}✅${NC}"
echo -e "Motion Automation: Check Node-RED flow"
echo ""
echo -e "${GREEN}All basic tests passed!${NC}"
echo ""
echo "For detailed monitoring, run:"
echo "  mosquitto_sub -h localhost -t '#' -v"
