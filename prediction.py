import joblib
import numpy as np
import pandas as pd
import os
from data_preprocessing import clean_text
import nltk
from nltk.corpus import stopwords

# Download NLTK resources if not already downloaded
nltk.download('stopwords', quiet=True)

class CareerPredictor:
    def __init__(self, model_path='models/best_model.pkl', vectorizer_path='models/tfidf_vectorizer.pkl'):
        """Initialize the career predictor with trained model and vectorizer"""
        print("Loading model and vectorizer...")
        self.model = joblib.load(model_path)
        self.vectorizer = joblib.load(vectorizer_path)
        self.stop_words = set(stopwords.words('english'))
        print("Career predictor initialized successfully!")

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

    def get_career_details(self, career_name, dataset_path='preprocessed_career_data.csv'):
        """Get details about a specific career from the dataset"""
        try:
            # Load the preprocessed dataset
            df = pd.read_csv(dataset_path)

            # Print available careers in the dataset for debugging
            available_careers = df['Career'].unique()
            print(f"Available careers in dataset: {available_careers}")

            # Print the requested career name
            print(f"Requested career name: {career_name}")

            # Career name mapping for common variations - updated to match model classes
            career_mapping = {
                "Software Developer": "Software Development and Engineering",
                "Software Engineer": "Software Development and Engineering",
                "Software Development": "Software Development and Engineering",
                "Software Development and Engineering": "Software Development and Engineering",
                "Data Scientist": "Data Science",
                "Data Science": "Data Science",
                "AI Engineer": "Artificial Intelligence",
                "Machine Learning Engineer": "Artificial Intelligence",
                "Artificial Intelligence": "Artificial Intelligence",
                "UX Designer": "User Experience (UX) and User Interface (UI) Design",
                "UI Designer": "User Experience (UX) and User Interface (UI) Design",
                "User Experience": "User Experience (UX) and User Interface (UI) Design",
                "Security Engineer": "Security",
                "Cybersecurity Engineer": "Security",
                "Security": "Security",
                "Web Developer": "Development",
                "Development": "Development"
            }

            # Check if the career name has a mapping
            mapped_career = career_mapping.get(career_name, career_name)
            print(f"Mapped career: {mapped_career}")

            # Filter rows for the specified career
            career_data = df[df['Career'] == mapped_career]

            # If still empty, try a case-insensitive match
            if career_data.empty:
                print(f"No exact match found for {mapped_career}, trying case-insensitive match")
                for career in df['Career'].unique():
                    if career.lower() == mapped_career.lower():
                        career_data = df[df['Career'] == career]
                        mapped_career = career
                        print(f"Found case-insensitive match: {mapped_career}")
                        break

            # If still empty, try a partial match
            if career_data.empty:
                print(f"No case-insensitive match found, trying partial match")
                for career in df['Career'].unique():
                    if mapped_career.lower() in career.lower() or career.lower() in mapped_career.lower():
                        career_data = df[df['Career'] == career]
                        mapped_career = career
                        print(f"Found partial match: {mapped_career}")
                        break

            # If still empty, just use the first career as a fallback
            if career_data.empty:
                print(f"No match found at all, using first career as fallback")
                first_career = df['Career'].iloc[0]
                career_data = df[df['Career'] == first_career]
                mapped_career = first_career
                print(f"Using fallback career: {mapped_career}")

            # Extract unique skills for this career
            all_skills = []
            for skills in career_data['Skill']:
                if isinstance(skills, str):
                    # Split by comma and strip whitespace
                    skill_list = [s.strip() for s in skills.split(',')]
                    all_skills.extend(skill_list)

            # Get unique skills
            unique_skills = list(set(all_skills))

            result = {
                "career": mapped_career,
                "original_query": career_name,
                "skills": unique_skills,
                "count": len(career_data)
            }

            print(f"Returning career details: {result}")
            return result

        except Exception as e:
            error_msg = f"Error getting career details: {str(e)}"
            print(error_msg)
            return {"error": error_msg}

def get_skill_recommendations(user_skills, dataset_path='preprocessed_career_data.csv'):
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
        return {"error": str(e)}

if __name__ == "__main__":
    # Test the predictor
    predictor = CareerPredictor()

    # Example skills
    test_skills = "Machine Learning, Data Analysis, Python Programming, Statistics"

    # Get predictions
    predictions = predictor.predict_career(test_skills)

    print(f"Input skills: {test_skills}")
    print("Predicted careers:")
    for pred in predictions:
        print(f"- {pred['career']} (Confidence: {pred['confidence']:.2f})")

    # Get details for the top predicted career
    top_career = predictions[0]['career']
    details = predictor.get_career_details(top_career)

    print(f"\nDetails for {top_career}:")
    print(f"Number of entries: {details.get('count', 'N/A')}")
    print("Common skills:")
    for skill in details.get('skills', [])[:10]:  # Show only first 10 skills
        print(f"- {skill}")

    # Get skill recommendations
    user_skills = ["Python Programming", "Data Analysis", "Statistics"]
    recommended_skills = get_skill_recommendations(user_skills)

    print("\nRecommended skills to learn:")
    for skill in recommended_skills:
        print(f"- {skill}")
