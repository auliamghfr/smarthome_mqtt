"""
Device launcher script
Runs the appropriate device based on DEVICE_TYPE environment variable
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DeviceLauncher")


def main():
    """
    Launch the appropriate device based on DEVICE_TYPE
    """
    device_type = os.getenv("DEVICE_TYPE", "")
    
    if not device_type:
        logger.error("DEVICE_TYPE environment variable not set!")
        logger.error("Valid values: temp_sensor, motion_sensor, smart_lamp")
        sys.exit(1)
    
    logger.info(f"Launching device: {device_type}")
    
    try:
        if device_type == "temp_sensor":
            from temp_sensor import run_temp_sensor
            run_temp_sensor()
        elif device_type == "motion_sensor":
            from motion_sensor import run_motion_sensor
            run_motion_sensor()
        elif device_type == "smart_lamp":
            from smart_lamp import run_smart_lamp
            run_smart_lamp()
        else:
            logger.error(f"Unknown device type: {device_type}")
            logger.error("Valid values: temp_sensor, motion_sensor, smart_lamp")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to launch device: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
