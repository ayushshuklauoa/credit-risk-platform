import pytest
import os
import sys

# Add shared-lib to path for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../shared-lib')))
from prediction import DefaultPredictor

@pytest.mark.asyncio
async def test_ideal_financial_profile():
    """Test that a great financial profile returns LOW risk"""
    # Initialize the predictor (it will safely fall back to rules if ML model isn't built locally)
    predictor = DefaultPredictor(model_path=None)
    
    result = await predictor.predict_default(
        customer_id="Tuhin_101",
        credit_score=800.0,
        income=120000.0,
        debt_ratio=0.1,  # 10% debt ratio
        age=30
    )
    
    assert result["risk_level"] == "LOW"
    assert result["default_probability"] < 0.1
    assert "recommended_action" in result

@pytest.mark.asyncio
async def test_critical_debt_profile():
    """Test that a terrible financial profile returns VERY_HIGH risk"""
    predictor = DefaultPredictor(model_path=None)
    
    result = await predictor.predict_default(
        customer_id="test_456",
        credit_score=450.0,
        income=50000.0,
        debt_ratio=0.85, # 85% debt ratio!
        age=25
    )
    
    assert result["risk_level"] == "VERY_HIGH"
    assert "debt" in result["recommended_action"].lower()