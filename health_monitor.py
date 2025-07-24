import logging
from datetime import datetime, timedelta
from data_simulator import HealthDataSimulator
from anomaly_detector import AnomalyDetector
from recommendations import HealthRecommendationEngine


class HealthMonitor:
    """Main health monitoring system that coordinates data generation, anomaly detection, and recommendations"""

    def __init__(self):
        self.data_simulator = HealthDataSimulator()
        self.anomaly_detector = AnomalyDetector()
        self.recommendation_engine = HealthRecommendationEngine()
        self.historical_data = []

        # Initialize with some historical data and train the initial model
        self._initialize_system()

    def _initialize_system(self):
        """Initialize the system with historical data and train the anomaly detection model"""
        logging.info("Initializing health monitoring system...")

        # Generate initial historical data for training
        for i in range(100):  # Generate 100 historical data points
            timestamp = datetime.now() - timedelta(hours=100-i)
            data_point = self.data_simulator.generate_data_point(timestamp)
            self.historical_data.append(data_point)

        # Train the initial anomaly detection model
        self.anomaly_detector.train(self.historical_data)

        logging.info("Health monitoring system initialized successfully")

    def generate_current_data(self, emergency_mode=False):
        """Generate current health data point"""
        if emergency_mode:
            current_data = self.data_simulator.generate_emergency_data_point()
        else:
            current_data = self.data_simulator.generate_data_point()

        # Add to historical data (keep last 200 points)
        self.historical_data.append(current_data)
        if len(self.historical_data) > 200:
            self.historical_data.pop(0)

        return current_data

    def detect_anomaly(self, data_point):
        """Detect if the current data point is an anomaly"""
        return self.anomaly_detector.predict(data_point)

    def get_recommendations(self, data_point, anomaly_result):
        """Get health recommendations based on current data and anomaly status"""
        return self.recommendation_engine.get_recommendations(data_point, anomaly_result)

    def get_model_metrics(self):
        """Get current model performance metrics"""
        return self.anomaly_detector.get_metrics()

    def get_historical_data(self, hours=24):
        """Get historical data for the specified number of hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_data = [
            data for data in self.historical_data
            if datetime.fromisoformat(data['timestamp']) > cutoff_time
        ]
        return recent_data

    def retrain_model(self):
        """Retrain the anomaly detection model with latest data"""
        logging.info("Retraining anomaly detection model...")
        self.anomaly_detector.train(self.historical_data)
        logging.info("Model retrained successfully")
