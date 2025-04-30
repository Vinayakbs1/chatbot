import os
import joblib
import re
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
import nltk
import logging

# Download NLTK resources
nltk.download('stopwords', quiet=True)

# Get paths from environment variables or use default paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_dir = os.environ.get('MODEL_PATH', 'models')
data_dir = os.environ.get('DATA_PATH', 'data')

# Path to models
MODEL_PATH = os.path.join(base_dir, model_dir)
VECTORIZER_PATH = os.path.join(MODEL_PATH, 'tfidf_vectorizer.pkl')
MODEL_FILE_PATH = os.path.join(MODEL_PATH, 'best_model.pkl')
DATASET_PATH = os.path.join(base_dir, data_dir, 'preprocessed_career_data.csv')

# Print paths for debugging
print(f"MODEL_PATH: {MODEL_PATH}")
print(f"VECTORIZER_PATH: {VECTORIZER_PATH}")
print(f"MODEL_FILE_PATH: {MODEL_FILE_PATH}")
print(f"DATASET_PATH: {DATASET_PATH}")

# CareerPredictor class
class CareerPredictor:
    def __init__(self, model_path=MODEL_FILE_PATH, vectorizer_path=VECTORIZER_PATH):
        """Initialize the career predictor with trained model and vectorizer"""
        print("Loading model and vectorizer...")
        try:
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vectorizer_path)
            self.stop_words = set(stopwords.words('english'))
            print("Career predictor initialized successfully!")
        except Exception as e:
            error_msg = f"Error loading model or vectorizer: {str(e)}"
            print(error_msg)
            logging.error(error_msg)
            raise e

    def preprocess_skills(self, skills_text):
        """Preprocess the input skills text"""
        # Clean the text
        cleaned_text = clean_text(skills_text)

        # Simple tokenization (split by spaces)
        tokens = cleaned_text.split()

        # Remove stopwords
        filtered_tokens = [word for word in tokens if word.lower() not in self.stop_words]

        # Join tokens back into a string
        processed_text = ' '.join(filtered_tokens)

        return processed_text

    def predict_career(self, skills_text, top_n=3):
        """Predict top N career paths based on skills"""
        # Preprocess the input skills
        processed_skills = self.preprocess_skills(skills_text)

        # Transform the text using the vectorizer
        skills_vector = self.vectorizer.transform([processed_skills])

        # Get prediction probabilities
        probabilities = self.model.predict_proba(skills_vector)[0]

        # Get the top N predictions
        top_indices = np.argsort(probabilities)[::-1][:top_n]
        top_careers = [self.model.classes_[i] for i in top_indices]
        top_probs = [probabilities[i] for i in top_indices]

        # Create a list of dictionaries with career and confidence
        predictions = [
            {'career': career, 'confidence': float(prob)}
            for career, prob in zip(top_careers, top_probs)
        ]

        return predictions

    def get_career_details(self, career_name, dataset_path=DATASET_PATH):
        """Get details about a specific career from the dataset"""
        try:
            # Load the preprocessed dataset
            df = pd.read_csv(dataset_path)

            # Filter rows for the specified career
            career_data = df[df['Career'] == career_name]

            if career_data.empty:
                return {"error": f"No information found for career: {career_name}"}

            # Extract unique skills for this career
            all_skills = []
            for skills in career_data['Skill']:
                if isinstance(skills, str):
                    # Split by comma and strip whitespace
                    skill_list = [s.strip() for s in skills.split(',')]
                    all_skills.extend(skill_list)

            # Get unique skills
            unique_skills = list(set(all_skills))

            return {
                "career": career_name,
                "skills": unique_skills,
                "count": len(career_data)
            }

        except Exception as e:
            error_msg = f"Error getting career details: {str(e)}"
            print(error_msg)
            return {"error": error_msg}

# Helper functions
def clean_text(text):
    """Clean and normalize text data"""
    if isinstance(text, str):
        # Remove special characters and extra spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        # Convert to lowercase
        text = text.lower()
        return text
    return ""

# Create a global instance of the predictor
try:
    predictor = CareerPredictor()
except Exception as e:
    logging.error(f"Failed to initialize predictor: {str(e)}")
    predictor = None

# Functions to be called from Azure Functions
def preprocess_skills(skills_text):
    """Preprocess the input skills text"""
    if predictor is None:
        return {"error": "Predictor not initialized"}
    return predictor.preprocess_skills(skills_text)

def predict_career(skills_text, top_n=3):
    """Predict top N career paths based on skills"""
    if predictor is None:
        return [{"error": "Predictor not initialized"}]
    try:
        return predictor.predict_career(skills_text, top_n)
    except Exception as e:
        print(f"Error predicting career: {str(e)}")
        return [{"error": str(e)}]

def get_career_details(career_name):
    """Get details about a specific career from the dataset"""
    if predictor is None:
        return {"error": "Predictor not initialized"}
    return predictor.get_career_details(career_name)

def get_skill_recommendations(user_skills, dataset_path=DATASET_PATH):
    """Get skill recommendations based on user's current skills"""
    try:
        # Load the preprocessed dataset
        df = pd.read_csv(dataset_path)

        # Initialize a list to store recommended skills
        recommended_skills = []

        # Convert user skills to lowercase for case-insensitive matching
        user_skills_lower = [skill.lower() for skill in user_skills]

        # Extract all skills from the dataset
        all_skills = []
        for skills_str in df['Skill']:
            if isinstance(skills_str, str):
                # Split by comma and strip whitespace
                skills = [s.strip() for s in skills_str.split(',')]
                all_skills.extend(skills)

        # Count skill frequencies
        skill_counts = {}
        for skill in all_skills:
            skill_lower = skill.lower()
            if skill_lower not in user_skills_lower:
                if skill_lower in skill_counts:
                    skill_counts[skill_lower] += 1
                else:
                    skill_counts[skill_lower] = 1

        # Sort skills by frequency
        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)

        # Get the top 10 most frequent skills
        top_skills = [skill for skill, count in sorted_skills[:10]]

        return top_skills

    except Exception as e:
        print(f"Error getting skill recommendations: {str(e)}")
        return {"error": str(e)}
