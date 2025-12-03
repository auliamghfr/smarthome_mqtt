// ============================================
// SMART HOME DASHBOARD - Enhanced Version
// Real-time monitoring with automation support
// ============================================

const API_URL = `http://${window.location.hostname}:5000`;
console.log('🌐 Dashboard initialized. API URL:', API_URL);

let pollInterval = null;
let temperatureChart = null;
let motionChart = null;
let lastMotionTime = 0;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ DOM loaded - initializing dashboard...');
    initDashboard();
});

// Main initialization
function initDashboard() {
    initChart();
    initControls();
    startPolling();
}

// ===== POLLING ENGINE =====
function startPolling() {
    console.log('🔄 Starting polling from API...');
    updateConnectionStatus('Connecting...', 'connecting');
    
    // First poll immediately
    pollOnce();
    
    // Then poll every 1 second for real-time updates
    pollInterval = setInterval(pollOnce, 1000);
    
    // Load events immediately and refresh every 2 seconds
    loadEvents();
    setInterval(loadEvents, 2000);
}

function pollOnce() {
    fetch(`${API_URL}/api/data`)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        })
        .then(data => {
            updateConnectionStatus('Connected', 'connected');
            
            // Update all displays
            if (data.temperature) updateTemperature(data.temperature);
            if (data.motion) updateMotion(data.motion);
            if (data.light_status) updateLightStatus(data.light_status);
            if (data.thermostat_status) updateThermostat(data.thermostat_status);
            if (data.camera_status) updateCamera(data.camera_status);
            
            // Update chart
            addChartData(data);
        })
        .catch(error => {
            console.error('❌ Poll failed:', error.message);
            updateConnectionStatus('Disconnected', 'error');
        });
}

// ===== LOAD EVENTS FROM API =====
function loadEvents() {
    fetch(`${API_URL}/api/events`)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        })
        .then(events => {
            const logTable = document.getElementById('logTableBody');
            if (!logTable) return;
            
            // Clear existing rows
            logTable.innerHTML = '';
            
            if (events.length === 0) {
                logTable.innerHTML = '<tr class="no-data"><td colspan="5">No events yet...</td></tr>';
                return;
            }
            
            // Function to get icon based on source
            const getSourceIcon = (source) => {
                if (source.includes('Temperature')) return '🌡️';
                if (source.includes('Motion') || source.includes('Camera')) return '👁️';
                if (source.includes('Thermostat')) return '⚙️';
                if (source.includes('Lamp')) return '💡';
                return '📡';
            };
            
            // Add events (most recent first)
            events.reverse().slice(0, 50).forEach(event => {
                const row = document.createElement('tr');
                row.className = 'log-entry';
                const icon = getSourceIcon(event.source);
                row.innerHTML = `
                    <td>${event.time}</td>
                    <td>${icon} ${event.source}</td>
                    <td>${event.role || 'N/A'}</td>
                    <td>${event.type}</td>
                    <td>${event.value}</td>
                `;
                logTable.appendChild(row);
            });
        })
        .catch(error => {
            console.error('❌ Failed to load events:', error.message);
        });
}

// ===== UI UPDATES =====
function updateTemperature(data) {
    const tempValue = document.getElementById('tempValue');
    if (tempValue && data.value !== undefined) {
        tempValue.textContent = data.value.toFixed(1);
        console.log(`🌡️  Temp: ${data.value}°C`);
    }
}

function updateMotion(data) {
    const motionText = document.getElementById('motionText');
    const motionIndicator = document.getElementById('motionIndicator');
    
    if (data.detected) {
        lastMotionTime = Date.now();
        motionText.textContent = '🚨 Motion Detected!';
        motionIndicator.className = 'motion-indicator motion-active';
        console.log(`🚨 Motion from ${data.camera_id}`);
    } else {
        // Auto clear motion after 5 seconds
        if (Date.now() - lastMotionTime > 5000) {
            motionText.textContent = 'No Motion';
            motionIndicator.className = 'motion-indicator motion-inactive';
        }
    }
}

