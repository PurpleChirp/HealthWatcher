from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
import json


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class HealthData(db.Model):
    """Model for storing health monitoring data points"""
    __tablename__ = 'health_data'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    heart_rate = db.Column(db.Integer, nullable=False)
    blood_oxygen = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    activity_level = db.Column(db.Integer, nullable=False)
    sleep_quality = db.Column(db.Integer, nullable=False)
    stress_level = db.Column(db.Integer, nullable=False)
    resting_heart_rate = db.Column(db.Integer, nullable=False)
    heart_rate_variability = db.Column(db.Float, nullable=False)
    health_score = db.Column(db.Integer, nullable=False)
    is_anomaly = db.Column(db.Boolean, default=False, nullable=False)
    emergency_mode = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'heart_rate': self.heart_rate,
            'blood_oxygen': self.blood_oxygen,
            'temperature': self.temperature,
            'activity_level': self.activity_level,
            'sleep_quality': self.sleep_quality,
            'stress_level': self.stress_level,
            'resting_heart_rate': self.resting_heart_rate,
            'heart_rate_variability': self.heart_rate_variability,
            'health_score': self.health_score,
            'is_anomaly': self.is_anomaly,
            'emergency_mode': self.emergency_mode
        }


class AnomalyResult(db.Model):
    """Model for storing anomaly detection results"""
    __tablename__ = 'anomaly_results'

    id = db.Column(db.Integer, primary_key=True)
    health_data_id = db.Column(db.Integer, db.ForeignKey(
        'health_data.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_anomaly = db.Column(db.Boolean, nullable=False)
    anomaly_score = db.Column(db.Float, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)

    # Relationship to health data
    health_data = db.relationship('HealthData', backref='anomaly_results')

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'health_data_id': self.health_data_id,
            'timestamp': self.timestamp.isoformat(),
            'is_anomaly': self.is_anomaly,
            'anomaly_score': self.anomaly_score,
            'confidence': self.confidence,
            'status': self.status,
            'risk_level': self.risk_level
        }


class HealthRecommendation(db.Model):
    """Model for storing health recommendations"""
    __tablename__ = 'health_recommendations'

    id = db.Column(db.Integer, primary_key=True)
    health_data_id = db.Column(db.Integer, db.ForeignKey(
        'health_data.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    recommendation_text = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False)  # high, medium, low
    # emergency, exercise, sleep, etc.
    category = db.Column(db.String(50), nullable=False)

    # Relationship to health data
    health_data = db.relationship('HealthData', backref='recommendations')

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'health_data_id': self.health_data_id,
            'timestamp': self.timestamp.isoformat(),
            'recommendation_text': self.recommendation_text,
            'priority': self.priority,
            'category': self.category
        }


class FingerprintScan(db.Model):
    """Model for tracking fingerprint scan events"""
    __tablename__ = 'fingerprint_scans'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    scan_type = db.Column(db.String(20), nullable=False)  # normal, emergency
    is_emergency = db.Column(db.Boolean, default=False, nullable=False)
    # For tracking scan sessions
    session_id = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        """Convert model to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'scan_type': self.scan_type,
            'is_emergency': self.is_emergency,
            'session_id': self.session_id
        }
