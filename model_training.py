import numpy as np
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

def train_models(X_train, y_train):
    """Train multiple classification models"""
    print("Training models...")
    
    # Initialize models
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'SVM': SVC(kernel='linear', probability=True, random_state=42)
    }
    
    # Train each model
    trained_models = {}
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train, y_train)
        trained_models[name] = model
    
    return trained_models

def evaluate_models(models, X_test, y_test):
    """Evaluate trained models and select the best one"""
    print("Evaluating models...")
    
    results = {}
    best_accuracy = 0
    best_model_name = None
    
    for name, model in models.items():
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate accuracy
        accuracy = accuracy_score(y_test, y_pred)
        results[name] = {
            'accuracy': accuracy,
            'classification_report': classification_report(y_test, y_pred, output_dict=True)
        }
        
        print(f"{name} Accuracy: {accuracy:.4f}")
        
        # Update best model
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_model_name = name
    
    print(f"Best model: {best_model_name} with accuracy: {best_accuracy:.4f}")
    
    # Plot confusion matrix for the best model
    plot_confusion_matrix(models[best_model_name], X_test, y_test, best_model_name)
    
    return results, models[best_model_name]

def plot_confusion_matrix(model, X_test, y_test, model_name):
    """Plot confusion matrix for model evaluation"""
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=model.classes_, 
                yticklabels=model.classes_)
    plt.title(f'Confusion Matrix - {model_name}')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(f'models/confusion_matrix_{model_name.replace(" ", "_").lower()}.png')
    plt.close()

def save_model(model, vectorizer, model_name='best_model'):
    """Save the trained model and vectorizer"""
    print(f"Saving {model_name}...")
    
    # Save the model
    joblib.dump(model, f'models/{model_name}.pkl')
    
    # Create a model info file
    with open(f'models/{model_name}_info.txt', 'w') as f:
        f.write(f"Model: {type(model).__name__}\n")
        f.write(f"Number of classes: {len(model.classes_)}\n")
        f.write(f"Classes: {', '.join(model.classes_)}\n")
    
    print(f"Model saved as models/{model_name}.pkl")

if __name__ == "__main__":
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Load processed data
    print("Loading processed data...")
    X_train, X_test, y_train, y_test = joblib.load('models/processed_data.pkl')
    
    # Load vectorizer
    vectorizer = joblib.load('models/tfidf_vectorizer.pkl')
    
    # Train models
    trained_models = train_models(X_train, y_train)
    
    # Evaluate models
    results, best_model = evaluate_models(trained_models, X_test, y_test)
    
    # Save the best model
    save_model(best_model, vectorizer, 'best_model')
    
    # Save all models for comparison
    for name, model in trained_models.items():
        save_model(model, vectorizer, name.lower().replace(' ', '_'))
    
    print("Model training completed successfully!")