function updateLightStatus(data) {
    const lampState = document.getElementById('lampState');
    const lampIcon = document.getElementById('lampIcon');
    const brightnessValue = document.getElementById('brightnessValue');
    const brightnessSlider = document.getElementById('brightnessSlider');
    
    if (lampState && data.state) {
        const isOn = data.state.toUpperCase() === 'ON';
        lampState.textContent = isOn ? '💡 ON' : '🌑 OFF';
        lampState.className = isOn ? 'lamp-state lamp-on' : 'lamp-state lamp-off';
        
        if (lampIcon) {
            lampIcon.className = isOn ? 'card-icon lamp-icon lamp-active' : 'card-icon lamp-icon';
        }
        
        if (brightnessValue && data.brightness !== undefined) {
            brightnessValue.textContent = data.brightness;
            if (brightnessSlider) {
                brightnessSlider.value = data.brightness;
            }
        }
        
        console.log(`💡 Light: ${data.state} (${data.brightness}%)`);
    }
}

function updateThermostat(data) {
    const thermostatMode = document.getElementById('thermostatMode');
    const hvacState = document.getElementById('hvacState');
    const targetTemp = document.getElementById('targetTemp');
    
    // Display HVAC state as the big text
    if (thermostatMode && data.hvac_state) {
        thermostatMode.textContent = data.hvac_state;
        
        // Color code based on HVAC state
        if (data.hvac_state === 'HEATING') {
            thermostatMode.style.color = '#ef4444'; // Red
        } else if (data.hvac_state === 'COOLING') {
            thermostatMode.style.color = '#06b6d4'; // Cyan
        } else {
            thermostatMode.style.color = '#10b981'; // Green
        }
    }
    
    // Display mode as the label
    if (hvacState && data.mode) {
        hvacState.textContent = data.mode;
    }
    
    if (targetTemp && data.target_temp !== undefined) {
        targetTemp.textContent = data.target_temp.toFixed(1);
    }
    
    console.log(`🌡️  Thermostat: ${data.mode} | ${data.hvac_state}`);
}

function updateCamera(data) {
    const automationStatus = document.getElementById('automationStatus');
    const autoIndicator = document.getElementById('autoIndicator');
    const autoText = document.getElementById('autoText');
    
    if (autoIndicator && data.active !== undefined) {
        if (data.active) {
            automationStatus?.classList.remove('inactive');
            autoIndicator.style.color = '#22c55e';
            autoText.textContent = 'Automation Active';
        } else {
            automationStatus?.classList.add('inactive');
            autoIndicator.style.color = '#64748b';
            autoText.textContent = 'Automation Paused';
        }
    }
}

function updateConnectionStatus(text, status) {
    const connStatus = document.getElementById('connectionStatus');
    const connDot = document.getElementById('connectionDot');
    
    if (connStatus) {
        connStatus.textContent = text;
    }
    
    if (connDot) {
        connDot.className = 'status-dot';
        if (status === 'connected') {
            connDot.classList.add('status-connected');
        } else if (status === 'connecting') {
            connDot.classList.add('status-connecting');
        } else {
            connDot.classList.add('status-error');
        }
    }
}

// ===== LIGHT CONTROL =====
function controlLight(command, level = null) {
    console.log(`🎯 Light command: ${command}${level !== null ? ` (${level}%)` : ''}`);
    
    const payload = level !== null 
        ? { command: 'BRIGHTNESS', level: level }
        : { command: command };
    
    fetch(`${API_URL}/api/light/control`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        console.log('✅ Light command sent:', data);
        addLogEntry('Control', 'Smart Light', `${command}${level !== null ? ` ${level}%` : ''}`);
    })
    .catch(error => {
        console.error('❌ Control failed:', error);
        addLogEntry('Error', 'System', `Failed: ${error.message}`);
    });
}

