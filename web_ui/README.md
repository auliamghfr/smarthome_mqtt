# 🌐 Smart Home Web Dashboard

Dashboard web modern real-time untuk monitoring dan kontrol sistem Smart Home berbasis MQTT.

## 🎯 Fitur

### 📊 Real-time Monitoring
- **Temperature Card**: Menampilkan suhu ruangan saat ini dengan gauge visual
- **Motion Detection Card**: Status motion sensor dengan indikator animasi
- **Smart Lamp Card**: Status lampu (ON/OFF) dengan icon dinamis
- **Real-time Chart**: Line chart multi-series untuk temperature dan motion history (30 data points terakhir)

### 🎮 Control Panel
- **Lamp ON/OFF Buttons**: Kontrol lampu dengan tombol dedicated
- **Brightness Slider**: Adjust brightness lampu (0-100%)
- **Visual Feedback**: Indikator real-time status lampu

### 📝 Event Log
- **Activity Table**: Log semua events dari sensors dan actuators
- **Auto-scroll**: Automatically scroll to latest entry
- **Max 100 entries**: Automatically trim old entries
- **Columns**: Time | Source | Type | Value

### 🎨 Design Features
- **Dark Theme**: Modern dark UI dengan gradient background
- **Responsive Layout**: Optimal untuk desktop dan mobile
- **Real-time Updates**: Data update otomatis via MQTT WebSocket
- **Smooth Animations**: Transitions dan hover effects

---

## 🚀 Cara Menjalankan

### Prasyarat
1. **Docker & Docker Compose** sudah running
2. **MQTT Broker** (Mosquitto) dengan WebSocket enabled di port 9001
3. **IoT Devices** (temp_sensor, motion_sensor, smart_lamp) sudah berjalan

### Langkah 1: Start Sistem Backend

```bash
cd /home/aulia/mqtt_smarthome
docker-compose up -d
```

Tunggu sampai semua containers running:
```bash
docker-compose ps
```

### Langkah 2: Buka Web Dashboard

**Option A: Langsung buka file HTML**
```bash
# Buka di browser default
xdg-open web_ui/index.html

# Atau manual:
# 1. Buka browser (Chrome/Firefox)
# 2. File → Open File
# 3. Pilih: /home/aulia/mqtt_smarthome/web_ui/index.html
```

**Option B: Gunakan HTTP Server (Recommended)**
```bash
# Dengan Python
cd web_ui
python3 -m http.server 8000

# Buka browser:
# http://localhost:8000
```

**Option C: Gunakan Live Server (VS Code)**
1. Install extension "Live Server" di VS Code
2. Right-click pada `index.html`
3. Pilih "Open with Live Server"

### Langkah 3: Verifikasi Koneksi

Setelah dashboard terbuka:

1. **Cek Connection Status** (header kanan atas)
   - ✅ "Connected" = Berhasil connect ke MQTT broker
   - ⚠️ "Connecting..." = Sedang mencoba connect
   - ❌ "Offline" = Gagal connect

2. **Cek Data Real-time**
   - Temperature card harus update setiap 5 detik
   - Motion status harus update setiap 3 detik
   - Chart harus bertambah data point secara real-time

3. **Test Kontrol Lampu**
   - Klik "Turn ON" → Lampu harus menyala
   - Klik "Turn OFF" → Lampu harus mati
   - Adjust brightness slider → Brightness harus berubah

---

## 🔧 Troubleshooting

### Problem: "Connection Failed" atau "Offline"

**Solusi 1: Cek Mosquitto WebSocket**
```bash
# Cek apakah port 9001 terbuka
netstat -tuln | grep 9001

# Atau
ss -tuln | grep 9001

# Harus ada output seperti:
# tcp  0  0  0.0.0.0:9001  0.0.0.0:*  LISTEN
```

**Solusi 2: Restart Mosquitto**
```bash
docker-compose restart mosquitto
```

**Solusi 3: Cek Mosquitto Config**
File `mosquitto/mosquitto.conf` harus punya:
```
listener 9001
protocol websockets
```

**Solusi 4: Cek Browser Console**
1. Tekan F12 → tab Console
2. Lihat error messages
3. Jika ada error CORS atau WebSocket, gunakan HTTP server (bukan buka file langsung)

