#!/usr/bin/env python3
"""
Smart Home MQTT Proxy Server
HTTP-to-MQTT bridge for web dashboard
Connects to MQTT broker and exposes REST API
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
MQTT_BROKER = "localhost"  # Use "mosquitto" if running in Docker
MQTT_PORT = 1883
MQTT_CLIENT_ID = "web_dashboard_proxy"

# Store latest sensor readings
sensor_data = {
    "temperature": None,
    "motion": None,
    "light_status": None,
    "thermostat_status": None,
    "camera_status": None,
    "timestamp": None
}

# Store event log (last 100 events)
event_log = deque(maxlen=100)

# MQTT Client
mqtt_client = None

def on_connect(client, userdata, flags, rc):
    print(f"✅ Connected to MQTT broker with result code {rc}")
    # Subscribe to all smart home topics
    client.subscribe("home/sensor/temperature")
    client.subscribe("home/sensor/motion")
    client.subscribe("home/security/motion")
    client.subscribe("home/security/camera/status")
    client.subscribe("home/light/status")
    client.subscribe("home/actuator/lamp/status")
    client.subscribe("home/thermostat/status")
    client.subscribe("home/hvac/command")
    print("✅ Subscribed to all topics")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    
    try:
        # Try to parse as JSON
        data = json.loads(payload)
    except:
        data = {"raw": payload}
    
    timestamp = datetime.now().isoformat()
    
    # Store data based on topic
    if topic == "home/sensor/temperature":
        sensor_data["temperature"] = {
            "value": data.get("value"),
            "unit": data.get("unit", "°C"),
            "timestamp": timestamp
        }
        event_log.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "source": "Temperature Sensor",
            "role": "Publisher",
            "type": "Reading",
            "value": f"{data.get('value', 0):.1f}°C"
        })
        print(f"🌡️  Temperature: {data.get('value')}°C")
    
    elif topic == "home/sensor/motion":
        # Motion sensor from devices/motion_sensor.py
        motion_value = data.get("value", 0)
        motion_status = data.get("status", "unknown")
        
        # Always update motion status (detected or not detected)
        sensor_data["motion"] = {
            "detected": motion_value == 1,
            "camera_id": "motion_sensor",
            "timestamp": timestamp
        }
        
        if motion_value == 1:
            event_log.append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "source": "Motion Sensor",
                "role": "Publisher",
                "type": "Motion Detected",
                "value": "🚨 Motion Alert"
            })
            print(f"🚨 Motion detected (value=1)")
        else:
            event_log.append({
                "time": datetime.now().strftime("%H:%M:%S"),
                "source": "Motion Sensor",
                "role": "Publisher",
                "type": "No Motion",
                "value": "✓ Clear"
            })
            print(f"✓ No motion detected (value=0)")
    
    elif topic == "home/security/motion":
        # Security camera motion
        sensor_data["motion"] = {
            "detected": True,
            "camera_id": data.get("camera_id"),
            "timestamp": timestamp
        }
        event_log.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "source": f"Camera {data.get('camera_id', 'Unknown')}",
            "role": "Publisher",
            "type": "Motion Detected",
            "value": "⚠️ Motion Alert"
        })
        print(f"🚨 Motion detected from {data.get('camera_id')}")
    
    elif topic == "home/security/camera/status":
        sensor_data["camera_status"] = {
            "active": data.get("active"),
            "recording": data.get("recording"),
            "camera_id": data.get("camera_id"),
            "timestamp": timestamp
        }
        
        status_text = "Active" if data.get("active") else "Inactive"
        recording_text = " | Recording" if data.get("recording") else ""
        
        event_log.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "source": f"Camera {data.get('camera_id', 'Unknown')}",
            "role": "Publisher",
            "type": "Status Change",
            "value": f"{status_text}{recording_text}"
        })
        print(f"📷 Camera status: {data.get('active')}")
    
    elif topic == "home/light/status" or topic == "home/actuator/lamp/status":
        state = data.get("state", "UNKNOWN")
        brightness = data.get("brightness", 0)
        
        sensor_data["light_status"] = {
            "state": state,
            "brightness": brightness,
            "light_id": data.get("light_id", "smart_lamp"),
            "timestamp": timestamp
        }
        
        # Add to event log
        event_log.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "source": "Smart Lamp",
            "role": "Subscriber",
            "type": "Status Change",
            "value": f"💡 {state} ({brightness}%)"
        })
        print(f"💡 Light: {state} - {brightness}%")
    
    elif topic == "home/thermostat/status":
        sensor_data["thermostat_status"] = {
            "current_temp": data.get("current_temp"),
            "target_temp": data.get("target_temp"),
            "mode": data.get("mode"),
            "hvac_state": data.get("hvac_state"),
            "timestamp": timestamp
        }
        event_log.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "source": "Thermostat",
            "role": "Subscriber",
            "type": "Status Update",
            "value": f"Mode: {data.get('mode')} | HVAC: {data.get('hvac_state')}"
        })
        print(f"🌡️  Thermostat: {data.get('mode')} - {data.get('hvac_state')}")
    
    sensor_data["timestamp"] = timestamp

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
        "light_status": sensor_data.get("light_status"),
        "thermostat_status": sensor_data.get("thermostat_status"),
        "camera_status": sensor_data.get("camera_status"),
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

@app.route('/api/light', methods=['GET'])
def get_light_status():
    """Get light status"""
    return jsonify(sensor_data.get("light_status") or {})

@app.route('/api/light/control', methods=['POST'])
def control_light():
    """Control light - POST {'command': 'ON'|'OFF'} or {'command': 'BRIGHTNESS', 'level': 0-100}"""
    try:
        data = request.get_json()
        command = data.get("command", "").upper()
        
        if command in ["ON", "OFF"]:
            payload = json.dumps({"command": command})
            mqtt_client.publish("home/actuator/lamp/command", payload, qos=1)
            return jsonify({"status": "success", "command": command}), 200
        elif command == "BRIGHTNESS":
            level = data.get("level", 100)
            payload = json.dumps({"command": "BRIGHTNESS", "level": level})
            mqtt_client.publish("home/actuator/lamp/command", payload, qos=1)
            return jsonify({"status": "success", "command": command, "level": level}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid command"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/thermostat', methods=['GET'])
def get_thermostat():
    """Get thermostat status"""
    return jsonify(sensor_data.get("thermostat_status") or {})

@app.route('/api/thermostat/control', methods=['POST'])
def control_thermostat():
    """Control thermostat - POST {'command': 'SET_TARGET', 'target': 24} or {'command': 'SET_MODE', 'mode': 'AUTO'}"""
    try:
        data = request.get_json()
        command = data.get("command", "").upper()
        
        payload = json.dumps(data)
        mqtt_client.publish("home/thermostat/command", payload, qos=1)
        return jsonify({"status": "success", "command": command}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/camera', methods=['GET'])
def get_camera():
    """Get camera status"""
    return jsonify(sensor_data.get("camera_status") or {})

@app.route('/api/camera/control', methods=['POST'])
def control_camera():
    """Control camera - POST {'command': 'ACTIVATE'|'DEACTIVATE'}"""
    try:
        data = request.get_json()
        payload = json.dumps(data)
        mqtt_client.publish("home/security/camera/command", payload, qos=1)
        return jsonify({"status": "success"}), 200
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