// ===== CHART.JS INTEGRATION =====
function initChart() {
    // Temperature Chart (Line)
    const tempCtx = document.getElementById('temperatureChart');
    if (tempCtx) {
        temperatureChart = new Chart(tempCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Temperature (°C)',
                        data: [],
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        tension: 0.4,
                        borderWidth: 2,
                        fill: true,
                        pointRadius: 3,
                        pointBackgroundColor: '#f59e0b',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2
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
                scales: {
                    x: {
                        grid: {
                            color: '#334155'
                        },
                        ticks: {
                            color: '#94a3b8',
                            maxRotation: 0
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: { 
                            display: true, 
                            text: 'Temperature (°C)',
                            color: '#f59e0b',
                            font: { weight: 'bold' }
                        },
                        grid: {
                            color: '#334155'
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    }
                },
                plugins: {
                    legend: { 
                        display: false
                    }
                }
            }
        });
    }

    // Motion Chart (Bar)
    const motionCtx = document.getElementById('motionChart');
    if (motionCtx) {
        motionChart = new Chart(motionCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Motion Detected',
                        data: [],
                        backgroundColor: 'rgba(16, 185, 129, 0.6)',
                        borderColor: '#10b981',
                        borderWidth: 2,
                        borderRadius: 4
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
                scales: {
                    x: {
                        grid: {
                            color: '#334155'
                        },
                        ticks: {
                            color: '#94a3b8',
                            maxRotation: 0
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        title: { 
                            display: true, 
                            text: 'Motion Events',
                            color: '#10b981',
                            font: { weight: 'bold' }
                        },
                        min: 0,
                        max: 1.2,
                        grid: {
                            color: '#334155'
                        },
                        ticks: {
                            color: '#94a3b8',
                            stepSize: 1,
                            callback: function(value) {
                                return value === 0 ? 'No Motion' : value === 1 ? 'Motion' : '';
                            }
                        }
                    }
                },
                plugins: {
                    legend: { 
                        display: false
                    }
                }
            }
        });
    }
}

function addChartData(data) {
    if (!temperatureChart || !motionChart) return;
    
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', { 
        hour12: false, 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    });
    
    // Keep only last 30 data points
    if (temperatureChart.data.labels.length >= 30) {
        temperatureChart.data.labels.shift();
        temperatureChart.data.datasets[0].data.shift();
        motionChart.data.labels.shift();
        motionChart.data.datasets[0].data.shift();
    }
    
    temperatureChart.data.labels.push(timeStr);
    temperatureChart.data.datasets[0].data.push(data.temperature?.value || null);
    
    motionChart.data.labels.push(timeStr);
    motionChart.data.datasets[0].data.push(data.motion?.detected ? 1 : 0);
    
    temperatureChart.update('none'); // No animation for smooth updates
    motionChart.update('none');
}

// ===== LOG TABLE =====
function addLogEntry(type, source, value) {
    const logTable = document.getElementById('logTableBody');
    if (!logTable) return;
    
    // Remove "no data" row if exists
    const noDataRow = logTable.querySelector('.no-data');
    if (noDataRow) {
        noDataRow.remove();
    }
    
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    
    const row = document.createElement('tr');
    row.className = 'log-entry';
    row.innerHTML = `
        <td>${timeStr}</td>
        <td>${source}</td>
        <td>${type}</td>
        <td>${value}</td>
    `;
    
    logTable.insertBefore(row, logTable.firstChild);
    
    // Keep only last 50 entries
    while (logTable.children.length > 50) {
        logTable.removeChild(logTable.lastChild);
    }
}

// ===== CONTROLS INITIALIZATION =====
function initControls() {
    // Light ON button
    const btnOn = document.getElementById('btnOn');
    if (btnOn) {
        btnOn.addEventListener('click', () => controlLight('ON'));
    }
    
    // Light OFF button
    const btnOff = document.getElementById('btnOff');
    if (btnOff) {
        btnOff.addEventListener('click', () => controlLight('OFF'));
    }
    
    // Clear log button
    const btnClearLog = document.getElementById('btnClearLog');
    if (btnClearLog) {
        btnClearLog.addEventListener('click', () => {
            const logTable = document.getElementById('logTableBody');
            if (logTable) {
                logTable.innerHTML = '<tr class="no-data"><td colspan="5">Log cleared</td></tr>';
            }
        });
    }
    
    console.log('✅ Controls initialized');
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
});

console.log('✅ Smart Home Dashboard loaded successfully!');
