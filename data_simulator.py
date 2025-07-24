import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import logging


class HealthDataSimulator:
    """Simulates realistic health data from wearable devices"""

    def __init__(self):
        # Define realistic ranges for health metrics
        self.baseline_ranges = {
            'heart_rate': {'min': 60, 'max': 100, 'mean': 75, 'std': 10},
            'blood_oxygen': {'min': 95, 'max': 100, 'mean': 98, 'std': 1.5},
            'temperature': {'min': 96.5, 'max': 99.5, 'mean': 98.6, 'std': 0.5},
            'activity_level': {'min': 0, 'max': 10, 'mean': 5, 'std': 2},
            'sleep_quality': {'min': 1, 'max': 10, 'mean': 7, 'std': 1.5},
            'stress_level': {'min': 1, 'max': 10, 'mean': 4, 'std': 2}
        }

        # Define patterns for different times of day
        self.time_patterns = {
            'morning': {'heart_rate_multiplier': 1.1, 'activity_multiplier': 1.3},
            'afternoon': {'heart_rate_multiplier': 1.0, 'activity_multiplier': 1.5},
            'evening': {'heart_rate_multiplier': 0.95, 'activity_multiplier': 1.2},
            'night': {'heart_rate_multiplier': 0.8, 'activity_multiplier': 0.2}
        }

        # Anomaly simulation parameters
        self.anomaly_probability = 0.05  # 5% chance of anomaly

    def _get_time_pattern(self, timestamp=None):
        """Get time-based pattern adjustments"""
        if timestamp is None:
            timestamp = datetime.now()

        hour = timestamp.hour

        if 6 <= hour < 12:
            return self.time_patterns['morning']
        elif 12 <= hour < 18:
            return self.time_patterns['afternoon']
        elif 18 <= hour < 22:
            return self.time_patterns['evening']
        else:
            return self.time_patterns['night']

    def _simulate_anomaly(self, base_value, metric_name):
        """Simulate anomalous values for a given metric"""
        anomaly_types = {
            'heart_rate': [0.6, 1.8],  # Very low or very high
            'blood_oxygen': [0.85, 1.0],  # Only low values are concerning
            'temperature': [0.95, 1.05],  # Fever or hypothermia
            'activity_level': [0.1, 2.0],  # Very low or very high
            'sleep_quality': [0.3, 1.0],  # Only poor sleep is concerning
            'stress_level': [1.0, 2.5]  # Only high stress is concerning
        }

        multipliers = anomaly_types.get(metric_name, [0.5, 2.0])
        multiplier = random.choice(multipliers)

        return base_value * multiplier

    def generate_data_point(self, timestamp=None):
        """Generate a single health data point"""
        if timestamp is None:
            timestamp = datetime.now()

        # Get time-based adjustments
        time_pattern = self._get_time_pattern(timestamp)

        # Initialize data point
        data_point = {
            'timestamp': timestamp.isoformat(),
            'is_anomaly': False
        }

        # Determine if this should be an anomalous data point
        is_anomaly = random.random() < self.anomaly_probability

        for metric, ranges in self.baseline_ranges.items():
            # Generate base value using normal distribution
            base_value = np.random.normal(ranges['mean'], ranges['std'])

            # Apply time-based adjustments
            if metric == 'heart_rate' and 'heart_rate_multiplier' in time_pattern:
                base_value *= time_pattern['heart_rate_multiplier']
            elif metric == 'activity_level' and 'activity_multiplier' in time_pattern:
                base_value *= time_pattern['activity_multiplier']

            # Apply anomaly if needed
            if is_anomaly and random.random() < 0.3:  # 30% chance this specific metric is anomalous
                base_value = self._simulate_anomaly(base_value, metric)
                data_point['is_anomaly'] = True

            # Ensure values stay within realistic bounds
            base_value = max(ranges['min'], min(ranges['max'], base_value))

            # Round appropriately
            if metric in ['heart_rate', 'activity_level', 'sleep_quality', 'stress_level']:
                data_point[metric] = round(base_value)
            else:
                data_point[metric] = round(base_value, 1)

        # Add some derived metrics
        data_point['resting_heart_rate'] = max(
            50, data_point['heart_rate'] - random.randint(10, 20))
        data_point['heart_rate_variability'] = round(random.uniform(20, 50), 1)

        # Calculate a simple health score (0-100)
        health_score = self._calculate_health_score(data_point)
        data_point['health_score'] = health_score

        logging.debug(f"Generated data point: {data_point}")

        return data_point

    def _calculate_health_score(self, data_point):
        """Calculate a simple health score based on all metrics"""
        score = 100

        # Heart rate scoring
        hr = data_point['heart_rate']
        if hr < 60 or hr > 100:
            score -= 15
        elif hr < 50 or hr > 120:
            score -= 30

        # Blood oxygen scoring
        spo2 = data_point['blood_oxygen']
        if spo2 < 95:
            score -= 25
        elif spo2 < 90:
            score -= 50

        # Temperature scoring
        temp = data_point['temperature']
        if temp < 97 or temp > 99:
            score -= 10
        elif temp < 96 or temp > 100:
            score -= 20

        # Activity level scoring (very low or very high activity can be concerning)
        activity = data_point['activity_level']
        if activity < 2:
            score -= 5
        elif activity > 8:
            score -= 5

        # Sleep quality scoring
        sleep = data_point['sleep_quality']
        if sleep < 5:
            score -= 15
        elif sleep < 3:
            score -= 25

        # Stress level scoring
        stress = data_point['stress_level']
        if stress > 7:
            score -= 10
        elif stress > 8:
            score -= 20

        return max(0, min(100, score))

    def generate_batch_data(self, num_points=100, start_time=None):
        """Generate a batch of health data points"""
        if start_time is None:
            start_time = datetime.now()

        data_points = []
        for i in range(num_points):
            timestamp = start_time + \
                timedelta(minutes=i * 15)  # 15-minute intervals
            data_point = self.generate_data_point(timestamp)
            data_points.append(data_point)

        return data_points

    def generate_emergency_data_point(self, timestamp=None):
        """Generate emergency health data point with critical values (red metrics)"""
        if timestamp is None:
            timestamp = datetime.now()

        # Critical emergency values that will trigger alerts
        data_point = {
            'timestamp': timestamp.isoformat(),
            'is_anomaly': True,
            'heart_rate': 150,  # Very high heart rate
            'blood_oxygen': 88,  # Low oxygen level
            'temperature': 103.2,  # High fever
            'activity_level': 10,  # Maximum activity
            'sleep_quality': 2,  # Poor sleep
            'stress_level': 10,  # Maximum stress
            'resting_heart_rate': 85,  # High resting heart rate
            'heart_rate_variability': 15.0,  # Low variability (bad sign)
            'health_score': 25  # Very low health score
        }

        logging.info(f"Generated EMERGENCY data point: {data_point}")

        return data_point
