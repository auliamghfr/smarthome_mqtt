"""
Temperature Sensor Device
Publishes random temperature readings to MQTT broker
"""

import time
import random
import json
import os
import logging
from utils import create_mqtt_client, connect_with_retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TempSensor")


def run_temp_sensor():
    """
    Main function for temperature sensor
    Publishes temperature readings every 5 seconds
    """
    # Get configuration from environment variables
    broker = os.getenv("BROKER", "mosquitto")
    port = int(os.getenv("PORT", "1883"))
    client_id = os.getenv("CLIENT_ID", "temp_sensor")
    topic = os.getenv("TOPIC", "home/sensor/temperature")
    interval = int(os.getenv("INTERVAL", "5"))
    
    logger.info(f"Starting Temperature Sensor")
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
            # Generate random temperature between 18 and 32 degrees Celsius
            temperature = round(random.uniform(18.0, 32.0), 2)
            
            # Create payload
            payload = {
                "sensor": "temperature",
                "value": temperature,
                "unit": "°C",
                "timestamp": time.time()
            }
            
            # Publish to MQTT topic
            result = client.publish(topic, json.dumps(payload), qos=1)
            
            if result.rc == 0:
                logger.info(f"📤 Published: {temperature}°C to {topic}")
            else:
                logger.error(f"Failed to publish. RC: {result.rc}")
            
            # Wait before next reading
            time.sleep(interval)
            
    except KeyboardInterrupt:
        logger.info("Shutting down temperature sensor...")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        logger.info("Temperature sensor stopped.")


if __name__ == "__main__":
    run_temp_sensor()
