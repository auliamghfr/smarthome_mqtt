"""
Utility functions for MQTT devices
Provides common MQTT client setup and connection handling
"""

import paho.mqtt.client as mqtt
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def create_mqtt_client(client_id, broker, port=1883):
    """
    Create and configure MQTT client
    
    Args:
        client_id: Unique identifier for this client
        broker: MQTT broker hostname or IP
        port: MQTT broker port (default 1883)
    
    Returns:
        Configured MQTT client instance
    """
    client = mqtt.Client(client_id=client_id)
    
    # Callback when connected
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logging.info(f"✓ Connected to broker {broker}:{port}")
        else:
            logging.error(f"✗ Connection failed with code {rc}")
    
    # Callback when disconnected
    def on_disconnect(client, userdata, rc):
        if rc != 0:
            logging.warning(f"Unexpected disconnection. Code: {rc}")
    
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    
    return client


def connect_with_retry(client, broker, port=1883, max_retries=10, retry_delay=5):
    """
    Connect to MQTT broker with retry mechanism
    
    Args:
        client: MQTT client instance
        broker: MQTT broker hostname
        port: MQTT broker port
        max_retries: Maximum number of connection attempts
        retry_delay: Delay between retries in seconds
    
    Returns:
        True if connected successfully, False otherwise
    """
    for attempt in range(1, max_retries + 1):
        try:
            logging.info(f"Attempting to connect to {broker}:{port} (attempt {attempt}/{max_retries})...")
            client.connect(broker, port, keepalive=60)
            return True
        except Exception as e:
            logging.warning(f"Connection attempt {attempt} failed: {e}")
            if attempt < max_retries:
                logging.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logging.error("Max retries reached. Could not connect to broker.")
                return False
    
    return False
