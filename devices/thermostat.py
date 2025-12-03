"""
Thermostat Device
Controls heating/cooling based on temperature readings
Subscribes to temperature sensor and controls HVAC system
"""

import time
import json
import os
import logging
from utils import create_mqtt_client, connect_with_retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Thermostat")


class Thermostat:
    """Smart Thermostat with temperature control"""
    
    def __init__(self, thermostat_id="main_hvac"):
        self.thermostat_id = thermostat_id
        self.current_temp = 25.0
        self.target_temp = 24.0
        self.mode = "AUTO"  # AUTO, HEAT, COOL, OFF
        self.hvac_state = "OFF"  # OFF, HEATING, COOLING
        self.temp_threshold = 1.0  # Temperature difference threshold
        
    def set_target_temperature(self, temp):
        """Set target temperature"""
        self.target_temp = temp
        logger.info(f"🎯 Target temperature set to {temp}°C")
        
    def set_mode(self, mode):
        """Set thermostat mode"""
        if mode in ["AUTO", "HEAT", "COOL", "OFF"]:
            self.mode = mode
            logger.info(f"🔧 Mode set to {mode}")
        else:
            logger.warning(f"Invalid mode: {mode}")
    
    def update_temperature(self, temp):
        """Update current temperature and control HVAC"""
        self.current_temp = temp
        
        if self.mode == "OFF":
            self.hvac_state = "OFF"
            return
        
        # Calculate temperature difference
        temp_diff = self.current_temp - self.target_temp
        
        # Control logic based on mode
        if self.mode == "AUTO":
            if temp_diff > self.temp_threshold:
                # Too hot - turn on cooling
                self.hvac_state = "COOLING"
                logger.info(f"❄️ COOLING: Current {self.current_temp}°C > Target {self.target_temp}°C")
            elif temp_diff < -self.temp_threshold:
                # Too cold - turn on heating
                self.hvac_state = "HEATING"
                logger.info(f"🔥 HEATING: Current {self.current_temp}°C < Target {self.target_temp}°C")
            else:
                # Temperature OK
                self.hvac_state = "OFF"
                logger.info(f"✓ Temperature OK: {self.current_temp}°C")
                
        elif self.mode == "COOL":
            if temp_diff > self.temp_threshold:
                self.hvac_state = "COOLING"
                logger.info(f"❄️ COOLING: {self.current_temp}°C")
            else:
                self.hvac_state = "OFF"
                
        elif self.mode == "HEAT":
            if temp_diff < -self.temp_threshold:
                self.hvac_state = "HEATING"
                logger.info(f"🔥 HEATING: {self.current_temp}°C")
            else:
                self.hvac_state = "OFF"
    
    def get_status(self):
        """Get current thermostat status"""
        return {
            "thermostat_id": self.thermostat_id,
            "current_temp": self.current_temp,
            "target_temp": self.target_temp,
            "mode": self.mode,
            "hvac_state": self.hvac_state,
            "timestamp": time.time()
        }


def run_thermostat():
    """
    Main function for thermostat
    Subscribes to temperature and publishes HVAC commands
    """
    # Get configuration from environment variables
    broker = os.getenv("BROKER", "mosquitto")
    port = int(os.getenv("PORT", "1883"))
    client_id = os.getenv("CLIENT_ID", "thermostat")
    thermostat_id = os.getenv("THERMOSTAT_ID", "main_hvac")
    temp_topic = os.getenv("TEMP_TOPIC", "home/sensor/temperature")
    command_topic = os.getenv("COMMAND_TOPIC", "home/thermostat/command")
    status_topic = os.getenv("STATUS_TOPIC", "home/thermostat/status")
    hvac_topic = os.getenv("HVAC_TOPIC", "home/hvac/command")
    
    logger.info(f"Starting Thermostat: {thermostat_id}")
    logger.info(f"Broker: {broker}:{port}")
    logger.info(f"Temperature topic: {temp_topic}")
    logger.info(f"Command topic: {command_topic}")
    logger.info(f"Status topic: {status_topic}")
    
    # Create thermostat instance
    thermostat = Thermostat(thermostat_id)
    
    # Create MQTT client
    client = create_mqtt_client(client_id, broker, port)
    
    def on_message(client, userdata, msg):
        """Handle incoming MQTT messages"""
        try:
            payload = msg.payload.decode()
            data = json.loads(payload)
            
            # Handle temperature sensor data
            if msg.topic == temp_topic:
                if "value" in data:
                    temp = float(data["value"])
                    thermostat.update_temperature(temp)
                    
                    # Publish HVAC command
                    hvac_command = {
                        "command": thermostat.hvac_state,
                        "timestamp": time.time()
                    }
                    client.publish(hvac_topic, json.dumps(hvac_command), qos=1)
                    
                    # Publish thermostat status
                    status = thermostat.get_status()
                    client.publish(status_topic, json.dumps(status), qos=1)
            
            # Handle thermostat commands
            elif msg.topic == command_topic:
                command = data.get("command", "").upper()
                
                if command == "SET_TARGET":
                    target = float(data.get("target", 24.0))
                    thermostat.set_target_temperature(target)
                elif command == "SET_MODE":
                    mode = data.get("mode", "AUTO").upper()
                    thermostat.set_mode(mode)
                elif command == "STATUS":
                    pass  # Just publish status
                else:
                    logger.warning(f"Unknown command: {command}")
                
                # Publish status after command
                status = thermostat.get_status()
                client.publish(status_topic, json.dumps(status), qos=1)
                logger.info(f"📤 Published status: Mode={status['mode']}, HVAC={status['hvac_state']}")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    # Set message callback
    client.on_message = on_message
    
    # Connect to broker with retry
    if not connect_with_retry(client, broker, port):
        logger.error("Failed to connect. Exiting.")
        return
    
    # Subscribe to topics
    client.subscribe(temp_topic)
    client.subscribe(command_topic)
    logger.info(f"✓ Subscribed to {temp_topic}")
    logger.info(f"✓ Subscribed to {command_topic}")
    
    # Publish initial status
    status = thermostat.get_status()
    client.publish(status_topic, json.dumps(status), qos=1)
    logger.info(f"📤 Published initial status: Target={status['target_temp']}°C, Mode={status['mode']}")
    
    # Start MQTT loop
    logger.info("Thermostat is running. Monitoring temperature...")
    
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down thermostat...")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        client.disconnect()
        logger.info("Thermostat stopped.")


if __name__ == "__main__":
    run_thermostat()
