import os
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from health_monitor import HealthMonitor
from models import db, HealthData, AnomalyResult, HealthRecommendation, FingerprintScan
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "health_monitor_secret_key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
db.init_app(app)

# Initialize health monitor
health_monitor = HealthMonitor()

# Global flags for system state
emergency_mode = False
monitoring_active = False  # Only generate data when fingerprint is scanned

# Create database tables
with app.app_context():
    db.create_all()
    logging.info("Database tables created successfully")


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/health-data')
def get_health_data():
    """API endpoint to get current health data and analysis"""
    global monitoring_active

    try:
        # Only generate data if monitoring is active (after fingerprint scan)
        if not monitoring_active:
            return jsonify({
                'health_data': None,
                'anomaly_result': {'is_anomaly': False, 'status': 'Waiting for fingerprint scan...', 'risk_level': 'None'},
                'recommendations': {'recommendations': ['Place your finger on the sensor to start health monitoring'], 'priority': 'low'},
                'metrics': {'is_trained': True, 'training_accuracy': 0.0, 'metrics': {'accuracy': 0.0, 'total_samples': 0, 'detected_anomalies': 0}},
                'timestamp': datetime.now().isoformat(),
                'monitoring_active': False
            })

        # Generate new health data (modify for emergency mode)
        current_data = health_monitor.generate_current_data(
            emergency_mode=emergency_mode)

        # Save health data to database
        health_record = HealthData(
            heart_rate=current_data['heart_rate'],
            blood_oxygen=current_data['blood_oxygen'],
            temperature=current_data['temperature'],
            activity_level=current_data['activity_level'],
            sleep_quality=current_data['sleep_quality'],
            stress_level=current_data['stress_level'],
            resting_heart_rate=current_data['resting_heart_rate'],
            heart_rate_variability=current_data['heart_rate_variability'],
            health_score=current_data['health_score'],
            is_anomaly=current_data['is_anomaly'],
            emergency_mode=emergency_mode
        )
        db.session.add(health_record)
        db.session.commit()

        # Detect anomalies
        anomaly_result = health_monitor.detect_anomaly(current_data)

        # Save anomaly result to database
        anomaly_record = AnomalyResult(
            health_data_id=health_record.id,
            is_anomaly=anomaly_result['is_anomaly'],
            anomaly_score=anomaly_result['anomaly_score'],
            confidence=anomaly_result['confidence'],
            status=anomaly_result['status'],
            risk_level=anomaly_result['risk_level']
        )
        db.session.add(anomaly_record)
        db.session.commit()

        # Get recommendations
        recommendations = health_monitor.get_recommendations(
            current_data, anomaly_result)

        # Save recommendations to database
        for rec_text in recommendations['recommendations']:
            recommendation = HealthRecommendation(
                health_data_id=health_record.id,
                recommendation_text=rec_text,
                priority=recommendations['priority'],
                category='general'  # Could be enhanced to categorize recommendations
            )
            db.session.add(recommendation)
        db.session.commit()

        # Get model metrics
        metrics = health_monitor.get_model_metrics()

        # Convert numpy types to Python native types for JSON serialization
        def convert_numpy_types(obj):
            if isinstance(obj, dict):
                return {k: convert_numpy_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            elif hasattr(obj, 'item'):  # numpy scalar
                return obj.item()
            else:
                return obj

        response = {
            'health_data': convert_numpy_types(current_data),
            'anomaly_result': convert_numpy_types(anomaly_result),
            'recommendations': convert_numpy_types(recommendations),
            'metrics': convert_numpy_types(metrics),
            'timestamp': current_data['timestamp'],
            'database_id': health_record.id
        }

        return jsonify(response)

    except Exception as e:
        logging.error(f"Error getting health data: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/historical-data')
def get_historical_data():
    """API endpoint to get historical health data for charts"""
    try:
        historical_data = health_monitor.get_historical_data()
        return jsonify(historical_data)

    except Exception as e:
        logging.error(f"Error getting historical data: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/retrain-model')
def retrain_model():
    """API endpoint to retrain the anomaly detection model"""
    try:
        health_monitor.retrain_model()
        return jsonify({'message': 'Model retrained successfully'})

    except Exception as e:
        logging.error(f"Error retraining model: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/fingerprint-scan', methods=['POST'])
def fingerprint_scan():
    """API endpoint to simulate fingerprint scan and trigger emergency mode"""
    global emergency_mode, monitoring_active
    try:
        emergency_mode = True
        monitoring_active = True

        # Create a session ID for this scan
        session_id = str(uuid.uuid4())
        session['scan_session_id'] = session_id

        # Save fingerprint scan record
        scan_record = FingerprintScan(
            scan_type='emergency',
            is_emergency=True,
            session_id=session_id
        )
        db.session.add(scan_record)
        db.session.commit()

        logging.info(
            "Emergency mode activated via fingerprint scan - monitoring started")
        return jsonify({
            'success': True,
            'message': 'Fingerprint detected! Emergency health scenario activated - critical health metrics detected!',
            'mode': 'emergency',
            'scan_id': scan_record.id
        })

    except Exception as e:
        logging.error(f"Error activating emergency mode: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/normal-scan', methods=['POST'])
def normal_scan():
    """API endpoint for normal fingerprint scan (good health)"""
    global emergency_mode, monitoring_active
    try:
        emergency_mode = False
        monitoring_active = True

        # Create a session ID for this scan
        session_id = str(uuid.uuid4())
        session['scan_session_id'] = session_id

        # Save fingerprint scan record
        scan_record = FingerprintScan(
            scan_type='normal',
            is_emergency=False,
            session_id=session_id
        )
        db.session.add(scan_record)
        db.session.commit()

        logging.info("Normal monitoring activated via fingerprint scan")
        return jsonify({
            'success': True,
            'message': 'Fingerprint detected! Health monitoring started - all metrics normal.',
            'mode': 'normal',
            'scan_id': scan_record.id
        })

    except Exception as e:
        logging.error(f"Error activating normal mode: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/reset-emergency', methods=['POST'])
def reset_emergency():
    """API endpoint to reset emergency mode"""
    global emergency_mode, monitoring_active
    try:
        emergency_mode = False
        monitoring_active = False

        # Clear session data
        if 'scan_session_id' in session:
            session.pop('scan_session_id')

        logging.info("Monitoring stopped - waiting for next fingerprint scan")
        return jsonify({
            'success': True,
            'message': 'Monitoring stopped. Place finger on sensor to scan again.',
            'mode': 'stopped'
        })

    except Exception as e:
        logging.error(f"Error resetting emergency mode: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health-history')
def get_health_history():
    """API endpoint to get historical health data from database"""
    try:
        # Get recent health data (last 50 records)
        health_records = HealthData.query.order_by(
            HealthData.timestamp.desc()).limit(50).all()

        history = []
        for record in health_records:
            history.append(record.to_dict())

        return jsonify({
            'success': True,
            'data': history,
            'total_records': len(history)
        })

    except Exception as e:
        logging.error(f"Error getting health history: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scan-history')
def get_scan_history():
    """API endpoint to get fingerprint scan history"""
    try:
        # Get recent scans (last 20 records)
        scan_records = FingerprintScan.query.order_by(
            FingerprintScan.timestamp.desc()).limit(20).all()

        scans = []
        for record in scan_records:
            scans.append(record.to_dict())

        return jsonify({
            'success': True,
            'data': scans,
            'total_scans': len(scans)
        })

    except Exception as e:
        logging.error(f"Error getting scan history: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
