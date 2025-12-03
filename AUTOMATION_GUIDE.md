# Smart Home Automation System - Complete Guide

## 📋 System Overview

Sistem home automation berbasis MQTT dengan multi-threading yang menghubungkan berbagai IoT devices (lights, thermostat, security cameras) dengan automation rules.

## ✅ Requirement Status

| Requirement | Status | File |
|------------|--------|------|
| **MQTT Protocol** | ✅ Complete | All devices |
| **Temperature Sensor** | ✅ Complete | `devices/temp_sensor.py` |
| **Lights** | ✅ Complete | `devices/smart_light.py` |
| **Thermostat** | ✅ Complete | `devices/thermostat.py` |
| **Security Camera** | ✅ Complete | `devices/security_camera.py` |
| **Automation** | ✅ Complete | `controller.py` |
| **Multi-threading** | ✅ Complete | `main.py` |
| **User Commands** | ✅ Complete | `user_commands.py` |

---

## 🏗️ System Architecture

```
┌─────────────────────┐
│   User Commands     │ (CLI Interface)
│  user_commands.py   │
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │ MQTT Broker  │ (mosquitto)
    │   Port 1883  │
    └──────┬───────┘
           │
     ┌─────┴──────────────────────────────┐
     │                                    │
┌────▼─────┐                    ┌────────▼────────┐
│ SENSORS  │                    │   ACTUATORS     │
├──────────┤                    ├─────────────────┤
│ • Temp   │ ──── publish ────> │ • Smart Light   │
│ • Motion │                    │ • Thermostat    │
│ • Camera │                    │ • HVAC          │
└──────────┘                    └─────────────────┘
     │                                    ▲
     │                                    │
     └──────> ┌──────────────────┐ ──────┘
              │ Automation       │
              │ Controller       │
              │ (controller.py)  │
              └──────────────────┘
```

---

## 🤖 Automation Rules

### Rule 1: Temperature Control
- **Condition**: Temperature > 28°C
- **Action**: Set thermostat to COOL mode
- **Effect**: Activates air conditioning

### Rule 2: Heating Control
- **Condition**: Temperature < 20°C
- **Action**: Set thermostat to HEAT mode
- **Effect**: Activates heating system

### Rule 3: Motion Detection Lighting
- **Condition**: Motion detected
- **Action**: Turn ON lights
- **Effect**: Automatic lighting when movement detected

### Rule 4: Auto Light Off
- **Condition**: No motion for 30 seconds
- **Action**: Turn OFF lights
- **Effect**: Energy saving by auto-off lights

---

## 🧵 Multi-threading Implementation

File: `main.py`

### Thread Architecture:
```python
Main Thread
├── Thread 1: Temperature Sensor
├── Thread 2: Smart Light
├── Thread 3: Thermostat
├── Thread 4: Security Camera
└── Thread 5: Automation Controller
```

**Benefits:**
- ✅ **Parallel Execution**: All devices run simultaneously
- ✅ **Responsive Control**: No blocking between devices
- ✅ **Real-time Processing**: Instant response to sensor data
- ✅ **Independent Operation**: One device failure doesn't affect others

---

## 📁 File Structure

```
mqtt_smarthome/
├── main.py                      # Multi-threading coordinator
├── controller.py                # Automation engine
├── user_commands.py             # User CLI interface
├── devices/
│   ├── utils.py                # MQTT utilities
│   ├── temp_sensor.py          # Temperature sensor
│   ├── smart_light.py          # Smart light device
│   ├── thermostat.py           # Thermostat controller
│   └── security_camera.py      # Motion detection camera
└── docker-compose.yml          # Docker configuration
```

---

## 🚀 Running the System

### Option 1: Run All Devices (Multi-threading)
```bash
python3 main.py
```
This starts all devices in parallel threads.

### Option 2: Run Individual Devices
```bash
# Terminal 1 - Temperature Sensor
python3 devices/temp_sensor.py

# Terminal 2 - Smart Light
python3 devices/smart_light.py

# Terminal 3 - Thermostat
python3 devices/thermostat.py

# Terminal 4 - Security Camera
python3 devices/security_camera.py

# Terminal 5 - Automation Controller
python3 controller.py
```

### Option 3: User Command Interface
```bash
python3 user_commands.py
```

---

## 💬 User Commands Reference

### Light Commands
```bash
light on                    # Turn on light
light off                   # Turn off light
light brightness 50         # Set brightness to 50%
```

