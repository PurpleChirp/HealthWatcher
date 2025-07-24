import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import logging
import joblib


class AnomalyDetector:
    """Anomaly detection system using Isolation Forest"""

    def __init__(self, contamination=0.1, random_state=42):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.feature_columns = [
            'heart_rate', 'blood_oxygen', 'temperature', 'activity_level',
            'sleep_quality', 'stress_level', 'resting_heart_rate', 'heart_rate_variability'
        ]
        self.is_trained = False
        self.training_accuracy = None
        self.training_metrics = {}

    def _prepare_features(self, data):
        """Prepare features for model training or prediction"""
        if isinstance(data, dict):
            # Single data point
            features = np.array([[data[col] for col in self.feature_columns]])
        elif isinstance(data, list):
            # Multiple data points
            features = np.array(
                [[point[col] for col in self.feature_columns] for point in data])
        else:
            raise ValueError(
                "Data must be a dictionary or list of dictionaries")

        return features

    def train(self, training_data):
        """Train the anomaly detection model"""
        logging.info(
            f"Training anomaly detection model with {len(training_data)} data points...")

        try:
            # Prepare features
            X = self._prepare_features(training_data)

            # Scale features
            X_scaled = self.scaler.fit_transform(X)

            # Train the model
            self.model.fit(X_scaled)

            # Evaluate on training data
            predictions = self.model.predict(X_scaled)

            # Convert predictions to binary (1 for normal, -1 for anomaly -> 0 for normal, 1 for anomaly)
            binary_predictions = np.where(predictions == -1, 1, 0)

            # Get actual labels if available
            actual_labels = np.array(
                [1 if point.get('is_anomaly', False) else 0 for point in training_data])

            # Calculate metrics
            self.training_accuracy = accuracy_score(
                actual_labels, binary_predictions)

            # Store additional metrics
            self.training_metrics = {
                'accuracy': self.training_accuracy,
                'confusion_matrix': confusion_matrix(actual_labels, binary_predictions).tolist(),
                'classification_report': classification_report(actual_labels, binary_predictions, output_dict=True),
                'total_samples': len(training_data),
                'detected_anomalies': np.sum(binary_predictions),
                'actual_anomalies': np.sum(actual_labels)
            }

            self.is_trained = True

            logging.info(
                f"Model trained successfully. Accuracy: {self.training_accuracy:.3f}")
            logging.info(
                f"Detected {self.training_metrics['detected_anomalies']} anomalies out of {len(training_data)} samples")

        except Exception as e:
            logging.error(f"Error training model: {str(e)}")
            raise

    def predict(self, data_point):
        """Predict if a data point is an anomaly"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        try:
            # Prepare features
            X = self._prepare_features(data_point)

            # Scale features
            X_scaled = self.scaler.transform(X)

            # Make prediction
            prediction = self.model.predict(X_scaled)[0]
            anomaly_score = self.model.decision_function(X_scaled)[0]

            # Convert prediction (-1 for anomaly, 1 for normal)
            is_anomaly = prediction == -1

            # Calculate confidence (distance from decision boundary)
            confidence = abs(anomaly_score)

            result = {
                'is_anomaly': bool(is_anomaly),
                'anomaly_score': float(anomaly_score),
                'confidence': float(confidence),
                'status': 'Anomaly Detected' if is_anomaly else 'Normal',
                'risk_level': self._get_risk_level(anomaly_score, is_anomaly)
            }

            logging.debug(f"Anomaly prediction: {result}")

            return result

        except Exception as e:
            logging.error(f"Error making prediction: {str(e)}")
            raise

    def _get_risk_level(self, anomaly_score, is_anomaly):
        """Determine risk level based on anomaly score"""
        if not is_anomaly:
            return 'Low'

        # For anomalies, determine severity based on how negative the score is
        if anomaly_score < -0.1:
            return 'High'
        elif anomaly_score < -0.05:
            return 'Medium'
        else:
            return 'Low'

    def get_metrics(self):
        """Get model performance metrics"""
        if not self.is_trained:
            return {'error': 'Model not trained yet'}

        return {
            'is_trained': self.is_trained,
            'training_accuracy': self.training_accuracy,
            'metrics': self.training_metrics
        }

    def get_feature_importance(self):
        """Get feature importance (simplified for Isolation Forest)"""
        if not self.is_trained:
            return None

        # Isolation Forest doesn't have direct feature importance,
        # but we can provide the features used
        return {
            'features': self.feature_columns,
            'note': 'Isolation Forest uses all features for anomaly detection'
        }

    def save_model(self, filepath):
        """Save the trained model to disk"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")

        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'training_metrics': self.training_metrics
        }

        joblib.dump(model_data, filepath)
        logging.info(f"Model saved to {filepath}")

    def load_model(self, filepath):
        """Load a trained model from disk"""
        try:
            model_data = joblib.load(filepath)

            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_columns = model_data['feature_columns']
            self.training_metrics = model_data['training_metrics']
            self.training_accuracy = self.training_metrics.get('accuracy', 0)
            self.is_trained = True

            logging.info(f"Model loaded from {filepath}")

        except Exception as e:
            logging.error(f"Error loading model: {str(e)}")
            raise
