# Smart Home Automation System - MQTT IoT Project

Sistem Smart Home berbasis IoT menggunakan MQTT protocol, Docker, Node-RED, dan Python.

🔥 **Automation Aktif:** Lampu menyala otomatis saat motion detected, mati saat no motion.

## ⚡ Quick Start

```bash
# 1. Clone dan masuk ke direktori
cd /home/yrr/smarthome_mqtt

# 2. Start semua services
docker-compose up -d

# 3. Start web dashboard
cd dashboard && python3 -m http.server 8080 &

# 4. Akses dashboard
# Web Dashboard: http://localhost:8080
# Node-RED Editor: http://localhost:1880

# 5. Monitor automation
docker exec mqtt_broker mosquitto_sub -t 'home/#' -v
```

✅ **Expected Result:** Lampu otomatis ON saat motion detected, OFF saat no motion.

........................................................................................

## 📋 Daftar Isi

- [Arsitektur Sistem](#arsitektur-sistem)
- [Komponen Sistem](#komponen-sistem)
- [Automation Logic](#-automation-logic)
- [Struktur Project](#struktur-project)
- [Cara Menjalankan](#cara-menjalankan)
- [Akses Dashboard](#-akses-dashboard)
- [Testing & Monitoring](#testing--monitoring)
- [Troubleshooting](#troubleshooting)
- [Referensi](#referensi)

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network                            │
│  ┌──────────────┐     ┌──────────────┐                      │
│  │ Temperature  │────▶│              │                       │
│  │   Sensor     │     │   Mosquitto  │◀────┐                │
│  └──────────────┘     │     Broker   │     │                │
│                       │   (MQTT)     │     │                │
│  ┌──────────────┐     │  Port 1883   │     │                │
│  │   Motion     │────▶│  Port 9001   │     │                │
│  │   Sensor     │     │  (WebSocket) │     │                │
│  └──────────────┘     └──────────────┘     │                │
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
- WebSocket enabled untuk web dashboard

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
- Publish ke: `home/sensor/motion`
- Interval: 3 detik
- Data: Status gerakan (0/1)

### 5. **Smart Lamp**
- Bahasa: Python 3.11
- Subscribe: `home/actuator/lamp/command`
- Publish: `home/actuator/lamp/status`
- Command: ON/OFF

---

## 🤖 Automation Logic

### Motion-Based Lamp Control

Sistem automation saat ini menggunakan **motion sensor** untuk mengontrol lampu secara otomatis:

**Logic:**
```
✅ Motion Detected (value = 1) → Lamp ON
❌ No Motion (value = 0) → Lamp OFF
```

**Karakteristik:**
- ⚡ **Instant Response**: Lampu langsung menyala/mati tanpa delay
- 🔄 **Real-time**: Response time < 100ms
- 🎯 **Simple & Reliable**: Logika sederhana tanpa kompleksitas

**Flow di Node-RED:**
```
Motion Sensor → Check Value → Switch (1/0) → Set ON/OFF → Lamp Command
```

**Topics:**
- Input: `home/sensor/motion` - Data motion sensor
- Output: `home/actuator/lamp/command` - Command ON/OFF ke lampu
- Feedback: `home/actuator/lamp/status` - Status lampu saat ini

📖 **Dokumentasi lengkap:** Lihat [AUTOMATION.md](AUTOMATION.md)

---

## 📁 Struktur Project

```
smarthome_mqtt/
├── docker-compose.yml          # Orchestration semua services
├── README.md                   # Dokumentasi ini
├── AUTOMATION.md               # Dokumentasi automation lengkap
├── QUICKSTART.md               # Quick start guide
├── mosquitto/
│   └── mosquitto.conf          # Konfigurasi MQTT broker + WebSocket
├── node-red/
│   └── data/
│       ├── flows.json          # Node-RED automation flow (ignored)
│       ├── package.json        # Node-RED dependencies
│       └── settings.js         # Node-RED settings
├── dashboard/
│   └── index.html              # Web dashboard (WebSocket)
└── devices/
    ├── Dockerfile              # Container image untuk devices
    ├── run_device.py           # Device launcher
    ├── utils.py                # MQTT helper functions
    ├── temp_sensor.py          # Temperature sensor script
    ├── motion_sensor.py        # Motion sensor script
    └── smart_lamp.py           # Smart lamp actuator script
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
cd /home/yrr/smarthome_mqtt
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

### Langkah 4: Akses Node-RED Dashboard

Buka browser dan akses:
```
http://localhost:1880
```

---

## 🌐 Akses Dashboard

Setelah semua container berjalan, Anda dapat mengakses:

### 1. Web Dashboard (Recommended)

**URL:** `http://localhost:8080`

**Fitur:**
- 🌡️ Real-time temperature gauge
- 👁️ Motion detection status
- 💡 Lamp status indicator
- 🎛️ Manual lamp control switch

**Menjalankan Dashboard:**
```bash
# Dari terminal terpisah
cd /home/yrr/smarthome_mqtt/dashboard
python3 -m http.server 8080
```

**Screenshot Dashboard:**
- Temperature display dengan gauge visual
- Motion sensor: "Motion Detected" atau "No Motion"
- Lamp status: ON (hijau) atau OFF (merah)
- Toggle switch untuk kontrol manual

### 2. Node-RED Editor

**URL:** `http://localhost:1880`

**Fitur:**
- Edit automation flow
- View debug messages
- Monitor MQTT traffic
- Modify logic tanpa coding

**Tab Available:**
- **Motion Automation**: Flow automation motion → lamp

### 3. Node-RED Dashboard (Optional)

**URL:** `http://localhost:1880/ui`

**Note:** UI dashboard mungkin tidak menampilkan widget dengan benar. Gunakan Web Dashboard (port 8080) untuk monitoring yang lebih reliable.

---

## 🧪 Testing & Monitoring

### Test 1: Monitoring MQTT Messages

**Metode 1: Menggunakan docker exec (Recommended)**

```bash
# Subscribe ke semua topics
docker exec mqtt_broker mosquitto_sub -t '#' -v

# Monitor temperature
docker exec mqtt_broker mosquitto_sub -t 'home/sensor/temperature'

# Monitor motion
docker exec mqtt_broker mosquitto_sub -t 'home/sensor/motion'

# Monitor lamp
docker exec mqtt_broker mosquitto_sub -t 'home/actuator/lamp/#' -v
```

**Metode 2: Install mosquitto clients di host (Optional)**

```bash
sudo apt-get update
sudo apt-get install mosquitto-clients

# Subscribe ke semua topics
mosquitto_sub -h localhost -t '#' -v
```

### Test 2: Manual Control Lamp

**Metode 1: Menggunakan docker exec**
```bash
# Turn ON lamp
docker exec mqtt_broker mosquitto_pub -t 'home/actuator/lamp/command' -m 'ON'

# Turn OFF lamp
docker exec mqtt_broker mosquitto_pub -t 'home/actuator/lamp/command' -m 'OFF'
```

**Metode 2: Dari host (jika mosquitto-clients terinstall)**
```bash
# Turn ON lamp
mosquitto_pub -h localhost -t 'home/actuator/lamp/command' -m 'ON'

# Turn OFF lamp
mosquitto_pub -h localhost -t 'home/actuator/lamp/command' -m 'OFF'
```

### Test 3: Simulate Motion Detection

```bash
# Simulate motion detected
docker exec mqtt_broker mosquitto_pub -t 'home/sensor/motion' \
  -m '{"sensor":"motion","value":1,"status":"motion detected"}'

# Simulate no motion
docker exec mqtt_broker mosquitto_pub -t 'home/sensor/motion' \
  -m '{"sensor":"motion","value":0,"status":"no motion"}'

# Expected result:
# - Motion detected → Lamp turns ON immediately
# - No motion → Lamp turns OFF immediately
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

## ⚙️ Verifikasi Automation di Node-RED

### Akses Node-RED Editor

```
http://localhost:1880
```

### Melihat Automation Flow

1. Buka browser dan akses Node-RED
2. Klik tab **"Motion Automation"**
3. Anda akan melihat flow:

```
[Motion Sensor In] → [Motion Value] → [ON/OFF] → [Lamp Command Out]
```

### Node Configuration

**MQTT Broker Config:**
- Server: `mosquitto`
- Port: `1883`
- Client ID: `nodered_automation`

**Flow Nodes:**

1. **Motion Sensor In** (MQTT In)
   - Topic: `home/sensor/motion`
   - QoS: 0
   - Datatype: JSON

2. **Motion Value** (Switch)
   - Property: `msg.payload.value`
   - Output 1: value == 1 (motion)
   - Output 2: value == 0 (no motion)

3. **ON / OFF** (Change)
   - Set `msg.payload` to `"ON"` or `"OFF"`

4. **Lamp Command Out** (MQTT Out)
   - Topic: `home/actuator/lamp/command`
   - QoS: 1

### Debug Messages

1. Klik tab **Debug** (sidebar kanan, icon bug)
2. Anda akan melihat real-time messages dari sensors
3. Verify automation working:
   - Motion detected → Command ON sent
   - No motion → Command OFF sent

### Modifikasi Automation

Untuk mengubah logic:

1. Double-click node yang ingin diubah
2. Edit konfigurasi
3. Klik **Done**
4. Klik **Deploy** (tombol merah kanan atas)

**Contoh modifikasi:**
- Tambah delay sebelum lamp OFF
- Kombinasi dengan temperature sensor
- Tambah time-based rules (malam/siang)

---

## 🎨 Import Flow Automation (Optional)

Jika flow belum ada, import JSON berikut:

**Cara Import:**
1. Menu ☰ → **Import**
2. Paste JSON
3. **Import**
4. **Deploy**

**Simple Flow JSON:**

```json
[
    {"id":"automation_tab","type":"tab","label":"Motion Automation","disabled":false,"info":""},
    {"id":"mqtt_broker","type":"mqtt-broker","name":"MQTT Broker","broker":"mosquitto","port":"1883","clientid":"nodered_automation","autoConnect":true,"usetls":false,"protocolVersion":"4","keepalive":"60","cleansession":true},
    {"id":"motion_in","type":"mqtt in","z":"automation_tab","name":"Motion Sensor In","topic":"home/sensor/motion","qos":"0","datatype":"json","broker":"mqtt_broker","x":140,"y":100,"wires":[["check_motion"]]},
    {"id":"check_motion","type":"switch","z":"automation_tab","name":"Motion Value","property":"payload.value","propertyType":"msg","rules":[{"t":"eq","v":"1","vt":"num"},{"t":"eq","v":"0","vt":"num"}],"outputs":2,"x":340,"y":100,"wires":[["lamp_on"],["lamp_off"]]},
    {"id":"lamp_on","type":"change","z":"automation_tab","name":"ON","rules":[{"t":"set","p":"payload","pt":"msg","to":"ON","tot":"str"}],"x":510,"y":80,"wires":[["lamp_out"]]},
    {"id":"lamp_off","type":"change","z":"automation_tab","name":"OFF","rules":[{"t":"set","p":"payload","pt":"msg","to":"OFF","tot":"str"}],"x":510,"y":120,"wires":[["lamp_out"]]},
    {"id":"lamp_out","type":"mqtt out","z":"automation_tab","name":"Lamp Command Out","topic":"home/actuator/lamp/command","qos":"1","broker":"mqtt_broker","x":690,"y":100,"wires":[]
]
```

**Note:** Flow sudah ter-deploy otomatis saat container start. Tidak perlu import manual kecuali flow hilang atau corrupt.

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
docker network inspect smarthome_mqtt_smarthome_network

# Volume info
docker volume ls
docker volume inspect smarthome_mqtt_mosquitto_data
```

---

## 📚 Referensi

### MQTT Topics Structure

```
home/
├── sensor/
│   ├── temperature      (publish only)
│   └── motion           (publish only)
└── actuator/
    └── lamp/
        ├── command      (subscribe)
        └── status       (publish)
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

### 1. Automation Enhancement
- [ ] Tambah delay OFF (lamp tetap ON 10-30 detik setelah motion stop)
- [ ] Kombinasi temperature + motion (lamp ON jika suhu > 30°C OR motion)
- [ ] Time-based rules (automation berbeda untuk siang/malam)
- [ ] Schedule automation (lamp ON/OFF otomatis di jam tertentu)

### 2. Device Baru
- [ ] Humidity sensor
- [ ] Door/window sensor
- [ ] AC/fan control
- [ ] Smoke detector
- [ ] Light intensity sensor

### 3. Security & Monitoring
- [ ] MQTT authentication (username & password)
- [ ] MQTT over TLS/SSL
- [ ] User access control
- [ ] Audit log

### 4. Data Analytics
- [ ] Database integration (InfluxDB/MongoDB)
- [ ] Grafana dashboard untuk historical data
- [ ] Data visualization & trends
- [ ] Energy consumption tracking

### 5. Notification & Alert
- [ ] Telegram bot notification
- [ ] Email alerts
- [ ] Push notification mobile
- [ ] Alert rules (temperature too high, motion at night, dll)

### 6. Advanced Features
- [ ] Machine Learning prediction
- [ ] Voice control (Google Assistant/Alexa)
- [ ] Mobile app (Flutter/React Native)
- [ ] Geofencing (auto ON/OFF based on location)
- [ ] Scene/preset automation

### 7. Dashboard Improvement
- [ ] Chart real-time dengan history
- [ ] Responsive design untuk mobile
- [ ] Dark mode
- [ ] Custom themes
- [ ] Widget drag & drop

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
