// MQTT Configuration
// Use window.location.hostname to auto-detect server IP (works for both localhost and remote access)
const MQTT_BROKER = `ws://${window.location.hostname}:9001`;
const TOPICS = {
    TEMPERATURE: 'home/sensor/temperature',
    MOTION: 'home/sensor/motion',
    LAMP_STATUS: 'home/actuator/lamp/status',
    LAMP_COMMAND: 'home/actuator/lamp/command',
    LAMP_BRIGHTNESS: 'home/actuator/lamp/brightness'
};

// Global Variables
let mqttClient = null;
let realtimeChart = null;
let chartData = {
    labels: [],
    temperature: [],
    motion: []
};
const MAX_DATA_POINTS = 30;
const MAX_LOG_ENTRIES = 100;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initMQTT();
    initChart();
    initControls();
});

// ===== MQTT Connection =====
function initMQTT() {
    const options = {
        keepalive: 60,
        clientId: 'smart_home_dashboard_' + Math.random().toString(16).substr(2, 8),
        clean: true,
        reconnectPeriod: 1000
    };

    updateConnectionStatus('Connecting...', 'connecting');

    try {
        mqttClient = mqtt.connect(MQTT_BROKER, options);

        mqttClient.on('connect', () => {
            console.log('✅ Connected to MQTT broker');
            updateConnectionStatus('Connected', 'connected');

            // Subscribe to all topics
            Object.values(TOPICS).forEach(topic => {
                if (topic !== TOPICS.LAMP_COMMAND && topic !== TOPICS.LAMP_BRIGHTNESS) {
                    mqttClient.subscribe(topic, (err) => {
                        if (err) {
                            console.error(`❌ Failed to subscribe to ${topic}:`, err);
                        } else {
                            console.log(`📡 Subscribed to ${topic}`);
                        }
                    });
                }
            });
        });

        mqttClient.on('message', (topic, message) => {
            handleMqttMessage(topic, message.toString());
        });

        mqttClient.on('error', (error) => {
            console.error('❌ MQTT Error:', error);
            updateConnectionStatus('Error', 'error');
        });

        mqttClient.on('reconnect', () => {
            console.log('🔄 Reconnecting to MQTT broker...');
            updateConnectionStatus('Reconnecting...', 'connecting');
        });

        mqttClient.on('offline', () => {
            console.log('⚠️ MQTT client offline');
            updateConnectionStatus('Offline', 'error');
        });

    } catch (error) {
        console.error('❌ Failed to connect to MQTT broker:', error);
        updateConnectionStatus('Connection Failed', 'error');
    }
}

// ===== Handle MQTT Messages =====
function handleMqttMessage(topic, message) {
    console.log(`📩 Message from ${topic}:`, message);

    try {
        let data;
        try {
            data = JSON.parse(message);
        } catch (e) {
            data = { value: message };
        }

        const timestamp = new Date().toLocaleTimeString();

        switch (topic) {
            case TOPICS.TEMPERATURE:
                handleTemperature(data, timestamp);
                break;
            case TOPICS.MOTION:
                handleMotion(data, timestamp);
                break;
            case TOPICS.LAMP_STATUS:
                handleLampStatus(data, timestamp);
                break;
        }
    } catch (error) {
        console.error('❌ Error handling message:', error);
    }
}

// ===== Temperature Handler =====
function handleTemperature(data, timestamp) {
    const temperature = parseFloat(data.value || data);
    
    if (isNaN(temperature)) return;

    // Update card
    document.getElementById('tempValue').textContent = temperature.toFixed(1);

    // Update chart
    updateChart(timestamp, temperature, null);

    // Add to log
    addLogEntry(timestamp, 'Temperature Sensor', 'Temperature', `${temperature.toFixed(1)}°C`);
}

// ===== Motion Handler =====
function handleMotion(data, timestamp) {
    const motionValue = data.value !== undefined ? parseInt(data.value) : (data.status === 'motion detected' ? 1 : 0);
    const motionText = motionValue === 1 ? 'Motion Detected' : 'No Motion';
    const isMotion = motionValue === 1;

    // Update card
    const motionTextEl = document.getElementById('motionText');
    const motionIndicator = document.getElementById('motionIndicator');
    
    motionTextEl.textContent = motionText;
    motionIndicator.className = 'motion-indicator ' + (isMotion ? 'motion-active' : 'motion-inactive');

    // Update chart
    updateChart(timestamp, null, motionValue);

    // Add to log
    addLogEntry(timestamp, 'Motion Sensor', 'Motion', motionText);
}

// ===== Lamp Status Handler =====
function handleLampStatus(data, timestamp) {
    const state = (data.state || data).toUpperCase();
    const isOn = state === 'ON';

    // Update card
    const lampState = document.getElementById('lampState');
    const lampIcon = document.getElementById('lampIcon');
    
    lampState.textContent = state;
    lampState.className = 'lamp-state ' + (isOn ? 'lamp-on' : 'lamp-off');
    lampIcon.className = 'card-icon lamp-icon ' + (isOn ? 'lamp-active' : '');

    // Add to log
    addLogEntry(timestamp, 'Smart Lamp', 'Status', state);
}

