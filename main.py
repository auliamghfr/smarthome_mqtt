"""
Main Application with Multi-threading
Coordinates all IoT devices and automation controller using parallel threads
Demonstrates multi-threading for responsive device control
"""

import threading
import time
import logging
import sys
import os

# Add devices directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'devices'))

from devices.temp_sensor import run_temp_sensor
from devices.smart_light import run_smart_light
from devices.thermostat import run_thermostat
from devices.security_camera import run_security_camera
from controller import run_automation_controller

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("MainApp")


class SmartHomeSystem:
    """Main coordinator for smart home system using multi-threading"""
    
    def __init__(self):
        self.threads = []
        self.running = False
        
    def start_device_thread(self, target, name):
        """Start a device in a separate thread"""
        thread = threading.Thread(target=target, name=name, daemon=True)
        thread.start()
        self.threads.append(thread)
        logger.info(f"✓ Started thread: {name}")
        return thread
    
    def start_all_devices(self):
        """Start all IoT devices and automation controller in parallel"""
        logger.info("=" * 70)
        logger.info("🏠 SMART HOME AUTOMATION SYSTEM")
        logger.info("=" * 70)
        logger.info("Starting all devices using multi-threading...")
        logger.info("")
        
        # List of devices to start
        devices = [
            (run_temp_sensor, "TemperatureSensor"),
            (run_smart_light, "SmartLight"),
            (run_thermostat, "Thermostat"),
            (run_security_camera, "SecurityCamera"),
            (run_automation_controller, "AutomationController")
        ]
        
        # Start each device in its own thread
        for device_func, device_name in devices:
            self.start_device_thread(device_func, device_name)
            time.sleep(0.5)  # Small delay between starts
        
        self.running = True
        
        logger.info("")
        logger.info("=" * 70)
        logger.info(f"✓ All {len(devices)} devices started successfully!")
        logger.info("=" * 70)
        logger.info("")
        logger.info("Active Threads:")
        for thread in self.threads:
            logger.info(f"  • {thread.name} - {'Running' if thread.is_alive() else 'Stopped'}")
        logger.info("")
        logger.info("System Status:")
        logger.info("  📡 MQTT Communication: Active")
        logger.info("  🤖 Automation Rules: Enabled")
        logger.info("  🧵 Multi-threading: Enabled")
        logger.info("")
        logger.info("Automation Rules Active:")
        logger.info("  1. Temperature > 28°C → Activate COOLING")
        logger.info("  2. Temperature < 20°C → Activate HEATING")
        logger.info("  3. Motion Detected → Turn ON lights")
        logger.info("  4. No motion for 30s → Turn OFF lights")
        logger.info("")
        logger.info("=" * 70)
        logger.info("Press Ctrl+C to stop the system")
        logger.info("=" * 70)
    
    def monitor_threads(self):
        """Monitor thread health"""
        while self.running:
            time.sleep(10)
            
            # Check if all threads are alive
            dead_threads = [t for t in self.threads if not t.is_alive()]
            
            if dead_threads:
                logger.warning(f"⚠️ {len(dead_threads)} thread(s) stopped:")
                for thread in dead_threads:
                    logger.warning(f"  • {thread.name}")
    
    def stop(self):
        """Stop the system"""
        logger.info("")
        logger.info("=" * 70)
        logger.info("Shutting down Smart Home System...")
        logger.info("=" * 70)
        
        self.running = False
        
        # Wait for threads to finish (with timeout)
        for thread in self.threads:
            if thread.is_alive():
                logger.info(f"Waiting for {thread.name} to stop...")
                thread.join(timeout=2)
        
        logger.info("=" * 70)
        logger.info("✓ Smart Home System stopped successfully")
        logger.info("=" * 70)


def main():
    """Main entry point"""
    # Create smart home system
    system = SmartHomeSystem()
    
    try:
        # Start all devices
        system.start_all_devices()
        
        # Monitor threads
        system.monitor_threads()
        
    except KeyboardInterrupt:
        logger.info("\n\nReceived interrupt signal...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        system.stop()


if __name__ == "__main__":
    # Set environment variables for devices (if not already set)
    if "BROKER" not in os.environ:
        os.environ["BROKER"] = "localhost"  # Use localhost when running outside Docker
    if "PORT" not in os.environ:
        os.environ["PORT"] = "1883"
    
    main()
