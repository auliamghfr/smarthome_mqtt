"""
Motion Sensor Device
Publishes motion detection events to MQTT broker
"""

import time
import random
import json
import os
import logging
from utils import create_mqtt_client, connect_with_retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MotionSensor")


def run_motion_sensor():
    """
    Main function for motion sensor
    Publishes motion detection status every 3 seconds
    """
    # Get configuration from environment variables
    broker = os.getenv("BROKER", "mosquitto")
    port = int(os.getenv("PORT", "1883"))
    client_id = os.getenv("CLIENT_ID", "motion_sensor")
    topic = os.getenv("TOPIC", "home/sensor/motion")
    interval = int(os.getenv("INTERVAL", "3"))
    
    logger.info(f"Starting Motion Sensor")
    logger.info(f"Broker: {broker}:{port}")
    logger.info(f"Publishing to: {topic}")
    logger.info(f"Interval: {interval} seconds")
    
    # Create MQTT client
    client = create_mqtt_client(client_id, broker, port)
    
    # Connect to broker with retry
    if not connect_with_retry(client, broker, port):
        logger.error("Failed to connect. Exiting.")
        return
    
    # Start MQTT loop in background
    client.loop_start()
    
    try:
        while True:
            # Randomly detect motion (30% chance of detecting motion)
            motion_detected = random.choice([0, 0, 0, 0, 0, 0, 0, 1, 1, 1])
            motion_status = "motion detected" if motion_detected == 1 else "no motion"
            
            # Create payload
            payload = {
                "sensor": "motion",
                "value": motion_detected,
                "status": motion_status,
                "timestamp": time.time()
            }
            
            # Publish to MQTT topic
            result = client.publish(topic, json.dumps(payload), qos=1)
            
            if result.rc == 0:
                icon = "🚶" if motion_detected == 1 else "🚫"
                logger.info(f"📤 Published: {icon} {motion_status} to {topic}")
            else:
                logger.error(f"Failed to publish. RC: {result.rc}")
            
            # Wait before next reading
            time.sleep(interval)
            
    except KeyboardInterrupt:
        logger.info("Shutting down motion sensor...")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        logger.info("Motion sensor stopped.")


if __name__ == "__main__":
    run_motion_sensor()