// ===== Chart Initialization =====
function initChart() {
    const ctx = document.getElementById('realtimeChart').getContext('2d');
    
    realtimeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: chartData.temperature,
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y'
                },
                {
                    label: 'Motion (0/1)',
                    data: chartData.motion,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    tension: 0,
                    fill: true,
                    stepped: true,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: '#374151',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(75, 85, 99, 0.2)'
                    },
                    ticks: {
                        color: '#9ca3af',
                        maxRotation: 0,
                        autoSkipPadding: 20
                    }
                },
                y: {
                    type: 'linear',
                    position: 'left',
                    grid: {
                        color: 'rgba(75, 85, 99, 0.2)'
                    },
                    ticks: {
                        color: '#f59e0b'
                    },
                    title: {
                        display: true,
                        text: 'Temperature (°C)',
                        color: '#f59e0b'
                    }
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    min: 0,
                    max: 1,
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        color: '#10b981',
                        stepSize: 1
                    },
                    title: {
                        display: true,
                        text: 'Motion',
                        color: '#10b981'
                    }
                }
            }
        }
    });
}

// ===== Update Chart =====
function updateChart(timestamp, temperature, motion) {
    // Add new data point
    chartData.labels.push(timestamp);
    
    if (temperature !== null) {
        chartData.temperature.push(temperature);
    } else if (chartData.temperature.length > 0) {
        chartData.temperature.push(chartData.temperature[chartData.temperature.length - 1]);
    } else {
        chartData.temperature.push(null);
    }

    if (motion !== null) {
        chartData.motion.push(motion);
    } else if (chartData.motion.length > 0) {
        chartData.motion.push(chartData.motion[chartData.motion.length - 1]);
    } else {
        chartData.motion.push(null);
    }

    // Limit data points
    if (chartData.labels.length > MAX_DATA_POINTS) {
        chartData.labels.shift();
        chartData.temperature.shift();
        chartData.motion.shift();
    }

    // Update chart
    realtimeChart.update('none');
}

// ===== Event Log =====
function addLogEntry(time, source, type, value) {
    const tbody = document.getElementById('logTableBody');
    
    // Remove "no data" row if exists
    const noDataRow = tbody.querySelector('.no-data');
    if (noDataRow) {
        noDataRow.remove();
    }

    // Create new row
    const row = document.createElement('tr');
    row.className = 'log-entry fade-in';
    row.innerHTML = `
        <td>${time}</td>
        <td>${source}</td>
        <td>${type}</td>
        <td>${value}</td>
    `;

    // Insert at the top
    tbody.insertBefore(row, tbody.firstChild);

    // Limit log entries
    while (tbody.children.length > MAX_LOG_ENTRIES) {
        tbody.removeChild(tbody.lastChild);
    }
}

// ===== Controls Initialization =====
function initControls() {
    // Lamp ON button
    document.getElementById('btnOn').addEventListener('click', () => {
        publishCommand(TOPICS.LAMP_COMMAND, 'ON');
    });

    // Lamp OFF button
    document.getElementById('btnOff').addEventListener('click', () => {
        publishCommand(TOPICS.LAMP_COMMAND, 'OFF');
    });

    // Brightness slider
    const brightnessSlider = document.getElementById('brightnessSlider');
    const brightnessValue = document.getElementById('brightnessValue');

    brightnessSlider.addEventListener('input', (e) => {
        brightnessValue.textContent = e.target.value;
    });

    brightnessSlider.addEventListener('change', (e) => {
        publishCommand(TOPICS.LAMP_BRIGHTNESS, e.target.value);
        addLogEntry(
            new Date().toLocaleTimeString(),
            'Dashboard',
            'Brightness Command',
            `${e.target.value}%`
        );
    });

    // Clear log button
    document.getElementById('btnClearLog').addEventListener('click', () => {
        const tbody = document.getElementById('logTableBody');
        tbody.innerHTML = '<tr class="no-data"><td colspan="4">Log cleared</td></tr>';
    });
}

// ===== Publish MQTT Command =====
function publishCommand(topic, message) {
    if (!mqttClient || !mqttClient.connected) {
        console.error('❌ MQTT client not connected');
        alert('Not connected to MQTT broker!');
        return;
    }

    mqttClient.publish(topic, message, { qos: 1 }, (err) => {
        if (err) {
            console.error(`❌ Failed to publish to ${topic}:`, err);
        } else {
            console.log(`✅ Published to ${topic}: ${message}`);
            addLogEntry(
                new Date().toLocaleTimeString(),
                'Dashboard',
                'Command',
                `${topic.split('/').pop()}: ${message}`
            );
        }
    });
}

// ===== Connection Status Update =====
function updateConnectionStatus(text, status) {
    const statusEl = document.getElementById('connectionStatus');
    const dotEl = document.getElementById('connectionDot');

    statusEl.textContent = text;
    dotEl.className = 'status-dot status-' + status;
}
