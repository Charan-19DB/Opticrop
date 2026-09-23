import pickle
import numpy as np
import pandas as pd
import os
from utils.agronomy_data import get_crop_info

FEATURE_NAMES = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']

def load_models(model_path='model/crop_model.pkl', 
                scaler_path='model/scaler.pkl', 
                encoder_path='model/encoder.pkl'):
    """Loads the trained ML model, scaler, and label encoder from disk."""
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)
    with open(encoder_path, 'rb') as f:
        encoder = pickle.load(f)
    return model, scaler, encoder

def preprocess_input(input_data, scaler):
    """
    Scales the user input using the fitted scaler.
    Uses DataFrame with feature names to prevent scikit-learn warnings.
    """
    df = pd.DataFrame([input_data], columns=FEATURE_NAMES)
    scaled_array = scaler.transform(df)
    return scaled_array

def predict_crop(scaled_input, model, encoder):
    """Predicts the crop and decodes the numerical prediction back to a string."""
    prediction = model.predict(scaled_input)
    crop_name = encoder.inverse_transform(prediction)[0]
    return crop_name

def predict_top_crops(scaled_input, model, encoder, top_n=3):
    """
    Calculates class probabilities and returns top-N recommendations with confidence scores.
    """
    probas = model.predict_proba(scaled_input)[0]
    top_indices = probas.argsort()[-top_n:][::-1]
    
    results = []
    for idx in top_indices:
        crop_code = encoder.inverse_transform([idx])[0]
        conf_pct = float(round(probas[idx] * 100, 1))
        info = get_crop_info(crop_code)
        results.append({
            'crop': crop_code,
            'confidence': conf_pct,
            'display_name': info['display_name'],
            'category': info['category'],
            'season': info['season'],
            'icon': info['icon'],
            'accent_color': info['accent_color']
        })
    return results

def return_prediction(N, P, K, temperature, humidity, ph, rainfall):
    """
    The main prediction wrapper function used by Flask.
    Returns primary prediction, top-3 candidates, confidence %, and agronomic dossiers.
    """
    try:
        model, scaler, encoder = load_models()
        input_data = [float(N), float(P), float(K), float(temperature), 
                      float(humidity), float(ph), float(rainfall)]
        
        scaled_input = preprocess_input(input_data, scaler)
        top_candidates = predict_top_crops(scaled_input, model, encoder, top_n=3)
        
        primary_crop = top_candidates[0]['crop']
        confidence = top_candidates[0]['confidence']
        agronomy_dossier = get_crop_info(primary_crop)
        
        metrics = {
            'N': float(N), 'P': float(P), 'K': float(K),
            'temperature': float(temperature), 'humidity': float(humidity),
            'ph': float(ph), 'rainfall': float(rainfall)
        }
        
        return {
            "success": True, 
            "prediction": primary_crop,
            "confidence": confidence,
            "top_candidates": top_candidates,
            "agronomy": agronomy_dossier,
            "metrics": metrics
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
