# 🚀 Quick Start Guide - Smart Home System

## Langkah Cepat Menjalankan Project

### 1️⃣ Pastikan Docker Berjalan

```bash
# Cek status Docker
docker --version
docker-compose --version

# Jika belum running, start Docker Desktop atau daemon
```

### 2️⃣ Jalankan Sistem

```bash
cd /home/aulia/mqtt_smarthome

# Opsi 1: Menggunakan script manage.sh (RECOMMENDED)
./manage.sh start

# Opsi 2: Menggunakan docker-compose langsung
docker-compose up --build -d
```

### 3️⃣ Verifikasi Container Berjalan

```bash
# Lihat status semua container
docker-compose ps

# Atau dengan manage script
./manage.sh status
```

Output yang diharapkan:
```
NAME                IMAGE                      STATUS
mqtt_broker         eclipse-mosquitto:2.0      Up (healthy)
node_red            nodered/node-red:latest    Up
temp_sensor         mqtt_smarthome-temp_sensor Up
motion_sensor       mqtt_smarthome-motion_sensor Up
smart_lamp          mqtt_smarthome-lamp        Up
```

### 4️⃣ Akses Node-RED

Buka browser:
- **Node-RED Editor**: http://localhost:1880
- **Dashboard** (setelah dikonfigurasi): http://localhost:1880/ui

### 5️⃣ Import Flow ke Node-RED

1. Buka http://localhost:1880
2. Klik menu ☰ (hamburger, kanan atas)
3. Pilih **Import**
4. Pilih tab **select a file to import**
5. Browse dan pilih file: `/home/aulia/mqtt_smarthome/nodered-flow.json`
6. Klik **Import**
7. Klik tombol **Deploy** (merah, kanan atas)

### 6️⃣ Test MQTT Communication

**Cara 1: Lihat Debug di Node-RED**
1. Di Node-RED, klik tab **Debug** (ikon bug, sidebar kanan)
2. Anda akan melihat messages dari sensors

**Cara 2: Gunakan mosquitto_sub**

```bash
# Install mosquitto clients jika belum ada
sudo apt-get update && sudo apt-get install -y mosquitto-clients

# Subscribe ke semua topics
mosquitto_sub -h localhost -t '#' -v

# Atau subscribe ke topic spesifik
mosquitto_sub -h localhost -t 'home/sensor/temperature' -v
mosquitto_sub -h localhost -t 'home/sensor/motion' -v
mosquitto_sub -h localhost -t 'home/actuator/lamp/status' -v
```

### 7️⃣ Test Manual Control Lamp

**Cara 1: Via Terminal**
```bash
# Turn ON lamp
mosquitto_pub -h localhost -t 'home/actuator/lamp/command' -m 'ON'

# Turn OFF lamp
mosquitto_pub -h localhost -t 'home/actuator/lamp/command' -m 'OFF'
```

**Cara 2: Via Node-RED**
1. Di flow editor Node-RED
2. Klik tombol di node "Manual ON" atau "Manual OFF"
3. Lihat hasilnya di Debug panel

---

## 📊 Monitoring Logs

```bash
# Lihat logs semua container
docker-compose logs -f

# Atau dengan manage script
./manage.sh logs

# Lihat logs container tertentu
docker-compose logs -f temp_sensor
docker-compose logs -f motion_sensor
docker-compose logs -f smart_lamp
docker-compose logs -f mosquitto
```

---

## 🛑 Menghentikan Sistem

```bash
# Opsi 1: Menggunakan manage script
./manage.sh stop

# Opsi 2: Langsung dengan docker-compose
docker-compose stop

# Untuk menghapus container sepenuhnya
docker-compose down

# Hapus container + volumes
docker-compose down -v
```

---

## 🔄 Restart Sistem

```bash
# Restart semua container
./manage.sh restart

# Atau
docker-compose restart

# Restart container tertentu
docker-compose restart temp_sensor
```

