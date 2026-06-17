"""
Shared library for default prediction stubs
"""
from typing import Dict
import logging
import os

logger = logging.getLogger(__name__)

# Safely import ML libraries so the app survives if pip fails
try:
    import joblib
    import numpy as np
    ML_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ML libraries missing, falling back to rules. {e}")
    ML_AVAILABLE = False

class DefaultPredictor:
    """
    Default prediction model (placeholder for ML model)
    
    Internal method used by services for credit risk prediction
    """
    
    def __init__(self, model_path: str = None):
        self.model = None
        self.model_version = "1.0.0-stub"
        
        # Safely load the actual Machine Learning model
        if ML_AVAILABLE and model_path and os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                self.model_version = "2.0.0-ml"
                logger.info(f"Successfully loaded ML model from {model_path}")
            except Exception as e:
                logger.error(f"Failed to load ML model: {e}")
                # Fallback to stubs will happen automatically

    async def predict_default(
        self,
        customer_id: str,
        credit_score: float,
        income: float,
        debt_ratio: float,
        age: int
    ) -> Dict[str, float]:
        """
        Predict probability of default
        
        Returns:
        {
            "default_probability": 0.0-1.0,
            "risk_level": "LOW|MEDIUM|HIGH|VERY_HIGH",
            "model_version": "1.0.0-stub"
        }
        """
        recommended_action = "Maintain current financial behavior."
        
        if self.model:
            # Prepare features as NumPy array for scikit-learn
            features = np.array([[credit_score, income, debt_ratio, age]])
            # Predict probability of default (class 1)
            probability = float(self.model.predict_proba(features)[0][1])
            
            # Feature Importance for Explainable AI (XAI)
            importances = self.model.feature_importances_
            worst_feature_idx = np.argmax(importances)
            
            if probability > 0.4:
                if worst_feature_idx == 0:
                    recommended_action = "Action needed: Build credit history by paying current bills on time."
                elif worst_feature_idx == 2:
                    recommended_action = "CRITICAL: Your debt-to-income ratio is high. Focus on paying down existing debt."
                elif worst_feature_idx == 1:
                    recommended_action = "Consider increasing income sources to lower your risk profile."
                else:
                    recommended_action = "Maintain a healthy mix of credit and low utilization."
            else:
                 recommended_action = "Great standing. You are eligible for premium credit line increases."
        else:
            # Fallback to rule-based logic if no ML model is loaded
            if credit_score < 550:
                probability = 0.8
                recommended_action = "Action needed: Build credit history."
            elif credit_score < 650:
                probability = 0.5
                recommended_action = "Pay down existing debt to improve score."
            elif credit_score < 750:
                probability = 0.2
                recommended_action = "Maintain current positive habits."
            else:
                probability = 0.05
                recommended_action = "Eligible for premium credit products."
            
            # Adjust based on debt ratio
            if debt_ratio > 0.8:
                probability = min(1.0, probability * 1.5)
                recommended_action = "CRITICAL: Immediately reduce outstanding debt."
        
        # Determine risk level
        if probability < 0.1:
            risk_level = "LOW"
        elif probability < 0.3:
            risk_level = "MEDIUM"
        elif probability < 0.6:
            risk_level = "HIGH"
        else:
            risk_level = "VERY_HIGH"
        
        return {
            "default_probability": probability,
            "risk_level": risk_level,
            "model_version": self.model_version,
            "recommended_action": recommended_action,
            "factors": {
                "credit_score": credit_score,
                "debt_ratio": debt_ratio,
                "age": age
            }
        }
