"""
Smart Lamp Actuator
Subscribes to command topic and publishes status updates
"""

import time
import json
import os
import logging
from utils import create_mqtt_client, connect_with_retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmartLamp")


class SmartLamp:
    """Smart Lamp class that responds to MQTT commands"""
    
    def __init__(self, broker, port, client_id, command_topic, status_topic):
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.command_topic = command_topic
        self.status_topic = status_topic
        self.lamp_state = "OFF"  # Initial state
        
        # Create MQTT client
        self.client = create_mqtt_client(client_id, broker, port)
        self.client.on_message = self.on_message
    
    def on_message(self, client, userdata, msg):
        """
        Callback when message is received on subscribed topic
        """
        try:
            payload = msg.payload.decode('utf-8')
            logger.info(f"📥 Received command: {payload} on {msg.topic}")
            
            # Try to parse as JSON first
            try:
                data = json.loads(payload)
                command = data.get("command", payload).upper()
            except json.JSONDecodeError:
                # If not JSON, treat as plain text
                command = payload.upper()
            
            # Process command
            if command in ["ON", "1", "TRUE"]:
                self.lamp_state = "ON"
                logger.info("💡 Lamp turned ON")
            elif command in ["OFF", "0", "FALSE"]:
                self.lamp_state = "OFF"
                logger.info("💡 Lamp turned OFF")
            else:
                logger.warning(f"Unknown command: {command}")
                return
            
            # Publish status update
            self.publish_status()
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def publish_status(self):
        """
        Publish current lamp status to status topic
        """
        status_payload = {
            "device": "smart_lamp",
            "state": self.lamp_state,
            "timestamp": time.time()
        }
        
        result = self.client.publish(
            self.status_topic,
            json.dumps(status_payload),
            qos=1,
            retain=True  # Retain status for new subscribers
        )
        
        if result.rc == 0:
            icon = "🟢" if self.lamp_state == "ON" else "🔴"
            logger.info(f"📤 Published status: {icon} {self.lamp_state} to {self.status_topic}")
        else:
            logger.error(f"Failed to publish status. RC: {result.rc}")
    
    def run(self):
        """
        Main run loop for smart lamp
        """
        logger.info(f"Starting Smart Lamp")
        logger.info(f"Broker: {self.broker}:{self.port}")
        logger.info(f"Command topic: {self.command_topic}")
        logger.info(f"Status topic: {self.status_topic}")
        
        # Connect to broker with retry
        if not connect_with_retry(self.client, self.broker, self.port):
            logger.error("Failed to connect. Exiting.")
            return
        
        # Subscribe to command topic
        self.client.subscribe(self.command_topic, qos=1)
        logger.info(f"✓ Subscribed to {self.command_topic}")
        
        # Publish initial status
        self.publish_status()
        
        # Start MQTT loop (blocking)
        try:
            logger.info("Smart Lamp is ready. Waiting for commands...")
            self.client.loop_forever()
        except KeyboardInterrupt:
            logger.info("Shutting down smart lamp...")
        except Exception as e:
            logger.error(f"Error: {e}")
        finally:
            self.client.disconnect()
            logger.info("Smart lamp stopped.")


def run_smart_lamp():
    """
    Entry point for smart lamp device
    """
    # Get configuration from environment variables
    broker = os.getenv("BROKER", "mosquitto")
    port = int(os.getenv("PORT", "1883"))
    client_id = os.getenv("CLIENT_ID", "smart_lamp")
    command_topic = os.getenv("COMMAND_TOPIC", "home/actuator/lamp/command")
    status_topic = os.getenv("STATUS_TOPIC", "home/actuator/lamp/status")
    
    # Create and run lamp
    lamp = SmartLamp(broker, port, client_id, command_topic, status_topic)
    lamp.run()


if __name__ == "__main__":
    run_smart_lamp()