---

## 🧪 Testing Scenarios

### Scenario 1: Motion Detection Auto Lamp

1. Lihat logs motion sensor: `docker-compose logs -f motion_sensor`
2. Tunggu sampai muncul "motion detected"
3. Lihat logs lamp: `docker-compose logs -f smart_lamp`
4. Lamp seharusnya otomatis ON
5. Tunggu "no motion"
6. Lamp seharusnya otomatis OFF

### Scenario 2: Temperature Monitoring

1. Subscribe ke temperature topic:
   ```bash
   mosquitto_sub -h localhost -t 'home/sensor/temperature' -v
   ```
2. Anda akan melihat data suhu setiap 5 detik
3. Di Node-RED Debug panel juga akan muncul data yang sama

### Scenario 3: Manual Lamp Control

1. Pastikan lamp dalam status OFF
2. Kirim command ON:
   ```bash
   mosquitto_pub -h localhost -t 'home/actuator/lamp/command' -m 'ON'
   ```
3. Subscribe ke lamp status:
   ```bash
   mosquitto_sub -h localhost -t 'home/actuator/lamp/status' -v
   ```
4. Anda akan melihat status berubah menjadi ON

---

## 🐛 Quick Troubleshooting

### Problem: Port sudah digunakan

```bash
# Cek port 1883 (MQTT)
sudo lsof -i :1883
# Kill process jika ada

# Cek port 1880 (Node-RED)
sudo lsof -i :1880
# Kill process jika ada
```

### Problem: Container tidak start

```bash
# Lihat logs untuk error
docker-compose logs mosquitto
docker-compose logs temp_sensor

# Rebuild container
docker-compose up --build --force-recreate
```

### Problem: Device tidak bisa connect ke broker

```bash
# Pastikan mosquitto healthy
docker-compose ps

# Cek network connectivity
docker-compose exec temp_sensor ping mosquitto

# Restart mosquitto
docker-compose restart mosquitto

# Tunggu beberapa detik, lalu restart devices
docker-compose restart temp_sensor motion_sensor lamp
```

---

## 📝 Perintah Berguna

```bash
# Lihat semua perintah manage.sh
./manage.sh

# Cek resource usage containers
docker stats

# Masuk ke container (debugging)
docker-compose exec mosquitto sh
docker-compose exec temp_sensor bash

# Rebuild specific service
docker-compose up --build --no-deps temp_sensor

# Lihat network info
docker network ls
docker network inspect mqtt_smarthome_smarthome_network
```

---

## ✅ Checklist Verifikasi

- [ ] Docker dan Docker Compose terinstall
- [ ] Semua 5 container running (mosquitto, nodered, temp_sensor, motion_sensor, lamp)
- [ ] Mosquitto status: **healthy**
- [ ] Bisa akses Node-RED di http://localhost:1880
- [ ] Flow sudah di-import dan di-deploy
- [ ] Debug panel Node-RED menampilkan data sensor
- [ ] mosquitto_sub bisa menerima messages
- [ ] Lamp bisa dikontrol manual (ON/OFF)
- [ ] Automation bekerja: motion detected → lamp ON

---

## 🎯 Next Steps

Setelah sistem berjalan:

1. ✨ **Buat Dashboard di Node-RED**
   - Install `node-red-dashboard`
   - Tambah gauge untuk temperature
   - Tambah LED indicator untuk motion
   - Tambah switch untuk lamp control

2. 📈 **Tambah Data Persistence**
   - Simpan data sensor ke file atau database
   - Visualisasi historical data

3. 🔔 **Implementasi Alerts**
   - Alert jika suhu terlalu tinggi
   - Notifikasi saat motion detected

4. 🤖 **Advanced Automation**
   - Jadwal otomatis (schedule)
   - Multiple conditions
   - Timer-based control

---

**Happy Coding! 🚀**

Jika ada masalah, lihat **README.md** untuk troubleshooting lengkap.
