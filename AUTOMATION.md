# Smart Home Automation Documentation

## Overview
Automation system untuk smart home menggunakan Node-RED yang mengendalikan lampu berdasarkan motion sensor.

## Automation Logic

### Simple Motion-Based Automation
**Rule:** Lampu menyala otomatis ketika ada pergerakan, mati ketika tidak ada pergerakan.

```
Motion Detected (value=1) → Lamp ON
No Motion (value=0) → Lamp OFF
```

## Node-RED Flow Structure

### Flow Configuration
- **Tab Name:** Motion Automation
- **MQTT Broker:** mosquitto:1883
- **Client ID:** nodered_automation

### Nodes in Flow

1. **Motion Sensor In** (MQTT In)
   - Topic: `home/sensor/motion`
   - QoS: 0
   - Datatype: JSON
   - Output: Parsed motion data

2. **Motion Value** (Switch Node)
   - Property: `msg.payload.value`
   - Rules:
     - Output 1: value == 1 (motion detected)
     - Output 2: value == 0 (no motion)

3. **ON** (Change Node)
   - Action: Set `msg.payload` to `"ON"`
   - Triggered when motion detected

4. **OFF** (Change Node)
   - Action: Set `msg.payload` to `"OFF"`
   - Triggered when no motion

5. **Lamp Command Out** (MQTT Out)
   - Topic: `home/actuator/lamp/command`
   - QoS: 1
   - Payload: "ON" or "OFF"

## MQTT Topics

### Input Topics
- `home/sensor/motion` - Motion sensor data
  ```json
  {
    "sensor": "motion",
    "value": 1,
    "status": "motion detected",
    "timestamp": 1764249539.555398
  }
  ```

### Output Topics
- `home/actuator/lamp/command` - Lamp control commands
  - Payload: `"ON"` or `"OFF"`

### Status Topics
- `home/actuator/lamp/status` - Lamp status feedback
  ```json
  {
    "device": "smart_lamp",
    "state": "ON",
    "timestamp": 1764249539.5610003
  }
  ```

## Testing Automation

### Monitor All Topics
```bash
docker exec mqtt_broker mosquitto_sub -t "home/#" -v
```

### Test Motion Detection
```bash
# Publish motion detected
docker exec mqtt_broker mosquitto_pub -t "home/sensor/motion" \
  -m '{"sensor":"motion","value":1,"status":"motion detected"}'

# Expected: Lamp turns ON

# Publish no motion
docker exec mqtt_broker mosquitto_pub -t "home/sensor/motion" \
  -m '{"sensor":"motion","value":0,"status":"no motion"}'

# Expected: Lamp turns OFF
```

## Flow Backup

Flow configuration is stored in:
- `/home/yrr/smarthome_mqtt/node-red/data/flows.json` (active)
- `/home/yrr/smarthome_mqtt/node-red/data/flows.json.backup` (backup)
- `/home/yrr/smarthome_mqtt/node-red/data/flows_simple.json` (simple version)

**Note:** flows.json is in .gitignore for security reasons.

## Accessing Node-RED

- **URL:** http://localhost:1880
- **Tab:** Motion Automation
- **Edit Flow:** Double-click nodes to modify logic
- **Deploy:** Click "Deploy" button after changes

## Troubleshooting

### Automation Not Working
1. Check Node-RED logs:
   ```bash
   docker logs node_red --tail 50
   ```

2. Verify MQTT connection:
   ```bash
   docker logs node_red | grep "Connected to broker"
   ```

3. Test MQTT manually:
   ```bash
   docker exec mqtt_broker mosquitto_sub -t "home/#" -v
   ```

### Restart Automation
```bash
docker-compose restart nodered
```

## Performance

- **Response Time:** < 100ms from motion detection to lamp command
- **No Delay:** Instant ON/OFF (no debounce or delay)
- **Real-time:** Direct MQTT pub/sub without buffering

## Last Updated
- Date: November 27, 2025
- Version: 1.0 - Simple Motion-Based Automation
- Branch: Yayan
