// ============================================
// SMART HOME DASHBOARD - HTTP Polling Client
// ============================================

const API_URL = `http://${window.location.hostname}:5000`;
console.log('🌐 Dashboard initialized. API URL:', API_URL);

let pollInterval = null;
let realtimeChart = null;

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
    
    // Then poll every 2 seconds
    pollInterval = setInterval(pollOnce, 2000);
}

function pollOnce() {
    fetch(`${API_URL}/api/data`)
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.json();
        })
        .then(data => {
            updateConnectionStatus('Connected', 'connected');
            
            // Update displays
            if (data.temperature) updateTemperature(data.temperature);
            if (data.motion) updateMotion(data.motion);
            if (data.lamp_status) updateLampStatus(data.lamp_status);
            
            addChartData(data);
        })
        .catch(error => {
            console.error('❌ Poll failed:', error.message);
            updateConnectionStatus('Connection Failed', 'disconnected');
        });
}

// ===== UI UPDATES =====
function updateTemperature(data) {
    const tempValue = document.getElementById('tempValue');
    if (tempValue) {
        tempValue.textContent = `${data.value}${data.unit || '°C'}`;
        console.log(`🌡️ Temp updated: ${data.value}°C`);
        addLogEntry('🌡️ Temperature', `${data.value}°C`);
    }
}

function updateMotion(data) {
    const motionText = document.getElementById('motionText');
    const motionIndicator = document.getElementById('motionIndicator');
    
    if (motionText) {
        const text = data.value === 1 ? '🚶 Motion Detected' : '✋ No Motion';
        motionText.textContent = text;
        console.log(`📍 Motion: ${text}`);
        
        if (motionIndicator) {
            motionIndicator.className = data.value === 1 ? 'status-active' : 'status-inactive';
        }
        
        addLogEntry('📍 Motion', text);
    }
}

function updateLampStatus(data) {
    const lampState = document.getElementById('lampState');
    const lampIcon = document.getElementById('lampIcon');
    
    if (lampState) {
        const isOn = data.state.toUpperCase() === 'ON';
        lampState.textContent = isOn ? '💡 ON' : '🌑 OFF';
        lampState.className = isOn ? 'status-on' : 'status-off';
        
        if (lampIcon) {
            lampIcon.textContent = isOn ? '💡' : '🌑';
        }
        
        console.log(`💡 Lamp status: ${data.state}`);
        addLogEntry('💡 Lamp', data.state);
    }
}

function updateConnectionStatus(text, status) {
    const connStatus = document.getElementById('connectionStatus');
    if (connStatus) {
        connStatus.textContent = text;
        connStatus.className = `status-badge status-${status}`;
    }
}

// ===== LAMP CONTROL =====
function controlLamp(command) {
    console.log(`🎯 Sending lamp command: ${command}`);
    
    fetch(`${API_URL}/api/lamp/control`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: command })
    })
    .then(response => response.json())
    .then(data => {
        console.log('✅ Lamp command sent:', data);
        addLogEntry('🕹️ Control', `Lamp ${command} command sent`);
    })
    .catch(error => {
        console.error('❌ Control failed:', error);
        addLogEntry('❌ Error', `Failed to control lamp: ${error.message}`);
    });
}

// ===== CHART.JS INTEGRATION =====
function initChart() {
    const ctx = document.getElementById('realtimeChart');
    if (!ctx) return;
    
    realtimeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Temperature (°C)',
                    data: [],
                    borderColor: '#FF6384',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    tension: 0.3,
                    yAxisID: 'y'
                },
                {
                    label: 'Motion (0=No, 1=Yes)',
                    data: [],
                    borderColor: '#36A2EB',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    tension: 0.3,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            interaction: { mode: 'index', intersect: false },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: { display: true, text: 'Temperature (°C)' }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: { display: true, text: 'Motion' },
                    min: 0,
                    max: 1
                }
            },
            plugins: {
                legend: { display: true, position: 'top' }
            }
        }
    });
}

function addChartData(data) {
    if (!realtimeChart) return;
    
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    
    // Keep only last 30 data points
    if (realtimeChart.data.labels.length >= 30) {
        realtimeChart.data.labels.shift();
        realtimeChart.data.datasets[0].data.shift();
        realtimeChart.data.datasets[1].data.shift();
    }
    
    realtimeChart.data.labels.push(timeStr);
    realtimeChart.data.datasets[0].data.push(data.temperature?.value || null);
    realtimeChart.data.datasets[1].data.push(data.motion?.value || null);
    
    realtimeChart.update('none'); // No animation for smooth updates
}

// ===== LOG TABLE =====
function addLogEntry(type, message) {
    const logTable = document.getElementById('logTableBody');
    if (!logTable) return;
    
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>${timeStr}</td>
        <td>${type}</td>
        <td>${message}</td>
    `;
    
    logTable.insertBefore(row, logTable.firstChild);
    
    // Keep only last 50 entries
    while (logTable.children.length > 50) {
        logTable.removeChild(logTable.lastChild);
    }
}

// ===== CONTROLS INITIALIZATION =====
function initControls() {
    const lampOnBtn = document.getElementById('lampOnBtn');
    const lampOffBtn = document.getElementById('lampOffBtn');
    const lampToggle = document.getElementById('lampToggle');
    
    if (lampOnBtn) lampOnBtn.addEventListener('click', () => controlLamp('ON'));
    if (lampOffBtn) lampOffBtn.addEventListener('click', () => controlLamp('OFF'));
    if (lampToggle) lampToggle.addEventListener('click', () => {
        const current = document.getElementById('lampState');
        if (current && current.textContent.includes('ON')) {
            controlLamp('OFF');
        } else {
            controlLamp('ON');
        }
    });
    
    console.log('✅ Controls initialized');
}

console.log('✅ Script loaded successfully - no external MQTT library needed!');
