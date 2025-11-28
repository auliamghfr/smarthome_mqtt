#!/usr/bin/env python3
"""
Simple HTTP-to-MQTT Proxy untuk Web Dashboard
Menerima HTTP requests dan translate ke MQTT messages
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import paho.mqtt.client as mqtt
import json
import threading
import time
from collections import deque
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MQTT Configuration
MQTT_BROKER = "localhost"  # Changed from "mosquitto" for host access
MQTT_PORT = 1883
MQTT_CLIENT_ID = "web_dashboard_proxy"

# Store latest sensor readings
sensor_data = {
    "temperature": None,
    "motion": None,
    "lamp_status": None,
    "timestamp": None
}

# Store event log (last 100 events)
event_log = deque(maxlen=100)

# MQTT Client
mqtt_client = None

def on_connect(client, userdata, flags, rc):
    print(f"✅ Connected to MQTT broker with result code {rc}")
    # Subscribe to all topics
    client.subscribe("home/sensor/#")
    client.subscribe("home/actuator/#")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    
    try:
        # Try to parse as JSON
        data = json.loads(payload)
    except:
        data = {"raw": payload}
    
    # Store data based on topic
    if "temperature" in topic:
        sensor_data["temperature"] = data
        event_log.append({
            "type": "temperature",
            "value": data.get("value"),
            "unit": data.get("unit", "°C"),
            "timestamp": datetime.now().isoformat()
        })
        print(f"🌡️ Temperature: {data.get('value')}°C")
    
    elif "motion" in topic:
        sensor_data["motion"] = data
        event_log.append({
            "type": "motion",
            "status": data.get("status"),
            "value": data.get("value"),
            "timestamp": datetime.now().isoformat()
        })
        print(f"🚶 Motion: {data.get('status')}")
    
    elif "lamp/status" in topic:
        sensor_data["lamp_status"] = data
        event_log.append({
            "type": "lamp",
            "state": data.get("state"),
            "timestamp": datetime.now().isoformat()
        })
        print(f"💡 Lamp: {data.get('state')}")
    
    sensor_data["timestamp"] = datetime.now().isoformat()

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print(f"⚠️ Unexpected disconnection: {rc}")

def connect_mqtt():
    global mqtt_client
    mqtt_client = mqtt.Client(client_id=MQTT_CLIENT_ID)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_disconnect = on_disconnect
    
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        mqtt_client.loop_start()
        return True
    except Exception as e:
        print(f"❌ Failed to connect to MQTT: {e}")
        return False

# REST API Endpoints

@app.route('/api/data', methods=['GET'])
def get_data():
    """Get current sensor readings"""
    return jsonify({
        "temperature": sensor_data.get("temperature"),
        "motion": sensor_data.get("motion"),
        "lamp_status": sensor_data.get("lamp_status"),
        "timestamp": sensor_data.get("timestamp")
    })

@app.route('/api/temperature', methods=['GET'])
def get_temperature():
    """Get current temperature"""
    return jsonify(sensor_data.get("temperature") or {})

@app.route('/api/motion', methods=['GET'])
def get_motion():
    """Get current motion status"""
    return jsonify(sensor_data.get("motion") or {})

@app.route('/api/lamp', methods=['GET'])
def get_lamp_status():
    """Get lamp status"""
    return jsonify(sensor_data.get("lamp_status") or {})

@app.route('/api/lamp/control', methods=['POST'])
def control_lamp():
    """Control lamp - POST {'command': 'ON'|'OFF'}"""
    try:
        data = request.get_json()
        command = data.get("command", "").upper()
        
        if command in ["ON", "OFF"]:
            mqtt_client.publish("home/actuator/lamp/command", command, qos=1)
            return jsonify({"status": "success", "command": command}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid command"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get event log"""
    limit = request.args.get("limit", 50, type=int)
    return jsonify(list(event_log)[-limit:])

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    return jsonify({
        "mqtt_connected": mqtt_client.is_connected() if mqtt_client else False,
        "broker": MQTT_BROKER,
        "port": MQTT_PORT,
        "uptime": "running"
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    print("🚀 Starting MQTT Proxy Server...")
    print(f"📡 Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    
    if connect_mqtt():
        print("✅ MQTT Connected!")
        time.sleep(2)  # Wait for initial connection
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("❌ Failed to connect to MQTT")
