"""
Smart Light Device
Subscribes to light commands and publishes light status
Can be controlled via MQTT messages (ON/OFF)
"""

import time
import json
import os
import logging
from utils import create_mqtt_client, connect_with_retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmartLight")


class SmartLight:
    """Smart Light that can be controlled via MQTT"""
    
    def __init__(self, light_id="living_room"):
        self.light_id = light_id
        self.state = "OFF"  # Initial state
        self.brightness = 0
        
    def turn_on(self):
        """Turn the light ON"""
        self.state = "ON"
        self.brightness = 100
        logger.info(f"💡 Light {self.light_id} turned ON")
        
    def turn_off(self):
        """Turn the light OFF"""
        self.state = "OFF"
        self.brightness = 0
        logger.info(f"🌑 Light {self.light_id} turned OFF")
        
    def set_brightness(self, level):
        """Set brightness level (0-100)"""
        if 0 <= level <= 100:
            self.brightness = level
            self.state = "ON" if level > 0 else "OFF"
            logger.info(f"💡 Light {self.light_id} brightness set to {level}%")
        else:
            logger.warning(f"Invalid brightness level: {level}")
    
    def get_status(self):
        """Get current light status"""
        return {
            "light_id": self.light_id,
            "state": self.state,
            "brightness": self.brightness,
            "timestamp": time.time()
        }


def run_smart_light():
    """
    Main function for smart light
    Subscribes to commands and publishes status
    """
    # Get configuration from environment variables
    broker = os.getenv("BROKER", "mosquitto")
    port = int(os.getenv("PORT", "1883"))
    client_id = os.getenv("CLIENT_ID", "smart_light")
    light_id = os.getenv("LIGHT_ID", "living_room")
    command_topic = os.getenv("COMMAND_TOPIC", "home/light/command")
    status_topic = os.getenv("STATUS_TOPIC", "home/light/status")
    
    logger.info(f"Starting Smart Light: {light_id}")
    logger.info(f"Broker: {broker}:{port}")
    logger.info(f"Command topic: {command_topic}")
    logger.info(f"Status topic: {status_topic}")
    
    # Create smart light instance
    light = SmartLight(light_id)
    
    # Create MQTT client
    client = create_mqtt_client(client_id, broker, port)
    
    def on_message(client, userdata, msg):
        """Handle incoming MQTT messages"""
        try:
            payload = msg.payload.decode()
            logger.info(f"📩 Received command: {payload}")
            
            # Handle JSON commands
            try:
                data = json.loads(payload)
                command = data.get("command", "").upper()
                
                if command == "ON":
                    light.turn_on()
                elif command == "OFF":
                    light.turn_off()
                elif command == "BRIGHTNESS":
                    level = data.get("level", 100)
                    light.set_brightness(level)
                elif command == "STATUS":
                    pass  # Just publish status
                else:
                    logger.warning(f"Unknown command: {command}")
                    
            except json.JSONDecodeError:
                # Handle simple text commands
                command = payload.upper()
                if command == "ON":
                    light.turn_on()
                elif command == "OFF":
                    light.turn_off()
                else:
                    logger.warning(f"Unknown command: {payload}")
            
            # Publish status after command
            status = light.get_status()
            client.publish(status_topic, json.dumps(status), qos=1)
            logger.info(f"📤 Published status: {status['state']} ({status['brightness']}%)")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    # Set message callback
    client.on_message = on_message
    
    # Connect to broker with retry
    if not connect_with_retry(client, broker, port):
        logger.error("Failed to connect. Exiting.")
        return
    
    # Subscribe to command topic
    client.subscribe(command_topic)
    logger.info(f"✓ Subscribed to {command_topic}")
    
    # Publish initial status
    status = light.get_status()
    client.publish(status_topic, json.dumps(status), qos=1)
    logger.info(f"📤 Published initial status: {status['state']}")
    
    # Start MQTT loop
    logger.info("Smart Light is running. Waiting for commands...")
    
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down smart light...")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        client.disconnect()
        logger.info("Smart light stopped.")


if __name__ == "__main__":
    run_smart_light()
