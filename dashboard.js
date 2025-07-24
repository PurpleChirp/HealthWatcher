/**
 * Health Monitoring Dashboard JavaScript
 * Handles real-time data updates, charts, and user interactions
 */

class HealthDashboard {
    constructor() {
        this.updateInterval = 5000; // 5 seconds
        this.isUpdating = false;
        this.chart = null;
        this.lastUpdateTime = null;
        this.emergencyMode = false;

        this.init();
    }

    init() {
        console.log('Initializing Health Dashboard...');

        // Initialize chart
        this.initChart();

        // Set up event listeners
        this.setupEventListeners();

        // Start data updates
        this.startDataUpdates();

        // Initial data load
        this.updateHealthData();
    }

    setupEventListeners() {
        // Retrain model button
        const retrainBtn = document.getElementById('retrainBtn');
        if (retrainBtn) {
            retrainBtn.addEventListener('click', () => {
                this.retrainModel();
            });
        }

        // Normal fingerprint scan button
        const normalScanBtn = document.getElementById('normalScanBtn');
        if (normalScanBtn) {
            normalScanBtn.addEventListener('click', () => {
                this.triggerNormalScan();
            });
        }

        // Emergency fingerprint scan button
        const emergencyScanBtn = document.getElementById('emergencyScanBtn');
        if (emergencyScanBtn) {
            emergencyScanBtn.addEventListener('click', () => {
                this.triggerEmergencyScan();
            });
        }

        // Stop monitoring button
        const stopBtn = document.getElementById('stopBtn');
        if (stopBtn) {
            stopBtn.addEventListener('click', () => {
                this.stopMonitoring();
            });
        }

        // View health history button
        const viewHistoryBtn = document.getElementById('viewHistoryBtn');
        if (viewHistoryBtn) {
            viewHistoryBtn.addEventListener('click', () => {
                this.viewHealthHistory();
            });
        }

        // View scan history button
        const viewScansBtn = document.getElementById('viewScansBtn');
        if (viewScansBtn) {
            viewScansBtn.addEventListener('click', () => {
                this.viewScanHistory();
            });
        }

        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopDataUpdates();
            } else {
                this.startDataUpdates();
            }
        });
    }

    initChart() {
        const ctx = document.getElementById('healthChart');
        if (!ctx) return;

        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Heart Rate',
                        data: [],
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Blood Oxygen',
                        data: [],
                        borderColor: '#0dcaf0',
                        backgroundColor: 'rgba(13, 202, 240, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y1'
                    },
                    {
                        label: 'Temperature',
                        data: [],
                        borderColor: '#ffc107',
                        backgroundColor: 'rgba(255, 193, 7, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y2'
                    },
                    {
                        label: 'Health Score',
                        data: [],
                        borderColor: '#198754',
                        backgroundColor: 'rgba(25, 135, 84, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y3'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Time'
                        }
                    },
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Heart Rate (BPM)'
                        },
                        min: 50,
                        max: 150
                    },
                    y1: {
                        type: 'linear',
                        display: false,
                        position: 'right',
                        min: 90,
                        max: 100,
                        grid: {
                            drawOnChartArea: false,
                        },
                    },
                    y2: {
                        type: 'linear',
                        display: false,
                        position: 'right',
                        min: 96,
                        max: 102
                    },
                    y3: {
                        type: 'linear',
                        display: false,
                        position: 'right',
                        min: 0,
                        max: 100
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            afterLabel: function (context) {
                                const datasetLabel = context.dataset.label;
                                let unit = '';
                                switch (datasetLabel) {
                                    case 'Heart Rate': unit = ' BPM'; break;
                                    case 'Blood Oxygen': unit = ' %'; break;
                                    case 'Temperature': unit = ' °F'; break;
                                    case 'Health Score': unit = '/100'; break;
                                }
                                return unit;
                            }
                        }
                    }
                }
            }
        });
    }

    startDataUpdates() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
        }

        this.updateTimer = setInterval(() => {
            this.updateHealthData();
        }, this.updateInterval);

        this.updateConnectionStatus(true);
    }

    stopDataUpdates() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }

        this.updateConnectionStatus(false);
    }

    async updateHealthData() {
        if (this.isUpdating) return;
        this.isUpdating = true;

        try {
            this.showLoading(true);

            const response = await fetch('/api/health-data');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Update UI with new data
            this.updateMetrics(data.health_data);
            this.updateHealthStatus(data.anomaly_result, data.health_data);
            this.updateRecommendations(data.recommendations);
            this.updateModelMetrics(data.metrics);
            this.updateChart(data.health_data);

            this.lastUpdateTime = new Date();
            this.updateLastUpdateTime();

            this.updateConnectionStatus(true);

        } catch (error) {
            console.error('Error updating health data:', error);
            this.showAlert('error', `Failed to update health data: ${error.message}`);
            this.updateConnectionStatus(false);
        } finally {
            this.showLoading(false);
            this.isUpdating = false;
        }
    }

    updateMetrics(healthData) {
        // If no health data (waiting for scan), show dashes
        if (!healthData) {
            const metricIds = ['heartRate', 'bloodOxygen', 'temperature', 'activityLevel', 'sleepQuality', 'stressLevel'];
            metricIds.forEach(id => {
                const element = document.getElementById(id);
                if (element) {
                    element.textContent = '--';
                }
            });
            return;
        }

        const metrics = [
            { id: 'heartRate', value: healthData.heart_rate },
            { id: 'bloodOxygen', value: healthData.blood_oxygen + '%' },
            { id: 'temperature', value: healthData.temperature + '°F' },
            { id: 'activityLevel', value: healthData.activity_level },
            { id: 'sleepQuality', value: healthData.sleep_quality },
            { id: 'stressLevel', value: healthData.stress_level }
        ];

        metrics.forEach(metric => {
            const element = document.getElementById(metric.id);
            if (element) {
                element.textContent = metric.value;
                element.classList.add('updated');
                setTimeout(() => element.classList.remove('updated'), 1000);
            }
        });
    }

    updateHealthStatus(anomalyResult, healthData) {
        const statusElement = document.getElementById('healthStatus');
        const indicatorElement = document.getElementById('statusIndicator');
        const scoreElement = document.getElementById('healthScore');
        const scoreBarElement = document.getElementById('healthScoreBar');

        if (statusElement && indicatorElement) {
            // Check if we're waiting for fingerprint scan
            if (anomalyResult.status === 'Waiting for fingerprint scan...') {
                statusElement.textContent = 'Waiting for scan...';
                indicatorElement.innerHTML = '<i class="fas fa-circle text-secondary"></i>';
                return;
            }

            const isAnomaly = anomalyResult.is_anomaly;
            const riskLevel = anomalyResult.risk_level;

            if (isAnomaly) {
                statusElement.textContent = `Anomaly Detected (${riskLevel} Risk)`;
                indicatorElement.innerHTML = '<i class="fas fa-circle text-danger emergency"></i>';
                this.emergencyMode = true;

                if (riskLevel === 'High') {
                    this.showAlert('danger', 'High risk health anomaly detected! Please monitor your symptoms closely.');
                } else if (riskLevel === 'Medium') {
                    this.showAlert('warning', 'Moderate health anomaly detected. Keep an eye on your metrics.');
                }
            } else {
                statusElement.textContent = 'Normal';
                indicatorElement.innerHTML = '<i class="fas fa-circle text-success normal"></i>';
                this.emergencyMode = false;
            }
        }

        if (scoreElement && scoreBarElement) {
            if (!healthData) {
                scoreElement.textContent = '--';
                scoreBarElement.style.width = '0%';
                scoreBarElement.className = 'progress-bar';
                return;
            }

            const healthScore = healthData.health_score;
            scoreElement.textContent = healthScore;
            scoreBarElement.style.width = healthScore + '%';

            // Update progress bar color based on score
            scoreBarElement.className = 'progress-bar';
            if (healthScore >= 80) {
                scoreBarElement.classList.add('bg-success');
            } else if (healthScore >= 60) {
                scoreBarElement.classList.add('bg-warning');
            } else {
                scoreBarElement.classList.add('bg-danger');
            }
        }
    }

    updateRecommendations(recommendations) {
        const listElement = document.getElementById('recommendationsList');
        if (!listElement || !recommendations.recommendations) return;

        listElement.innerHTML = '';

        recommendations.recommendations.forEach((rec, index) => {
            const recElement = document.createElement('div');
            recElement.className = `recommendation-item priority-${recommendations.priority.toLowerCase()}`;
            recElement.innerHTML = `
                <div class="d-flex align-items-start">
                    <i class="fas fa-lightbulb me-2 mt-1"></i>
                    <span>${rec}</span>
                </div>
            `;

            // Add animation delay
            recElement.style.animationDelay = `${index * 0.1}s`;
            listElement.appendChild(recElement);
        });

        // If no recommendations, show a default message
        if (recommendations.recommendations.length === 0) {
            listElement.innerHTML = '<p class="text-muted">No specific recommendations at this time. Keep monitoring your health!</p>';
        }
    }

    updateModelMetrics(metrics) {
        if (!metrics.metrics) return;

        const accuracyElement = document.getElementById('modelAccuracy');
        const samplesElement = document.getElementById('trainingSamples');
        const anomaliesElement = document.getElementById('anomaliesDetected');

        if (accuracyElement) {
            accuracyElement.textContent = (metrics.metrics.accuracy * 100).toFixed(1) + '%';
        }

        if (samplesElement) {
            samplesElement.textContent = metrics.metrics.total_samples;
        }

        if (anomaliesElement) {
            anomaliesElement.textContent = metrics.metrics.detected_anomalies;
        }
    }

    updateChart(healthData) {
        if (!this.chart) return;

        const time = new Date(healthData.timestamp).toLocaleTimeString();

        // Add new data point
        this.chart.data.labels.push(time);
        this.chart.data.datasets[0].data.push(healthData.heart_rate);
        this.chart.data.datasets[1].data.push(healthData.blood_oxygen);
        this.chart.data.datasets[2].data.push(healthData.temperature);
        this.chart.data.datasets[3].data.push(healthData.health_score);

        // Keep only last 20 data points
        const maxPoints = 20;
        if (this.chart.data.labels.length > maxPoints) {
            this.chart.data.labels.shift();
            this.chart.data.datasets.forEach(dataset => {
                dataset.data.shift();
            });
        }

        this.chart.update('none'); // Update without animation for real-time feel
    }

    async retrainModel() {
        const button = document.getElementById('retrainBtn');
        if (!button) return;

        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Retraining...';

        try {
            const response = await fetch('/api/retrain-model');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.showAlert('success', 'Model retrained successfully!');

            // Update metrics after retraining
            setTimeout(() => {
                this.updateHealthData();
            }, 1000);

        } catch (error) {
            console.error('Error retraining model:', error);
            this.showAlert('danger', `Failed to retrain model: ${error.message}`);
        } finally {
            button.disabled = false;
            button.innerHTML = originalText;
        }
    }

    showAlert(type, message) {
        const alertSection = document.getElementById('alertSection');
        const alertElement = document.getElementById('healthAlert');
        const messageElement = document.getElementById('alertMessage');

        if (alertSection && alertElement && messageElement) {
            // Set alert type
            alertElement.className = `alert alert-${type} alert-dismissible fade show`;
            messageElement.textContent = message;

            // Show alert
            alertSection.style.display = 'block';

            // Auto-hide after 5 seconds
            setTimeout(() => {
                alertSection.style.display = 'none';
            }, 5000);
        }
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            if (show) {
                overlay.classList.add('show');
            } else {
                overlay.classList.remove('show');
            }
        }
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            statusElement.textContent = connected ? 'Connected' : 'Disconnected';
            statusElement.previousElementSibling.className = connected ?
                'fas fa-wifi text-success me-1' :
                'fas fa-wifi text-danger me-1';
        }
    }

    updateLastUpdateTime() {
        const element = document.getElementById('lastUpdate');
        if (element && this.lastUpdateTime) {
            element.textContent = `Last updated: ${this.lastUpdateTime.toLocaleTimeString()}`;
        }
    }

    async triggerNormalScan() {
        const normalBtn = document.getElementById('normalScanBtn');
        const emergencyBtn = document.getElementById('emergencyScanBtn');
        const stopBtn = document.getElementById('stopBtn');
        const fingerprintSection = document.getElementById('fingerprintSection');

        if (!normalBtn) return;

        const originalText = normalBtn.innerHTML;
        normalBtn.disabled = true;
        normalBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Scanning...';

        try {
            const response = await fetch('/api/normal-scan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.showAlert('success', result.message);

            // Hide fingerprint section and show stop button
            if (fingerprintSection) fingerprintSection.style.display = 'none';
            if (stopBtn) stopBtn.style.display = 'block';

            // Force immediate update to show normal data
            setTimeout(() => {
                this.updateHealthData();
            }, 500);

        } catch (error) {
            console.error('Error triggering normal scan:', error);
            this.showAlert('danger', `Failed to start normal monitoring: ${error.message}`);
        } finally {
            normalBtn.disabled = false;
            normalBtn.innerHTML = originalText;
        }
    }

    async triggerEmergencyScan() {
        const normalBtn = document.getElementById('normalScanBtn');
        const emergencyBtn = document.getElementById('emergencyScanBtn');
        const stopBtn = document.getElementById('stopBtn');
        const fingerprintSection = document.getElementById('fingerprintSection');

        if (!emergencyBtn) return;

        const originalText = emergencyBtn.innerHTML;
        emergencyBtn.disabled = true;
        emergencyBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Scanning...';

        try {
            const response = await fetch('/api/fingerprint-scan', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.showAlert('danger', result.message);

            // Hide fingerprint section and show stop button
            if (fingerprintSection) fingerprintSection.style.display = 'none';
            if (stopBtn) stopBtn.style.display = 'block';

            // Force immediate update to show emergency data
            setTimeout(() => {
                this.updateHealthData();
            }, 500);

        } catch (error) {
            console.error('Error triggering emergency scan:', error);
            this.showAlert('danger', `Failed to start emergency monitoring: ${error.message}`);
        } finally {
            emergencyBtn.disabled = false;
            emergencyBtn.innerHTML = originalText;
        }
    }

    async stopMonitoring() {
        const stopBtn = document.getElementById('stopBtn');
        const fingerprintSection = document.getElementById('fingerprintSection');

        if (!stopBtn) return;

        const originalText = stopBtn.innerHTML;
        stopBtn.disabled = true;
        stopBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Stopping...';

        try {
            const response = await fetch('/api/reset-emergency', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.showAlert('info', result.message);

            // Show fingerprint section and hide stop button
            if (fingerprintSection) fingerprintSection.style.display = 'block';
            if (stopBtn) stopBtn.style.display = 'none';

            // Force immediate update to show waiting state
            setTimeout(() => {
                this.updateHealthData();
            }, 500);

        } catch (error) {
            console.error('Error stopping monitoring:', error);
            this.showAlert('danger', `Failed to stop monitoring: ${error.message}`);
        } finally {
            stopBtn.disabled = false;
            stopBtn.innerHTML = originalText;
        }
    }

    async viewHealthHistory() {
        const modal = new bootstrap.Modal(document.getElementById('historyModal'));
        const modalTitle = document.getElementById('historyModalTitle');
        const content = document.getElementById('historyContent');

        modalTitle.textContent = 'Health Data History';
        content.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';

        modal.show();

        try {
            const response = await fetch('/api/health-history');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            let html = `
                <div class="mb-3">
                    <h6>Total Records: ${result.total_records}</h6>
                </div>
                <div class="table-responsive">
                    <table class="table table-striped table-sm">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Heart Rate</th>
                                <th>Blood O2</th>
                                <th>Temp (°F)</th>
                                <th>Activity</th>
                                <th>Sleep</th>
                                <th>Stress</th>
                                <th>Health Score</th>
                                <th>Emergency</th>
                                <th>Anomaly</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            result.data.forEach(record => {
                const time = new Date(record.timestamp).toLocaleString();
                const emergencyBadge = record.emergency_mode ? '<span class="badge bg-danger">Yes</span>' : '<span class="badge bg-success">No</span>';
                const anomalyBadge = record.is_anomaly ? '<span class="badge bg-warning">Yes</span>' : '<span class="badge bg-info">No</span>';

                html += `
                    <tr>
                        <td>${time}</td>
                        <td>${record.heart_rate}</td>
                        <td>${record.blood_oxygen}%</td>
                        <td>${record.temperature}</td>
                        <td>${record.activity_level}</td>
                        <td>${record.sleep_quality}</td>
                        <td>${record.stress_level}</td>
                        <td>${record.health_score}</td>
                        <td>${emergencyBadge}</td>
                        <td>${anomalyBadge}</td>
                    </tr>
                `;
            });

            html += '</tbody></table></div>';
            content.innerHTML = html;

        } catch (error) {
            console.error('Error loading health history:', error);
            content.innerHTML = `<div class="alert alert-danger">Error loading health history: ${error.message}</div>`;
        }
    }

    async viewScanHistory() {
        const modal = new bootstrap.Modal(document.getElementById('historyModal'));
        const modalTitle = document.getElementById('historyModalTitle');
        const content = document.getElementById('historyContent');

        modalTitle.textContent = 'Fingerprint Scan History';
        content.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';

        modal.show();

        try {
            const response = await fetch('/api/scan-history');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            let html = `
                <div class="mb-3">
                    <h6>Total Scans: ${result.total_scans}</h6>
                </div>
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Scan Type</th>
                                <th>Emergency Mode</th>
                                <th>Session ID</th>
                            </tr>
                        </thead>
                        <tbody>
            `;

            result.data.forEach(record => {
                const time = new Date(record.timestamp).toLocaleString();
                const typeBadge = record.scan_type === 'emergency' ?
                    '<span class="badge bg-danger">Emergency</span>' :
                    '<span class="badge bg-success">Normal</span>';
                const emergencyBadge = record.is_emergency ?
                    '<span class="badge bg-danger">Yes</span>' :
                    '<span class="badge bg-success">No</span>';

                html += `
                    <tr>
                        <td>${time}</td>
                        <td>${typeBadge}</td>
                        <td>${emergencyBadge}</td>
                        <td><small>${record.session_id ? record.session_id.substring(0, 8) + '...' : 'N/A'}</small></td>
                    </tr>
                `;
            });

            html += '</tbody></table></div>';
            content.innerHTML = html;

        } catch (error) {
            console.error('Error loading scan history:', error);
            content.innerHTML = `<div class="alert alert-danger">Error loading scan history: ${error.message}</div>`;
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.healthDashboard = new HealthDashboard();
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (window.healthDashboard) {
        window.healthDashboard.stopDataUpdates();
    }
});
