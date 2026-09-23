import pandas as pd
import numpy as np
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import cross_val_score

from utils.preprocess import preprocess_pipeline

def train_and_evaluate():
    print("Loading data and preprocessing...")
    filepath = 'dataset/Crop_recommendation.csv'
    X_train, X_test, y_train, y_test, scaler, le = preprocess_pipeline(filepath)
    
    models = {
        'Logistic Regression': LogisticRegression(max_iter=2000, random_state=42),
        'KNN': KNeighborsClassifier(),
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Naive Bayes': GaussianNB(),
        'SVM': SVC(probability=True, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(random_state=42)
    }
    
    results = {}
    best_model_name = None
    best_accuracy = 0
    best_model = None
    
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        # Cross validation across full dataset features
        cv_scores = cross_val_score(model, np.vstack((X_train, X_test)), np.concatenate((y_train, y_test)), cv=5)
        
        results[name] = {
            'Accuracy': acc,
            'Precision': prec,
            'Recall': rec,
            'F1 Score': f1,
            'CV Mean Accuracy': cv_scores.mean()
        }
        
        if acc > best_accuracy:
            best_accuracy = acc
            best_model_name = name
            best_model = model
            
    print("\n--- Model Comparison ---")
    results_df = pd.DataFrame(results).T
    print(results_df.round(4))
    
    print(f"\nBest Model: {best_model_name} with Accuracy: {best_accuracy:.4f}")
    
    # Save the best model, scaler, and label encoder (Module 5)
    print("Saving Best Model, Scaler, and Label Encoder...")
    with open('model/crop_model.pkl', 'wb') as f:
        pickle.dump(best_model, f)
    with open('model/scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    with open('model/encoder.pkl', 'wb') as f:
        pickle.dump(le, f)
        
    print("Model saved successfully in 'model/' directory.")

if __name__ == '__main__':
    train_and_evaluate()