### Thermostat Commands
```bash
thermostat temp 24          # Set target temperature to 24°C
thermostat mode AUTO        # Set to AUTO mode
thermostat mode COOL        # Set to COOL mode
thermostat mode HEAT        # Set to HEAT mode
thermostat mode OFF         # Turn off thermostat
```

### Camera Commands
```bash
camera on                   # Activate camera
camera off                  # Deactivate camera
camera sensitivity 0.5      # Set sensitivity to 0.5 (0.0-1.0)
```

### System Commands
```bash
status                      # Get status from all devices
help                        # Show help menu
quit                        # Exit interface
```

---

## 📡 MQTT Topics

### Sensor Topics (Publish)
- `home/sensor/temperature` - Temperature readings
- `home/security/motion` - Motion detection events

### Actuator Command Topics (Subscribe)
- `home/light/command` - Light control commands
- `home/thermostat/command` - Thermostat commands
- `home/security/camera/command` - Camera commands
- `home/hvac/command` - HVAC system commands

### Status Topics (Publish)
- `home/light/status` - Light status
- `home/thermostat/status` - Thermostat status
- `home/security/camera/status` - Camera status

---

## 🔧 Configuration

Environment variables (all devices):
```bash
BROKER=mosquitto           # MQTT broker hostname
PORT=1883                  # MQTT broker port
CLIENT_ID=device_name      # Unique client identifier
```

Device-specific variables:
```bash
# Temperature Sensor
TOPIC=home/sensor/temperature
INTERVAL=5                 # Publish interval in seconds

# Smart Light
LIGHT_ID=living_room
COMMAND_TOPIC=home/light/command
STATUS_TOPIC=home/light/status

# Thermostat
THERMOSTAT_ID=main_hvac
TEMP_TOPIC=home/sensor/temperature

# Security Camera
CAMERA_ID=front_door
MOTION_TOPIC=home/security/motion
CHECK_INTERVAL=3
```

---

## 📊 Monitoring

### Check Running Threads
When using `main.py`, you'll see:
```
Active Threads:
  • TemperatureSensor - Running
  • SmartLight - Running
  • Thermostat - Running
  • SecurityCamera - Running
  • AutomationController - Running
```

### System Status
```
System Status:
  📡 MQTT Communication: Active
  🤖 Automation Rules: Enabled
  🧵 Multi-threading: Enabled
```

---

## 🧪 Testing Scenarios

### Scenario 1: Temperature-based Cooling
1. Wait for temperature sensor to publish temp > 28°C
2. Automation controller detects high temperature
3. Thermostat switches to COOL mode
4. HVAC system activates cooling

### Scenario 2: Motion Detection
1. Security camera detects motion (random simulation)
2. Motion event published to MQTT
3. Automation controller receives event
4. Light turns ON automatically
5. After 30s no motion, light turns OFF

### Scenario 3: Manual Control
1. Run `user_commands.py`
2. Enter: `light on`
3. Light receives command and turns on
4. Status published back to user

---

## 🛑 Stopping the System

- **Multi-threaded mode**: Press `Ctrl+C`
- **Individual devices**: Press `Ctrl+C` in each terminal
- **User interface**: Type `quit` or press `Ctrl+C`

---

## ✨ Key Features Implemented

### ✅ MQTT Communication
- Publisher/Subscriber pattern
- QoS level 1 for reliable delivery
- Automatic reconnection with retry mechanism

### ✅ Multi-threading
- Daemon threads for clean shutdown
- Thread monitoring and health checks
- Independent device operation

### ✅ Automation
- Event-driven architecture
- Rule-based automation engine
- Sensor-actuator coordination

### ✅ User Interface
- Interactive CLI
- Real-time device control
- Status monitoring

### ✅ Device Simulation
- Realistic sensor data generation
- Stateful device models
- Command processing

---

## 📝 Summary

**Requirement Compliance: 100% ✅**

This system fully implements:
1. ✅ Multiple IoT devices (lights, thermostat, security camera)
2. ✅ MQTT for lightweight messaging
3. ✅ Multi-threading for parallel device communication
4. ✅ Responsive control of devices
5. ✅ Home automation with intelligent rules
6. ✅ User command interface

**Communication Paradigm**: MQTT (Message Queuing Telemetry Transport)
**Process Model**: Multi-threading with daemon threads
**Architecture**: Publisher-Subscriber with centralized automation

---

## 🎯 Next Steps

1. Run the system: `python3 main.py`
2. Open another terminal: `python3 user_commands.py`
3. Try commands: `light on`, `status`, `thermostat temp 25`
4. Observe automation rules in action!

Enjoy your Smart Home Automation System! 🏠✨
