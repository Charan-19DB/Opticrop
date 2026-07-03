import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings
warnings.filterwarnings('ignore')

def load_data(filepath):
    """Loads the dataset from the specified path."""
    return pd.read_csv(filepath)

def clean_data(df):
    """Handles missing values and duplicates."""
    if df.duplicated().sum() > 0:
        df = df.drop_duplicates()
    
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna(df[col].mode()[0])
            else:
                df[col] = df[col].fillna(df[col].median())
    return df

def handle_outliers(df, features):
    """Caps outliers using the IQR method."""
    df_out = df.copy()
    for col in features:
        Q1 = df_out[col].quantile(0.25)
        Q3 = df_out[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Capping outliers
        df_out[col] = np.where(df_out[col] < lower_bound, lower_bound, df_out[col])
        df_out[col] = np.where(df_out[col] > upper_bound, upper_bound, df_out[col])
    return df_out

def preprocess_pipeline(filepath):
    """
    Complete pipeline for data preprocessing.
    Returns: X_train, X_test, y_train, y_test, scaler, label_encoder
    """
    df = load_data(filepath)
    df = clean_data(df)
    
    features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    target = 'label'
    
    df = handle_outliers(df, features)
    
    X = df[features]
    y = df[target]
    
    # Encode target labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Train-test split (stratify ensures equal distribution of crops in train/test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, le
