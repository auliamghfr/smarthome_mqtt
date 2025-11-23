# Dockerfile for IoT Devices
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install paho-mqtt library
RUN pip install --no-cache-dir paho-mqtt

# Copy all Python scripts
COPY *.py /app/

# Default command (will be overridden in docker-compose)
CMD ["python", "run_device.py"]
