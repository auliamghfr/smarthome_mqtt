# Smart Home Automation System - MQTT IoT Project

Sistem Smart Home berbasis IoT menggunakan MQTT protocol, Docker, Node-RED, dan Python.

## 📋 Daftar Isi

- [Arsitektur Sistem](#arsitektur-sistem)
- [Komponen Sistem](#komponen-sistem)
- [Struktur Project](#struktur-project)
- [Cara Menjalankan](#cara-menjalankan)
- [Web Dashboard UI](#web-dashboard-ui)
- [Testing & Monitoring](#testing--monitoring)
- [Konfigurasi Node-RED](#konfigurasi-node-red)
- [Troubleshooting](#troubleshooting)
- [Referensi](#referensi)

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network                            │
│  ┌──────────────┐     ┌──────────────┐                      │
│  │ Temperature  │────▶│              │                       │
│  │   Sensor     │     │   Mosquitto  │                       │
│  └──────────────┘     │     Broker   │◀────┐                │
│                       │   (MQTT)     │     │                │
│  ┌──────────────┐     │              │     │                │
│  │   Motion     │────▶│   Port 1883  │     │                │
│  │   Sensor     │     └──────────────┘     │                │
│  └──────────────┘            ▲             │                │
│                              │             │                │
│  ┌──────────────┐            │       ┌─────┴──────┐         │
│  │  Smart Lamp  │◀───────────┼───────│  Node-RED  │         │
│  │  (Actuator)  │            │       │ (Logic &   │         │
│  └──────────────┘            │       │ Dashboard) │         │
│                              │       │ Port 1880  │         │
│                              └───────│            │         │
│                                      └────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Komponen Sistem

### 1. **MQTT Broker (Mosquitto)**
- Image: `eclipse-mosquitto:2.0`
- Port: `1883` (MQTT), `9001` (WebSocket)
- Fungsi: Pusat komunikasi pub/sub untuk semua IoT devices
- Konfigurasi: `allow_anonymous true` untuk development
- WebSocket: Enabled untuk web dashboard connectivity

### 2. **Node-RED**
- Image: `nodered/node-red:latest`
- Port: `1880` (Web UI)
- Fungsi: 
  - Logic controller (automation)
  - Dashboard visualisasi
  - Rule engine untuk smart home

### 3. **Temperature Sensor**
- Bahasa: Python 3.11
- Publish ke: `home/sensor/temperature`
- Interval: 5 detik
- Data: Suhu acak 18-32°C

### 4. **Motion Sensor**
- Bahasa: Python 3.11
- Publish ke: `home/security/motion`
- Interval: 3 detik
- Data: Status gerakan (0/1) dalam format JSON

### 5. **Smart Lamp (Light)**
- Bahasa: Python 3.11
- Subscribe: `home/light/command`
- Publish: `home/light/status`
- Command: ON/OFF dengan brightness support
- Status: JSON dengan state, brightness, timestamp

### 6. **Thermostat**
- Bahasa: Python 3.11
- Subscribe: `home/thermostat/command`
- Publish: `home/thermostat/status`
- Mode: AUTO, HEAT, COOL, OFF
- HVAC State: HEATING, COOLING, IDLE

### 7. **Enhanced Web Dashboard**
- Stack: Flask + paho-mqtt + HTML/CSS/JS
- MQTT Proxy: HTTP-to-MQTT bridge (port 5000)
- Web UI: Modern dashboard (port 8000)
- Features: Real-time monitoring, device control, charts, event logs

---

## 📁 Struktur Project

```
mqtt_smarthome/
├── docker-compose.yml          # Orchestration semua services
├── README.md                   # Dokumentasi ini
├── DASHBOARD_UPDATE.md         # Enhanced dashboard guide
├── start-dashboard.sh          # Quick start script untuk dashboard
├── mosquitto/
│   └── mosquitto.conf          # Konfigurasi MQTT broker
├── node-red/
│   └── data/
│       ├── flows.json          # Node-RED automation flows
│       └── settings.js         # Node-RED settings
├── devices/
│   ├── Dockerfile              # Container image untuk devices
│   ├── run_device.py           # Device launcher
│   ├── utils.py                # MQTT helper functions
│   ├── temp_sensor.py          # Temperature sensor script
│   ├── motion_sensor.py        # Motion sensor script
│   └── smart_lamp.py           # Smart lamp actuator script
└── web_ui/                     # Enhanced Web Dashboard
    ├── index.html              # Dashboard UI
    ├── script.js               # Frontend logic
    ├── style.css               # Modern dark theme
    ├── mqtt_proxy.py           # MQTT-to-HTTP proxy server
    └── README.md               # Dashboard documentation
```

---

## 🚀 Cara Menjalankan

### Prasyarat
- Docker & Docker Compose terinstall
- WSL Ubuntu 24.04 atau Linux environment
- Port 1883 dan 1880 tersedia

### Langkah 1: Clone atau Setup Project

Pastikan Anda berada di direktori project:
```bash
cd /home/aulia/mqtt_smarthome
```

### Langkah 2: Build dan Jalankan Semua Container

```bash
# Build dan jalankan semua services
docker-compose up --build

# Atau jalankan di background (detached mode)
docker-compose up --build -d
```

### Langkah 3: Cek Status Container

```bash
# Lihat semua container yang berjalan
docker-compose ps

# Lihat logs semua services
docker-compose logs

# Lihat logs specific service
docker-compose logs -f temp_sensor
docker-compose logs -f mosquitto
docker-compose logs -f nodered
```

### Langkah 4: Akses Dashboard

Ada 2 pilihan dashboard untuk monitoring dan kontrol:

#### **Option A: Enhanced Web Dashboard (Recommended)** 🌐

Modern web-based dashboard dengan MQTT proxy API dan real-time visualization.

**Quick Start dengan Script:**
```bash
# Gunakan script otomatis
bash start-dashboard.sh

# Script akan:
# 1. Start MQTT Proxy (port 5000)
# 2. Start Web Server (port 8000)
# 3. Verify semua services
```

**Manual Start (Alternative):**
```bash
# 1. Start MQTT Proxy Server
cd web_ui
python3 mqtt_proxy.py &

# 2. Start Web Server (terminal baru)
cd web_ui
python3 -m http.server 8000

# 3. Buka browser:
http://localhost:8000
```

**Fitur Enhanced Dashboard:**
- 🛰️ **MQTT Proxy API**: HTTP bridge untuk MQTT data (port 5000)
- 📊 **Real-time Chart**: Temperature & motion trend dengan Chart.js
- 🎮 **Device Controls**: Light ON/OFF, brightness slider (0-100%)
- 🌡️ **Thermostat Card**: Mode, HVAC state, target temperature display
- 📹 **Camera Status**: Motion detection & recording indicator
- 📝 **Event Log**: Time-stamped activity table dengan auto-scroll
- 🎨 **Modern Dark Theme**: Professional UI dengan smooth animations
- 📱 **Responsive Design**: Works on desktop & mobile
- ✅ **Connection Status**: Real-time indicator dengan health check

**Architecture:**
```
Browser (port 8000) ──HTTP polling──> MQTT Proxy (port 5000) ──MQTT──> Mosquitto (port 1883)
```

**Detail lengkap:** Lihat [DASHBOARD_UPDATE.md](DASHBOARD_UPDATE.md)

#### **Option B: Node-RED Dashboard** 🔧

Built-in Node-RED dashboard untuk automation logic dan monitoring.

```
http://localhost:1880/ui
```

**Fitur Node-RED Dashboard:**
- 🌡️ Temperature Monitoring: Gauge real-time
- 🚶 Motion Detection: Status dengan visual indicator
- 💡 Smart Lamp Control: Switch interaktif
- 🔧 Flow Editor: Visual programming untuk automation
- 📝 Debug Console: Live MQTT message monitoring

---

## 🌐 Enhanced Web Dashboard

### Architecture Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                     Enhanced Dashboard System                    │
│                                                                   │
│  Browser (localhost:8000)                                        │
│       │                                                           │
│       │ HTTP Polling (1s interval)                               │
│       ▼                                                           │
│  MQTT Proxy Server (localhost:5000)                             │
│       │                                                           │
│       │ REST API Endpoints:                                      │
│       │  • GET /api/data        (all sensor data)               │
│       │  • GET /api/events      (event log)                     │
│       │  • GET /api/status      (connection status)             │
│       │  • POST /api/light/control (lamp commands)              │
│       │  • GET /health          (health check)                  │
│       │                                                           │
│       │ MQTT Subscribe/Publish                                   │
│       ▼                                                           │
│  Mosquitto Broker (localhost:1883)                              │
│       │                                                           │
│       └─► Devices: temp_sensor, motion_sensor, smart_lamp, etc. │
└─────────────────────────────────────────────────────────────────┘
```

### Quick Start Guide

**Automated Start (Recommended):**
```bash
cd /home/yrr/smarthome_mqtt
bash start-dashboard.sh
```

**Manual Start:**
```bash
# Terminal 1: Start MQTT Proxy
cd web_ui
python3 mqtt_proxy.py

# Terminal 2: Start Web Server
cd web_ui
python3 -m http.server 8000

# Browser: Open http://localhost:8000
```

### Features & Capabilities

#### 1. **Real-time Monitoring**
- Temperature sensor display (°C dengan 1 desimal)
- Motion detection indicator dengan alert
- Smart light status (ON/OFF + brightness %)
- Thermostat mode dan HVAC state
- Camera recording status

#### 2. **Device Control**
- Light ON/OFF toggle buttons
- Brightness slider (0-100%) dengan auto-update
- Future: Thermostat & camera controls

#### 3. **Data Visualization**
- Dual-axis Chart.js graph
- Temperature trend (left axis, yellow line)
- Motion events (right axis, green line)
- 30 data points rolling history
- Smooth animations

#### 4. **Event Logging**
- Time-stamped event table
- Source tracking (sensor/device names)
- Type classification (Sensor Data, Status Change)
- Auto-scroll to latest entry
- Maximum 50 entries display

#### 5. **Connection Status**
- Real-time connection indicator (header)
- Pulsing dot animation when connected
- Automatic reconnection handling
- Health check endpoint monitoring

### MQTT Topics Integration

**Subscribed Topics (Proxy → Broker):**
```
home/sensor/temperature       → Temperature Card
home/security/motion          → Motion Indicator
home/security/camera/status   → Camera Status
home/light/status             → Light Card
home/thermostat/status        → Thermostat Card
```

**Published Topics (Proxy → Broker):**
```
home/light/command            ← Light Control Buttons
home/thermostat/command       ← (Future) Thermostat Control
home/security/camera/command  ← (Future) Camera Control
```

### API Endpoints Reference

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/health` | GET | Health check | `{"status":"ok"}` |
| `/api/data` | GET | All sensor data | JSON with temp, motion, light, thermostat |
| `/api/events` | GET | Event log | Array of timestamped events |
| `/api/status` | GET | Connection status | MQTT connection state |
| `/api/light/control` | POST | Control light | `{"command":"ON","brightness":100}` |

### Testing Dashboard

**Test 1: Verify Proxy Health**
```bash
curl http://localhost:5000/health
# Expected: {"status":"ok"}
```

**Test 2: Check Real-time Data**
```bash
curl http://localhost:5000/api/data
# Expected: JSON dengan temperature, motion, light_status, dll
```

**Test 3: Control Light via API**
```bash
# Turn ON
curl -X POST http://localhost:5000/api/light/control \
  -H "Content-Type: application/json" \
  -d '{"command":"ON","brightness":80}'

# Turn OFF
curl -X POST http://localhost:5000/api/light/control \
  -H "Content-Type: application/json" \
  -d '{"command":"OFF"}'
```

**Test 4: Monitor MQTT Messages**
```bash
# Subscribe to all topics
mosquitto_sub -h localhost -t "home/#" -v
```

### Technical Stack
- **Backend**: Flask (MQTT Proxy Server)
- **MQTT Client**: paho-mqtt (Python)
- **Frontend**: Pure HTML5 + CSS3 + Vanilla JavaScript
- **Charts**: Chart.js 4.4.0
- **Styling**: Custom dark theme dengan CSS variables
- **Communication**: HTTP Polling (1 second interval)
- **Responsive**: Mobile-first design

### Troubleshooting Dashboard

**Problem: Dashboard shows "Disconnected"**
```bash
# Check proxy running
ps aux | grep mqtt_proxy

# Check proxy logs
tail -f .mqtt_proxy.log

# Restart proxy
pkill -f mqtt_proxy.py
cd web_ui && python3 mqtt_proxy.py &
```

**Problem: No data displayed**
```bash
# Verify MQTT broker running
docker-compose ps | grep mqtt_broker

# Check devices publishing
docker-compose logs temp_sensor motion_sensor

# Test proxy API
curl http://localhost:5000/api/data
```

**Problem: Controls not working**
```bash
# Check lamp device listening
docker-compose logs smart_lamp

# Monitor command topic
mosquitto_sub -h localhost -t "home/light/command" -v

# Test manual command
mosquitto_pub -h localhost -t "home/light/command" -m "ON"
```

### Dokumentasi Lengkap
Untuk dokumentasi detail, troubleshooting advanced, dan customization:
- **Dashboard Update Guide**: [DASHBOARD_UPDATE.md](DASHBOARD_UPDATE.md)
- **Web UI README**: [web_ui/README.md](web_ui/README.md)

---

## 🌐 Legacy Web Dashboard (Old)

⚠️ **Deprecated**: Dashboard lama telah digantikan dengan Enhanced Dashboard.

Dashboard lama (direktori `dashboard/`) menggunakan koneksi MQTT WebSocket langsung tanpa proxy. Fitur terbatas dibanding enhanced version.

---

## 🧪 Testing & Monitoring

### Test 1: Monitoring MQTT Messages

Install mosquitto clients (jika belum ada):
```bash
sudo apt-get update
sudo apt-get install mosquitto-clients
```

**Subscribe ke semua topics:**
```bash
mosquitto_sub -h localhost -t '#' -v
```

**Subscribe ke specific topics:**
```bash
# Monitor temperature
mosquitto_sub -h localhost -t 'home/sensor/temperature' -v

# Monitor motion
mosquitto_sub -h localhost -t 'home/sensor/motion' -v

# Monitor lamp status
mosquitto_sub -h localhost -t 'home/actuator/lamp/status' -v
```

### Test 2: Manual Control Lamp

**Turn ON lamp:**
```bash
mosquitto_pub -h localhost -t 'home/actuator/lamp/command' -m 'ON'
```

**Turn OFF lamp:**
```bash
mosquitto_pub -h localhost -t 'home/actuator/lamp/command' -m 'OFF'
```

### Test 3: Simulate Motion Detection

```bash
# Simulate motion detected
mosquitto_pub -h localhost -t 'home/sensor/motion' -m '{"value": 1, "status": "motion detected"}'

# Simulate no motion
mosquitto_pub -h localhost -t 'home/sensor/motion' -m '{"value": 0, "status": "no motion"}'
```

### Monitoring Container Health

```bash
# Check container stats (CPU, Memory, Network)
docker stats

# Check specific container logs
docker logs -f mqtt_broker
docker logs -f temp_sensor
docker logs -f motion_sensor
docker logs -f smart_lamp
```

---

## ⚙️ Konfigurasi Node-RED

### Langkah 1: Akses Node-RED UI

1. Buka browser: `http://localhost:1880`
2. Anda akan melihat Node-RED Flow Editor

### Langkah 2: Install Node Dashboard (Jika Belum Ada)

1. Klik menu ☰ (kanan atas) → **Manage palette**
2. Tab **Install**
3. Cari: `node-red-dashboard`
4. Klik **Install**

### Langkah 3: Konfigurasi MQTT Broker Connection

1. Drag node **mqtt in** ke canvas
2. Double-click node tersebut
3. Di **Server**, klik tombol pencil (edit)
4. Isi konfigurasi:
   - **Server**: `mosquitto`
   - **Port**: `1883`
   - **Client ID**: (kosongkan atau isi bebas)
   - **Keep Alive**: `60`
5. Klik **Add** / **Update**

### Langkah 4: Import Flow Automation

Copy JSON flow berikut dan import ke Node-RED:

**Cara Import:**
1. Klik menu ☰ → **Import**
2. Paste JSON di bawah
3. Klik **Import**

**JSON Flow:**

```json
[
    {
        "id": "mqtt_broker_config",
        "type": "mqtt-broker",
        "name": "Mosquitto Broker",
        "broker": "mosquitto",
        "port": "1883",
        "clientid": "",
        "autoConnect": true,
        "usetls": false,
        "protocolVersion": "4",
        "keepalive": "60",
        "cleansession": true,
        "birthTopic": "",
        "birthQos": "0",
        "birthPayload": "",
        "birthMsg": {},
        "closeTopic": "",
        "closeQos": "0",
        "closePayload": "",
        "closeMsg": {},
        "willTopic": "",
        "willQos": "0",
        "willPayload": "",
        "willMsg": {},
        "userProps": "",
        "sessionExpiry": ""
    },
    {
        "id": "motion_in",
        "type": "mqtt in",
        "z": "flow1",
        "name": "Motion Sensor",
        "topic": "home/sensor/motion",
        "qos": "1",
        "datatype": "json",
        "broker": "mqtt_broker_config",
        "nl": false,
        "rap": true,
        "rh": 0,
        "inputs": 0,
        "x": 120,
        "y": 200,
        "wires": [["parse_motion"]]
    },
    {
        "id": "parse_motion",
        "type": "json",
        "z": "flow1",
        "name": "Parse JSON",
        "property": "payload",
        "action": "",
        "pretty": false,
        "x": 310,
        "y": 200,
        "wires": [["motion_switch"]]
    },
    {
        "id": "motion_switch",
        "type": "switch",
        "z": "flow1",
        "name": "Motion Detected?",
        "property": "payload.value",
        "propertyType": "msg",
        "rules": [
            {
                "t": "eq",
                "v": "1",
                "vt": "num"
            },
            {
                "t": "eq",
                "v": "0",
                "vt": "num"
            }
        ],
        "checkall": "true",
        "repair": false,
        "outputs": 2,
        "x": 510,
        "y": 200,
        "wires": [["lamp_on"], ["lamp_off"]]
    },
    {
        "id": "lamp_on",
        "type": "change",
        "z": "flow1",
        "name": "Set ON",
        "rules": [
            {
                "t": "set",
                "p": "payload",
                "pt": "msg",
                "to": "ON",
                "tot": "str"
            }
        ],
        "action": "",
        "property": "",
        "from": "",
        "to": "",
        "reg": false,
        "x": 710,
        "y": 180,
        "wires": [["lamp_command"]]
    },
    {
        "id": "lamp_off",
        "type": "change",
        "z": "flow1",
        "name": "Set OFF",
        "rules": [
            {
                "t": "set",
                "p": "payload",
                "pt": "msg",
                "to": "OFF",
                "tot": "str"
            }
        ],
        "action": "",
        "property": "",
        "from": "",
        "to": "",
        "reg": false,
        "x": 710,
        "y": 220,
        "wires": [["lamp_command"]]
    },
    {
        "id": "lamp_command",
        "type": "mqtt out",
        "z": "flow1",
        "name": "Lamp Command",
        "topic": "home/actuator/lamp/command",
        "qos": "1",
        "retain": "false",
        "respTopic": "",
        "contentType": "",
        "userProps": "",
        "correl": "",
        "expiry": "",
        "broker": "mqtt_broker_config",
        "x": 930,
        "y": 200,
        "wires": []
    },
    {
        "id": "temp_in",
        "type": "mqtt in",
        "z": "flow1",
        "name": "Temperature",
        "topic": "home/sensor/temperature",
        "qos": "1",
        "datatype": "json",
        "broker": "mqtt_broker_config",
        "nl": false,
        "rap": true,
        "rh": 0,
        "inputs": 0,
        "x": 120,
        "y": 100,
        "wires": [["temp_display"]]
    },
    {
        "id": "temp_display",
        "type": "debug",
        "z": "flow1",
        "name": "Temperature Debug",
        "active": true,
        "tosidebar": true,
        "console": false,
        "tostatus": false,
        "complete": "payload",
        "targetType": "msg",
        "statusVal": "",
        "statusType": "auto",
        "x": 350,
        "y": 100,
        "wires": []
    },
    {
        "id": "lamp_status_in",
        "type": "mqtt in",
        "z": "flow1",
        "name": "Lamp Status",
        "topic": "home/actuator/lamp/status",
        "qos": "1",
        "datatype": "json",
        "broker": "mqtt_broker_config",
        "nl": false,
        "rap": true,
        "rh": 0,
        "inputs": 0,
        "x": 120,
        "y": 300,
        "wires": [["lamp_status_display"]]
    },
    {
        "id": "lamp_status_display",
        "type": "debug",
        "z": "flow1",
        "name": "Lamp Status Debug",
        "active": true,
        "tosidebar": true,
        "console": false,
        "tostatus": false,
        "complete": "payload",
        "targetType": "msg",
        "statusVal": "",
        "statusType": "auto",
        "x": 360,
        "y": 300,
        "wires": []
    }
]
```

### Langkah 5: Deploy Flow

Klik tombol **Deploy** (kanan atas)

### Langkah 6: Verifikasi Flow Berjalan

1. Buka tab **Debug** (kanan, ikon bug)
2. Anda akan melihat messages dari temperature sensor dan lamp status
3. Saat motion detected, lamp akan otomatis ON
4. Saat no motion, lamp akan otomatis OFF

---

## 🎨 Membuat Dashboard di Node-RED

### Install Dashboard Nodes

1. Menu ☰ → **Manage palette** → **Install**
2. Cari: `node-red-dashboard`
3. Install

### Tambah Dashboard Widgets

Tambahkan nodes berikut ke flow:

**1. Temperature Gauge:**
- Node: **gauge**
- Topic: dari `home/sensor/temperature` (gunakan mqtt in)
- Extract value: gunakan **change** node untuk extract `msg.payload.value`

**2. Motion Indicator:**
- Node: **text** atau **LED**
- Input: dari `home/sensor/motion`

**3. Lamp Control:**
- Node: **switch** (toggle)
- Output: ke `home/actuator/lamp/command`

**4. Lamp Status Indicator:**
- Node: **text** atau **LED**
- Input: dari `home/actuator/lamp/status`

Akses dashboard di:
```
http://localhost:1880/ui
```

---

## 🛠️ Troubleshooting

### Problem 1: Port Already in Use

**Error:**
```
Error: bind: address already in use
```

**Solusi:**
```bash
# Cek port yang digunakan
sudo netstat -tulpn | grep :1883
sudo netstat -tulpn | grep :1880

# Kill process yang menggunakan port
sudo kill -9 <PID>

# Atau ubah port di docker-compose.yml
# Contoh: "1884:1883" untuk MQTT
```

### Problem 2: Permission Denied

**Error:**
```
Permission denied: mosquitto.conf
```

**Solusi:**
```bash
# Set permission yang benar
chmod 644 mosquitto/mosquitto.conf
chmod -R 755 node-red/data

# Atau gunakan sudo
sudo docker-compose up --build
```

### Problem 3: Container Tidak Bisa Connect ke Mosquitto

**Error di logs:**
```
Connection refused
```

**Solusi:**

1. Cek mosquitto container berjalan:
```bash
docker-compose ps
```

2. Cek logs mosquitto:
```bash
docker-compose logs mosquitto
```

3. Pastikan healthcheck passed:
```bash
docker inspect mqtt_broker | grep -A 10 Health
```

4. Test koneksi dari container lain:
```bash
docker-compose exec temp_sensor ping mosquitto
```

### Problem 4: Node-RED Tidak Bisa Connect ke Mosquitto

**Solusi:**

1. Pastikan hostname di Node-RED config adalah `mosquitto` (bukan `localhost`)
2. Pastikan kedua container dalam network yang sama
3. Restart Node-RED:
```bash
docker-compose restart nodered
```

### Problem 5: Device Tidak Publish Data

**Solusi:**

1. Cek logs device:
```bash
docker-compose logs temp_sensor
docker-compose logs motion_sensor
```

2. Pastikan environment variables sudah benar di `docker-compose.yml`

3. Restart device container:
```bash
docker-compose restart temp_sensor
```

### Problem 6: Data Tidak Muncul di Node-RED

**Solusi:**

1. Cek topic di MQTT in node sudah benar
2. Lihat debug messages di Node-RED (tab Debug)
3. Test subscribe manual:
```bash
mosquitto_sub -h localhost -t '#' -v
```

---

## 🧹 Menghentikan dan Membersihkan

### Stop Semua Container

```bash
# Stop tanpa menghapus
docker-compose stop

# Stop dan hapus container
docker-compose down

# Stop, hapus container dan volumes
docker-compose down -v

# Stop, hapus container, volumes, dan images
docker-compose down -v --rmi all
```

### Restart Specific Service

```bash
docker-compose restart mosquitto
docker-compose restart nodered
docker-compose restart temp_sensor
```

### Rebuild Specific Service

```bash
docker-compose up --build --no-deps temp_sensor
```

---

## 📊 Monitoring Resources

```bash
# Real-time resource usage
docker stats

# Disk usage
docker system df

# Network info
docker network inspect mqtt_smarthome_smarthome_network

# Volume info
docker volume ls
docker volume inspect mqtt_smarthome_mosquitto_data
```

---

## 📚 Referensi

### MQTT Topics Structure

```
home/
├── sensor/
│   └── temperature          (publish: temp_sensor)
├── security/
│   ├── motion               (publish: motion_sensor)
│   └── camera/
│       └── status           (publish: camera device)
├── light/
│   ├── command              (subscribe: smart_lamp)
│   └── status               (publish: smart_lamp)
└── thermostat/
    ├── command              (subscribe: thermostat)
    └── status               (publish: thermostat)
```

**Legacy Topics (Old System):**
```
home/
├── sensor/
│   ├── temperature
│   └── motion
└── actuator/
    └── lamp/
        ├── command
        └── status
```

### Environment Variables untuk Devices

| Variable | Description | Default |
|----------|-------------|---------|
| DEVICE_TYPE | Jenis device | - |
| BROKER | Hostname MQTT broker | mosquitto |
| PORT | MQTT port | 1883 |
| CLIENT_ID | Unique client identifier | - |
| TOPIC | MQTT topic | - |
| INTERVAL | Publish interval (seconds) | - |

### Docker Compose Commands Cheatsheet

```bash
# Build dan start
docker-compose up --build

# Start di background
docker-compose up -d

# Stop
docker-compose stop

# Remove
docker-compose down

# Logs
docker-compose logs -f [service]

# List containers
docker-compose ps

# Execute command in container
docker-compose exec [service] [command]

# Scale service
docker-compose up --scale temp_sensor=2
```

---

## 🎯 Pengembangan Selanjutnya

Ide untuk pengembangan project:

1. **Tambah device baru**: humidity sensor, door sensor, AC control
2. **Implementasi autentikasi MQTT**: username & password
3. **Database integration**: simpan data sensor ke InfluxDB atau MongoDB
4. **Grafana dashboard**: visualisasi data time-series
5. **Alert system**: notifikasi via Telegram/Email
6. **Machine Learning**: predictive automation based on historical data
7. **MQTT over TLS**: enkripsi komunikasi
8. **Rule engine**: automation rules yang lebih kompleks
9. **Mobile app**: Flutter/React Native untuk kontrol
10. **Voice control**: integrasi dengan Google Assistant/Alexa

---

## 👥 Credits

Project ini dibuat untuk tugas Sistem Terdistribusi.

**Technologies:**
- Docker & Docker Compose
- Eclipse Mosquitto (MQTT Broker)
- Node-RED
- Python (paho-mqtt)
- WSL Ubuntu

---

## 📝 License

MIT License - Free to use for educational purposes

---

**Selamat Mencoba! 🚀**

Jika ada pertanyaan atau issue, silakan cek troubleshooting section atau lihat logs container untuk debugging.
