"""
User Commands Interface
Interactive CLI for sending manual commands to IoT devices
Allows users to control devices in real-time via MQTT
"""

import sys
import json
import time
import logging
import os
from utils import create_mqtt_client, connect_with_retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UserInterface")


class UserCommandInterface:
    """Interactive command interface for controlling smart home devices"""
    
    def __init__(self, broker, port):
        self.broker = broker
        self.port = port
        self.client = None
        self.running = False
        
    def connect(self):
        """Connect to MQTT broker"""
        logger.info("Connecting to MQTT broker...")
        self.client = create_mqtt_client("user_interface", self.broker, self.port)
        
        # Subscribe to status topics for feedback
        def on_message(client, userdata, msg):
            try:
                data = json.loads(msg.payload.decode())
                logger.info(f"📩 Status from {msg.topic}:")
                for key, value in data.items():
                    if key != "timestamp":
                        logger.info(f"   {key}: {value}")
            except:
                pass
        
        self.client.on_message = on_message
        
        if connect_with_retry(self.client, self.broker, self.port):
            # Subscribe to status topics
            self.client.subscribe("home/light/status")
            self.client.subscribe("home/thermostat/status")
            self.client.subscribe("home/security/camera/status")
            self.client.loop_start()
            logger.info("✓ Connected successfully!")
            return True
        else:
            logger.error("Failed to connect to broker")
            return False
    
    def send_light_command(self, command):
        """Send command to smart light"""
        topic = "home/light/command"
        
        if command in ["on", "off"]:
            payload = json.dumps({"command": command.upper()})
        elif command.startswith("brightness"):
            try:
                level = int(command.split()[1])
                payload = json.dumps({"command": "BRIGHTNESS", "level": level})
            except:
                logger.error("Usage: brightness <0-100>")
                return
        else:
            logger.error(f"Unknown light command: {command}")
            return
        
        self.client.publish(topic, payload, qos=1)
        logger.info(f"✓ Sent: {payload} to {topic}")
    
    def send_thermostat_command(self, command):
        """Send command to thermostat"""
        topic = "home/thermostat/command"
        
        if command.startswith("temp"):
            try:
                temp = float(command.split()[1])
                payload = json.dumps({"command": "SET_TARGET", "target": temp})
            except:
                logger.error("Usage: temp <temperature>")
                return
        elif command.startswith("mode"):
            try:
                mode = command.split()[1].upper()
                payload = json.dumps({"command": "SET_MODE", "mode": mode})
            except:
                logger.error("Usage: mode <AUTO|HEAT|COOL|OFF>")
                return
        else:
            logger.error(f"Unknown thermostat command: {command}")
            return
        
        self.client.publish(topic, payload, qos=1)
        logger.info(f"✓ Sent: {payload} to {topic}")
    
    def send_camera_command(self, command):
        """Send command to security camera"""
        topic = "home/security/camera/command"
        
        if command in ["on", "activate"]:
            payload = json.dumps({"command": "ACTIVATE"})
        elif command in ["off", "deactivate"]:
            payload = json.dumps({"command": "DEACTIVATE"})
        elif command.startswith("sensitivity"):
            try:
                level = float(command.split()[1])
                payload = json.dumps({"command": "SET_SENSITIVITY", "sensitivity": level})
            except:
                logger.error("Usage: sensitivity <0.0-1.0>")
                return
        else:
            logger.error(f"Unknown camera command: {command}")
            return
        
        self.client.publish(topic, payload, qos=1)
        logger.info(f"✓ Sent: {payload} to {topic}")
    
    def show_help(self):
        """Display help menu"""
        print("\n" + "=" * 70)
        print("SMART HOME CONTROL INTERFACE - AVAILABLE COMMANDS")
        print("=" * 70)
        print("\n💡 LIGHT COMMANDS:")
        print("  light on              - Turn on the light")
        print("  light off             - Turn off the light")
        print("  light brightness <0-100> - Set brightness level")
        print("\n🌡️  THERMOSTAT COMMANDS:")
        print("  thermostat temp <celsius> - Set target temperature")
        print("  thermostat mode <mode>    - Set mode (AUTO/HEAT/COOL/OFF)")
        print("\n📷 CAMERA COMMANDS:")
        print("  camera on             - Activate camera")
        print("  camera off            - Deactivate camera")
        print("  camera sensitivity <0.0-1.0> - Set motion detection sensitivity")
        print("\n📊 SYSTEM COMMANDS:")
        print("  status                - Request status from all devices")
        print("  help                  - Show this help menu")
        print("  quit / exit           - Exit the interface")
        print("=" * 70 + "\n")
    
    def request_status(self):
        """Request status from all devices"""
        self.client.publish("home/light/command", json.dumps({"command": "STATUS"}), qos=1)
        self.client.publish("home/thermostat/command", json.dumps({"command": "STATUS"}), qos=1)
        self.client.publish("home/security/camera/command", json.dumps({"command": "STATUS"}), qos=1)
        logger.info("✓ Status requested from all devices")
        time.sleep(1)  # Wait for responses
    
    def process_command(self, user_input):
        """Process user command"""
        parts = user_input.lower().strip().split(maxsplit=1)
        
        if not parts:
            return True
        
        device = parts[0]
        command = parts[1] if len(parts) > 1 else ""
        
        if device in ["quit", "exit"]:
            return False
        elif device == "help":
            self.show_help()
        elif device == "status":
            self.request_status()
        elif device == "light":
            self.send_light_command(command)
        elif device == "thermostat":
            self.send_thermostat_command(command)
        elif device == "camera":
            self.send_camera_command(command)
        else:
            logger.error(f"Unknown device: {device}")
            print("Type 'help' for available commands")
        
        return True
    
    def run(self):
        """Run interactive command loop"""
        print("\n" + "=" * 70)
        print("🏠 SMART HOME USER INTERFACE")
        print("=" * 70)
        
        if not self.connect():
            return
        
        self.show_help()
        self.running = True
        
        try:
            while self.running:
                try:
                    user_input = input("\n🏠 SmartHome > ").strip()
                    
                    if user_input:
                        if not self.process_command(user_input):
                            break
                    
                except EOFError:
                    break
                
        except KeyboardInterrupt:
            print("\n\nReceived interrupt signal...")
        finally:
            logger.info("Shutting down user interface...")
            if self.client:
                self.client.loop_stop()
                self.client.disconnect()
            logger.info("User interface stopped.")


def run_user_commands():
    """Main function for user command interface"""
    # Get configuration from environment variables
    broker = os.getenv("BROKER", "mosquitto")
    port = int(os.getenv("PORT", "1883"))
    
    # Create and run interface
    interface = UserCommandInterface(broker, port)
    interface.run()


if __name__ == "__main__":
    # Add devices directory to path for utils import
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'devices'))
    
    run_user_commands()