### Problem: Data tidak update

**Solusi 1: Cek IoT Devices**
```bash
# Cek logs devices
docker-compose logs -f temp_sensor
docker-compose logs -f motion_sensor
docker-compose logs -f smart_lamp

# Harus ada output seperti:
# "Published: 25.3°C to home/sensor/temperature"
```

**Solusi 2: Test MQTT Manual**
```bash
# Subscribe ke semua topics
mosquitto_sub -h localhost -t 'home/#' -v

# Harus muncul messages real-time
```

**Solusi 3: Hard Refresh Browser**
```
Ctrl + Shift + R
```

### Problem: Chart tidak muncul

**Solusi:**
1. Cek browser console untuk error Chart.js
2. Pastikan internet connection aktif (Chart.js loaded dari CDN)
3. Wait 30 seconds untuk data points terkumpul

### Problem: Control lampu tidak bekerja

**Solusi 1: Cek MQTT Connection**
Dashboard harus status "Connected"

**Solusi 2: Cek Smart Lamp Container**
```bash
docker-compose logs -f smart_lamp

# Harus muncul:
# "Received command: ON"
# "Published status: ON"
```

**Solusi 3: Test Manual**
```bash
# Test command
mosquitto_pub -h localhost -t 'home/actuator/lamp/command' -m 'ON'

# Cek status
mosquitto_sub -h localhost -t 'home/actuator/lamp/status' -C 1
```

---

## 📁 Struktur File

```
web_ui/
├── index.html          # Dashboard HTML structure
├── script.js           # MQTT logic & DOM manipulation
├── style.css           # Dark theme styling
└── README.md           # Dokumentasi ini
```

---

## 🎨 Customization

### Ubah Warna Tema

Edit `style.css`:
```css
:root {
    --bg-primary: #0f172a;        /* Background utama */
    --accent-cyan: #06b6d4;       /* Aksen warna */
    --accent-green: #10b981;      /* Motion active */
    --accent-yellow: #f59e0b;     /* Temperature/Lamp */
}
```

### Ubah MQTT Broker URL

Edit `script.js`:
```javascript
const MQTT_BROKER = 'ws://localhost:9001';  // Ganti sesuai broker Anda
```

### Ubah Jumlah Data Points Chart

Edit `script.js`:
```javascript
const MAX_DATA_POINTS = 30;  // Default 30 points
```

### Ubah Max Log Entries

Edit `script.js`:
```javascript
const MAX_LOG_ENTRIES = 100;  // Default 100 entries
```

---

## 📊 MQTT Topics yang Digunakan

| Topic | Direction | Format | Deskripsi |
|-------|-----------|--------|-----------|
| `home/sensor/temperature` | Subscribe | `{"sensor":"temperature","value":25.3,"unit":"°C"}` | Data suhu |
| `home/sensor/motion` | Subscribe | `{"sensor":"motion","value":1,"status":"motion detected"}` | Data motion |
| `home/actuator/lamp/status` | Subscribe | `{"state":"ON","timestamp":...}` | Status lampu |
| `home/actuator/lamp/command` | Publish | `"ON"` atau `"OFF"` | Kontrol lampu |
| `home/actuator/lamp/brightness` | Publish | `"0"` - `"100"` | Brightness lampu |

---

## 🌟 Fitur Lanjutan (Future Enhancement)

- [ ] Add authentication (username/password)
- [ ] Add SSL/TLS support untuk WebSocket
- [ ] Add notification alerts untuk motion detection
- [ ] Add temperature history export (CSV/JSON)
- [ ] Add multiple room support
- [ ] Add dark/light theme toggle
- [ ] Add responsive mobile app (PWA)

---

## 📝 Lisensi

MIT License - Free to use and modify

---

## 🆘 Support

Jika ada masalah:
1. Cek troubleshooting section di atas
2. Lihat browser console (F12)
3. Cek Docker logs: `docker-compose logs`
4. Cek MQTT messages: `mosquitto_sub -h localhost -t '#' -v`

---

**🎉 Selamat! Dashboard Smart Home MQTT Anda siap digunakan!**
