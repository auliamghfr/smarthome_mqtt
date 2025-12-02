"""
Security Camera with Motion Detection
Simulates a security camera that detects motion and publishes alerts
"""

import time
import random
import json
import os
import logging
from utils import create_mqtt_client, connect_with_retry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SecurityCamera")


class SecurityCamera:
    """Security Camera with motion detection"""
    
    def __init__(self, camera_id="front_door"):
        self.camera_id = camera_id
        self.is_active = True
        self.motion_detected = False
        self.last_motion_time = 0
        self.sensitivity = 0.1  # 10% probability - more OFF time for automation demo
        self.recording = False
        
    def check_motion(self):
        """
        Simulate motion detection
        Returns True if motion is detected
        """
        if not self.is_active:
            return False
        
        # Use sensitivity setting for motion detection probability
        motion = random.random() < self.sensitivity
        
        if motion:
            self.motion_detected = True
            self.last_motion_time = time.time()
            self.recording = True
            logger.warning(f"🚨 MOTION DETECTED by camera {self.camera_id}!")
            return True
        else:
            # Reset recording after 10 seconds of no motion
            if self.recording and (time.time() - self.last_motion_time > 10):
                self.recording = False
                logger.info(f"✓ No motion - stopping recording")
            self.motion_detected = False
            return False
    
    def set_active(self, active):
        """Enable/disable the camera"""
        self.is_active = active
        status = "ACTIVE" if active else "INACTIVE"
        logger.info(f"📷 Camera {self.camera_id} is now {status}")
    
    def set_sensitivity(self, sensitivity):
        """Set motion detection sensitivity (0-1)"""
        if 0 <= sensitivity <= 1:
            self.sensitivity = sensitivity
            logger.info(f"🎚️ Sensitivity set to {sensitivity}")
        else:
            logger.warning(f"Invalid sensitivity: {sensitivity}")
    
    def get_status(self):
        """Get current camera status"""
        return {
            "camera_id": self.camera_id,
            "active": self.is_active,
            "motion_detected": self.motion_detected,
            "recording": self.recording,
            "sensitivity": self.sensitivity,
            "last_motion": self.last_motion_time if self.last_motion_time > 0 else None,
            "timestamp": time.time()
        }
    
    def get_motion_event(self):
        """Get motion detection event data with actual motion state"""
        return {
            "camera_id": self.camera_id,
            "motion_detected": self.motion_detected,
            "event": "MOTION_DETECTED" if self.motion_detected else "NO_MOTION",
            "location": self.camera_id,
            "timestamp": time.time(),
            "recording": self.recording
        }


def run_security_camera():
    """
    Main function for security camera
    Monitors for motion and publishes alerts
    """
    # Get configuration from environment variables
    broker = os.getenv("BROKER", "mosquitto")
    port = int(os.getenv("PORT", "1883"))
    client_id = os.getenv("CLIENT_ID", "security_camera")
    camera_id = os.getenv("CAMERA_ID", "front_door")
    motion_topic = os.getenv("MOTION_TOPIC", "home/security/motion")
    status_topic = os.getenv("STATUS_TOPIC", "home/security/camera/status")
    command_topic = os.getenv("COMMAND_TOPIC", "home/security/camera/command")
    check_interval = int(os.getenv("CHECK_INTERVAL", "10"))  # Check every 10 seconds
    
    logger.info(f"Starting Security Camera: {camera_id}")
    logger.info(f"Broker: {broker}:{port}")
    logger.info(f"Motion topic: {motion_topic}")
    logger.info(f"Status topic: {status_topic}")
    logger.info(f"Check interval: {check_interval} seconds")
    
    # Create camera instance
    camera = SecurityCamera(camera_id)
    
    # Create MQTT client
    client = create_mqtt_client(client_id, broker, port)
    
    def on_message(client, userdata, msg):
        """Handle incoming MQTT commands"""
        try:
            payload = msg.payload.decode()
            logger.info(f"📩 Received command: {payload}")
            
            # Handle JSON commands
            try:
                data = json.loads(payload)
                command = data.get("command", "").upper()
                
                if command == "ACTIVATE":
                    camera.set_active(True)
                elif command == "DEACTIVATE":
                    camera.set_active(False)
                elif command == "SET_SENSITIVITY":
                    sensitivity = float(data.get("sensitivity", 0.3))
                    camera.set_sensitivity(sensitivity)
                elif command == "STATUS":
                    pass  # Just publish status
                else:
                    logger.warning(f"Unknown command: {command}")
                    
            except json.JSONDecodeError:
                # Handle simple text commands
                command = payload.upper()
                if command == "ON" or command == "ACTIVATE":
                    camera.set_active(True)
                elif command == "OFF" or command == "DEACTIVATE":
                    camera.set_active(False)
            
            # Publish status after command
            status = camera.get_status()
            client.publish(status_topic, json.dumps(status), qos=1)
            logger.info(f"📤 Published status: Active={status['active']}")
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
    
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
    status = camera.get_status()
    client.publish(status_topic, json.dumps(status), qos=1)
    logger.info(f"📤 Published initial status: Active={status['active']}")
    
    # Start MQTT loop in background
    client.loop_start()
    
    # Main motion detection loop
    logger.info("Security camera is running. Monitoring for motion...")
    
    try:
        while True:
            # Check for motion
            motion_detected = camera.check_motion()
            
            # Always publish motion status (both detected and not detected)
            event = camera.get_motion_event()
            client.publish(motion_topic, json.dumps(event), qos=1)
            
            if motion_detected:
                logger.warning(f"🚨 Published MOTION DETECTED to {motion_topic}")
            else:
                logger.info(f"✓ Published NO MOTION to {motion_topic}")
                
            # Publish updated camera status
            status = camera.get_status()
            client.publish(status_topic, json.dumps(status), qos=1)
            
            # Wait before next check
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        logger.info("Shutting down security camera...")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        logger.info("Security camera stopped.")


if __name__ == "__main__":
    run_security_camera()
