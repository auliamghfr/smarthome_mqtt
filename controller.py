"""
Home Automation Controller
Central automation engine that connects sensors with actuators
Implements automation rules based on sensor data
"""

import time
import json
import os
import logging
from utils import create_mqtt_client, connect_with_retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutomationController")


class AutomationController:
    """Central controller for home automation rules"""
    
    def __init__(self):
        self.current_temp = 25.0
        self.light_state = "OFF"
        self.motion_detected = False
        self.last_motion_time = 0
        
        # Automation rules configuration
        self.temp_high_threshold = 28.0  # Turn on cooling if temp > 28°C
        self.temp_low_threshold = 20.0   # Turn on heating if temp < 20°C
        self.motion_light_timeout = 30   # Turn off light 30 seconds after no motion
        
        logger.info("Automation Controller initialized")
        logger.info(f"Temperature thresholds: {self.temp_low_threshold}°C - {self.temp_high_threshold}°C")
        logger.info(f"Motion light timeout: {self.motion_light_timeout} seconds")
    
    def handle_temperature(self, temp, client):
        """
        Automation Rule: Control thermostat based on temperature
        - High temp (>28°C): Set thermostat to COOL mode
        - Low temp (<20°C): Set thermostat to HEAT mode
        - Normal temp: Set thermostat to AUTO mode
        """
        self.current_temp = temp
        logger.info(f"🌡️ Temperature update: {temp}°C")
        
        if temp > self.temp_high_threshold:
            # Too hot - activate cooling
            command = {
                "command": "SET_MODE",
                "mode": "COOL",
                "reason": f"Temperature {temp}°C exceeds threshold {self.temp_high_threshold}°C"
            }
            client.publish("home/thermostat/command", json.dumps(command), qos=1)
            logger.warning(f"🔥 HIGH TEMP! Activating COOL mode: {temp}°C > {self.temp_high_threshold}°C")
            
        elif temp < self.temp_low_threshold:
            # Too cold - activate heating
            command = {
                "command": "SET_MODE",
                "mode": "HEAT",
                "reason": f"Temperature {temp}°C below threshold {self.temp_low_threshold}°C"
            }
            client.publish("home/thermostat/command", json.dumps(command), qos=1)
            logger.warning(f"❄️ LOW TEMP! Activating HEAT mode: {temp}°C < {self.temp_low_threshold}°C")
            
        else:
            # Normal temperature - use AUTO mode
            command = {
                "command": "SET_MODE",
                "mode": "AUTO",
                "reason": "Temperature within normal range"
            }
            client.publish("home/thermostat/command", json.dumps(command), qos=1)
            logger.info(f"✓ Normal temperature. AUTO mode: {temp}°C")
    
    def handle_motion(self, motion_data, client):
        """
        Automation Rule: Control lights based on motion detection
        - Motion detected: Turn on lights and reset timeout
        - No motion: Start timeout countdown to turn off lights
        """
        camera_id = motion_data.get("camera_id", "unknown")
        motion_detected = motion_data.get("motion_detected", False)
        
        if motion_detected:
            # Motion detected - turn on lights
            self.motion_detected = True
            self.last_motion_time = time.time()
            logger.warning(f"🚨 Motion detected from {camera_id}!")
            
            # Turn on light when motion is detected
            if self.light_state == "OFF":
                command = {"command": "ON"}
                client.publish("home/light/command", json.dumps(command), qos=1)
                logger.info(f"💡 Motion detected - Light turned ON")
                self.light_state = "ON"
            else:
                logger.info(f"💡 Lights already ON, motion timer refreshed")
        else:
            # No motion detected
            logger.info(f"✓ No motion from {camera_id}")
            
            # Check if lights should be turned off due to timeout
            if self.motion_detected and self.light_state == "ON":
                time_since_motion = time.time() - self.last_motion_time
                
                if time_since_motion >= self.motion_light_timeout:
                    # Timeout reached - turn off lights
                    command = {"command": "OFF"}
                    client.publish("home/light/command", json.dumps(command), qos=1)
                    logger.info(f"💡 No motion for {self.motion_light_timeout}s - Light turned OFF")
                    self.light_state = "OFF"
                    self.motion_detected = False
                else:
                    remaining = self.motion_light_timeout - time_since_motion
                    logger.info(f"⏱️  Waiting for timeout: {remaining:.0f}s remaining")
    
    def handle_light_status(self, status_data):
        """Track light status"""
        self.light_state = status_data.get("state", "OFF")
    
    def check_motion_timeout(self, client):
        """
        Check if motion timeout has elapsed and turn off lights
        Called periodically from main loop
        """
        if self.motion_detected and self.light_state == "ON":
            time_since_motion = time.time() - self.last_motion_time
            
            if time_since_motion > self.motion_light_timeout:
                # No motion detected for timeout period - turn off lights
                command = {"command": "OFF"}
                client.publish("home/light/command", json.dumps(command), qos=1)
                logger.info(f"🌑 Turning OFF lights - no motion for {int(time_since_motion)}s")
                self.motion_detected = False
                self.light_state = "OFF"


def run_automation_controller():
    """
    Main function for automation controller
    Subscribes to sensors and publishes commands to actuators
    """
    # Get configuration from environment variables
    broker = os.getenv("BROKER", "mosquitto")
    port = int(os.getenv("PORT", "1883"))
    client_id = os.getenv("CLIENT_ID", "automation_controller")
    
    logger.info("=" * 60)
    logger.info("Starting Home Automation Controller")
    logger.info("=" * 60)
    logger.info(f"Broker: {broker}:{port}")
    
    # Create automation controller instance
    controller = AutomationController()
    
    # Create MQTT client
    client = create_mqtt_client(client_id, broker, port)
    
    def on_message(client, userdata, msg):
        """Handle incoming MQTT messages from sensors"""
        try:
            payload = msg.payload.decode()
            data = json.loads(payload)
            topic = msg.topic
            
            # Route messages to appropriate handlers
            if topic == "home/sensor/temperature":
                # Temperature sensor data
                if "value" in data:
                    temp = float(data["value"])
                    controller.handle_temperature(temp, client)
            
            elif topic == "home/security/motion":
                # Motion detection event
                controller.handle_motion(data, client)
            
            elif topic == "home/light/status":
                # Light status update
                controller.handle_light_status(data)
            
            elif topic == "home/thermostat/status":
                # Thermostat status (for monitoring)
                logger.info(f"📊 Thermostat: {data.get('mode')} - {data.get('hvac_state')}")
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
        except Exception as e:
            logger.error(f"Error processing message from {msg.topic}: {e}")
    
    # Set message callback
    client.on_message = on_message
    
    # Connect to broker with retry
    if not connect_with_retry(client, broker, port):
        logger.error("Failed to connect. Exiting.")
        return
    
    # Subscribe to all sensor topics
    topics = [
        "home/sensor/temperature",
        "home/security/motion",
        "home/light/status",
        "home/thermostat/status"
    ]
    
    for topic in topics:
        client.subscribe(topic)
        logger.info(f"✓ Subscribed to {topic}")
    
    # Start MQTT loop in background
    client.loop_start()
    
    logger.info("=" * 60)
    logger.info("Automation Controller is running")
    logger.info("Monitoring sensors and applying automation rules...")
    logger.info("=" * 60)
    
    # Main loop for periodic checks
    try:
        while True:
            # Check motion timeout periodically
            controller.check_motion_timeout(client)
            
            # Sleep for 1 second before next check
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down automation controller...")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        logger.info("Automation controller stopped.")


if __name__ == "__main__":
    run_automation_controller()
