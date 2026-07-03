import pickle
import numpy as np
import os

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
    input_data must be a list of 7 elements: [N, P, K, temp, humidity, ph, rainfall]
    """
    # Convert list to a 2D numpy array with 1 row and 7 columns
    input_array = np.array(input_data).reshape(1, -1)
    scaled_array = scaler.transform(input_array)
    return scaled_array

def predict_crop(scaled_input, model, encoder):
    """Predicts the crop and decodes the numerical prediction back to a string."""
    prediction = model.predict(scaled_input)
    # The encoder outputs a list, so we grab the first (and only) element
    crop_name = encoder.inverse_transform(prediction)[0]
    return crop_name

def return_prediction(N, P, K, temperature, humidity, ph, rainfall):
    """
    The main wrapper function used directly by the Flask backend.
    Takes 7 raw floats from the HTML form and outputs the final crop prediction.
    """
    try:
        model, scaler, encoder = load_models()
        input_data = [N, P, K, temperature, humidity, ph, rainfall]
        
        scaled_input = preprocess_input(input_data, scaler)
        crop = predict_crop(scaled_input, model, encoder)
        
        return {"success": True, "prediction": crop}
    except Exception as e:
        return {"success": False, "error": str(e)}
