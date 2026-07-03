import pytest
from utils.predict import return_prediction, load_models

def test_load_models():
    """Test if the pickle files load successfully and return expected objects."""
    model, scaler, encoder = load_models()
    assert model is not None
    assert scaler is not None
    assert encoder is not None
    assert hasattr(model, 'predict')
    assert hasattr(scaler, 'transform')

def test_valid_prediction():
    """Test the prediction pipeline with valid numerical inputs."""
    # Sample data that typically predicts 'rice' or a similar crop
    res = return_prediction(90, 42, 43, 20.8, 82.0, 6.5, 202.9)
    assert res['success'] is True
    assert 'prediction' in res
    assert isinstance(res['prediction'], str)
    assert len(res['prediction']) > 0

def test_invalid_prediction_types():
    """Test the prediction pipeline with invalid data types (strings instead of floats)."""
    res = return_prediction("abc", 42, 43, 20.8, 82.0, 6.5, 202.9)
    assert res['success'] is False
    assert 'error' in res
