import logging
from datetime import datetime


class HealthRecommendationEngine:
    """Generates health recommendations based on current metrics and anomaly status"""

    def __init__(self):
        # Define recommendation templates for different conditions
        self.recommendations = {
            'heart_rate': {
                'high': [
                    "Your heart rate is elevated. Consider taking slow, deep breaths.",
                    "Try some light stretching or meditation to help lower your heart rate.",
                    "Avoid caffeine and consider hydrating with water.",
                    "If this persists, consider consulting with a healthcare provider."
                ],
                'low': [
                    "Your heart rate is lower than normal. This might be due to rest or fitness.",
                    "If you feel dizzy or weak, consider light movement or sitting up slowly.",
                    "Monitor for any symptoms like fatigue or dizziness.",
                    "Consider consulting a healthcare provider if this is unusual for you."
                ]
            },
            'blood_oxygen': {
                'low': [
                    "Your blood oxygen level is below normal. Ensure good ventilation.",
                    "Try taking slow, deep breaths to improve oxygen saturation.",
                    "Consider moving to fresh air if you're in a stuffy environment.",
                    "If levels remain low or you feel short of breath, seek medical attention."
                ]
            },
            'temperature': {
                'high': [
                    "Your body temperature is elevated. Stay hydrated and rest.",
                    "Consider removing excess clothing and staying in a cool environment.",
                    "Monitor your temperature regularly and watch for other symptoms.",
                    "If fever persists or rises above 101°F, consider consulting a healthcare provider."
                ],
                'low': [
                    "Your body temperature is lower than normal. Keep warm and stay active.",
                    "Consider warm beverages and additional clothing.",
                    "Light physical activity can help raise body temperature.",
                    "If you feel very cold or shivering persists, seek warmth immediately."
                ]
            },
            'activity_level': {
                'low': [
                    "Your activity level is quite low today. Consider some light movement.",
                    "Try a short walk or gentle stretching to boost your activity.",
                    "Even small movements can improve circulation and mood.",
                    "Set a goal for gradual increase in daily activity."
                ],
                'high': [
                    "You've been very active! Make sure to stay hydrated and rest when needed.",
                    "Listen to your body and take breaks if you feel fatigued.",
                    "Consider some gentle stretching to help with recovery.",
                    "Ensure you're getting adequate nutrition for your activity level."
                ]
            },
            'sleep_quality': {
                'poor': [
                    "Your sleep quality seems poor. Consider establishing a regular bedtime routine.",
                    "Avoid screens and caffeine before bedtime for better sleep.",
                    "Create a comfortable, cool, and dark sleeping environment.",
                    "If sleep issues persist, consider consulting with a healthcare provider."
                ]
            },
            'stress_level': {
                'high': [
                    "Your stress level is elevated. Try some relaxation techniques.",
                    "Consider deep breathing exercises or short meditation sessions.",
                    "Take breaks from stressful activities when possible.",
                    "Physical activity or talking to someone can help reduce stress."
                ]
            },
            'general_anomaly': [
                "We've detected some unusual patterns in your health data.",
                "Consider monitoring your symptoms and how you're feeling overall.",
                "Maintain regular healthy habits: proper sleep, nutrition, and hydration.",
                "If you're experiencing any concerning symptoms, consult with a healthcare provider."
            ],
            'general_healthy': [
                "Your health metrics look good! Keep up the healthy habits.",
                "Continue with regular exercise, proper sleep, and good nutrition.",
                "Stay hydrated throughout the day.",
                "Regular monitoring helps maintain awareness of your health patterns."
            ]
        }

    def get_recommendations(self, data_point, anomaly_result):
        """Generate personalized recommendations based on health data and anomaly status"""
        recommendations = []

        try:
            # Check if anomaly was detected
            if anomaly_result.get('is_anomaly', False):
                recommendations.extend(self.recommendations['general_anomaly'])

                # Add specific recommendations based on risk level
                risk_level = anomaly_result.get('risk_level', 'Low')
                if risk_level == 'High':
                    recommendations.append(
                        "⚠️ High risk detected - consider immediate attention to your health metrics.")
                elif risk_level == 'Medium':
                    recommendations.append(
                        "⚡ Moderate concern - monitor your symptoms closely.")

            # Analyze individual metrics for specific recommendations
            self._analyze_heart_rate(data_point, recommendations)
            self._analyze_blood_oxygen(data_point, recommendations)
            self._analyze_temperature(data_point, recommendations)
            self._analyze_activity_level(data_point, recommendations)
            self._analyze_sleep_quality(data_point, recommendations)
            self._analyze_stress_level(data_point, recommendations)

            # If no specific issues found and no anomaly, add general healthy recommendations
            if not anomaly_result.get('is_anomaly', False) and len(recommendations) == 0:
                recommendations.extend(
                    self.recommendations['general_healthy'][:2])

            # Add health score-based recommendations
            health_score = data_point.get('health_score', 100)
            if health_score < 70:
                recommendations.append(
                    "Your overall health score suggests room for improvement in multiple areas.")
            elif health_score >= 90:
                recommendations.append(
                    "Excellent health score! You're maintaining great health habits.")

            # Limit recommendations to avoid overwhelming the user
            if len(recommendations) > 4:
                recommendations = recommendations[:4]

            # Add timestamps and priority
            recommendation_data = {
                'recommendations': recommendations,
                'priority': self._get_priority_level(anomaly_result, data_point),
                'generated_at': datetime.now().isoformat(),
                'health_score': health_score,
                'total_recommendations': len(recommendations)
            }

            logging.debug(f"Generated {len(recommendations)} recommendations")

            return recommendation_data

        except Exception as e:
            logging.error(f"Error generating recommendations: {str(e)}")
            return {
                'recommendations': ["Unable to generate recommendations at this time."],
                'priority': 'Low',
                'generated_at': datetime.now().isoformat(),
                'error': str(e)
            }

    def _analyze_heart_rate(self, data_point, recommendations):
        """Analyze heart rate and add specific recommendations"""
        hr = data_point.get('heart_rate', 75)

        if hr > 100:
            recommendations.extend(
                self.recommendations['heart_rate']['high'][:2])
        elif hr < 60:
            recommendations.extend(
                self.recommendations['heart_rate']['low'][:2])

    def _analyze_blood_oxygen(self, data_point, recommendations):
        """Analyze blood oxygen and add specific recommendations"""
        spo2 = data_point.get('blood_oxygen', 98)

        if spo2 < 95:
            recommendations.extend(
                self.recommendations['blood_oxygen']['low'][:2])

    def _analyze_temperature(self, data_point, recommendations):
        """Analyze temperature and add specific recommendations"""
        temp = data_point.get('temperature', 98.6)

        if temp > 99.5:
            recommendations.extend(
                self.recommendations['temperature']['high'][:2])
        elif temp < 97:
            recommendations.extend(
                self.recommendations['temperature']['low'][:2])

    def _analyze_activity_level(self, data_point, recommendations):
        """Analyze activity level and add specific recommendations"""
        activity = data_point.get('activity_level', 5)

        if activity < 2:
            recommendations.extend(
                self.recommendations['activity_level']['low'][:1])
        elif activity > 8:
            recommendations.extend(
                self.recommendations['activity_level']['high'][:1])

    def _analyze_sleep_quality(self, data_point, recommendations):
        """Analyze sleep quality and add specific recommendations"""
        sleep = data_point.get('sleep_quality', 7)

        if sleep < 5:
            recommendations.extend(
                self.recommendations['sleep_quality']['poor'][:1])

    def _analyze_stress_level(self, data_point, recommendations):
        """Analyze stress level and add specific recommendations"""
        stress = data_point.get('stress_level', 4)

        if stress > 7:
            recommendations.extend(
                self.recommendations['stress_level']['high'][:1])

    def _get_priority_level(self, anomaly_result, data_point):
        """Determine priority level for recommendations"""
        if anomaly_result.get('is_anomaly', False):
            risk_level = anomaly_result.get('risk_level', 'Low')
            if risk_level == 'High':
                return 'High'
            elif risk_level == 'Medium':
                return 'Medium'

        # Check for critical individual metrics
        hr = data_point.get('heart_rate', 75)
        spo2 = data_point.get('blood_oxygen', 98)
        temp = data_point.get('temperature', 98.6)

        if hr > 120 or hr < 50 or spo2 < 90 or temp > 101 or temp < 95:
            return 'High'
        elif hr > 100 or hr < 60 or spo2 < 95 or temp > 99.5 or temp < 97:
            return 'Medium'

        return 'Low'
