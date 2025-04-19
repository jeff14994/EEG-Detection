// Global variables
let ws = null;
let timeSeriesData = [];
const maxDataPoints = 50;

// Initialize WebSocket connection
function connectWebSocket() {
    ws = new WebSocket('ws://localhost:8000/ws/eeg_data');

    ws.onopen = () => {
        console.log('WebSocket Connected');
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateVisualizations(data);
    };

    ws.onerror = (error) => {
        console.error('WebSocket Error:', error);
    };

    ws.onclose = () => {
        console.log('WebSocket Disconnected');
        // Try to reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000);
    };
}

// Update visualizations with new data
function updateVisualizations(data) {
    updateEmotionState(data);
    updateBarChart(data);
    updateLineChart(data);
}

// Update emotion state display
function updateEmotionState(data) {
    document.getElementById('emotionState').textContent = data.emotion;
    document.getElementById('statusIndicator').style.backgroundColor = 
        data.emotion === 'anxious' ? 'red' : 'green';
}

// Update bar chart with new data
function updateBarChart(data) {
    const barData = [{
        x: Object.keys(data.features),
        y: Object.values(data.features),
        type: 'bar',
        marker: {
            color: data.emotion === 'anxious' ? 'red' : 'green'
        }
    }];

    Plotly.newPlot('barChart', barData, {
        title: 'EEG Power Distribution',
        xaxis: { title: 'Frequency Band' },
        yaxis: { title: 'Power' }
    });
}

// Update line chart with new data
function updateLineChart(data) {
    // Add new data point
    timeSeriesData.push({
        timestamp: new Date(data.timestamp),
        values: Object.values(data.features)
    });

    // Remove oldest data point if we exceed max points
    if (timeSeriesData.length > maxDataPoints) {
        timeSeriesData.shift();
    }

    const lineData = [{
        y: timeSeriesData.map(d => d.values[0]), // Using first feature for simplicity
        type: 'scatter',
        mode: 'lines+markers',
        name: 'EEG Power'
    }];

    Plotly.newPlot('lineChart', lineData, {
        title: 'EEG Power Time Series',
        xaxis: { title: 'Time' },
        yaxis: { title: 'Power' }
    });
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    connectWebSocket();
}); 