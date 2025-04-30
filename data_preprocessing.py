import pandas as pd
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
import nltk
from nltk.corpus import stopwords
import joblib
import os

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

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

def preprocess_data(file_path):
    """Preprocess the career dataset"""
    print(f"Loading data from {file_path}...")

    # Load the dataset
    df = pd.read_csv(file_path)

    # Check for missing values
    print(f"Missing values in dataset: {df.isnull().sum()}")

    # Drop rows with missing values
    df = df.dropna()

    # Clean the skill text
    df['Skill'] = df['Skill'].apply(clean_text)

    # Create a new column with simple tokenization (split by spaces)
    df['Tokenized_Skills'] = df['Skill'].apply(lambda x: ' '.join(x.split()))

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    df['Filtered_Skills'] = df['Tokenized_Skills'].apply(
        lambda x: ' '.join([word for word in x.split() if word.lower() not in stop_words])
    )

    print(f"Preprocessed data shape: {df.shape}")

    # Save the preprocessed data
    output_path = os.path.join(os.path.dirname(file_path), 'preprocessed_career_data.csv')
    df.to_csv(output_path, index=False)
    print(f"Preprocessed data saved to {output_path}")

    return df

def create_feature_vectors(df):
    """Create feature vectors from skills using TF-IDF"""
    print("Creating feature vectors...")

    # Initialize TF-IDF Vectorizer
    tfidf_vectorizer = TfidfVectorizer(max_features=1000)

    # Fit and transform the skills data
    tfidf_matrix = tfidf_vectorizer.fit_transform(df['Filtered_Skills'])

    # Convert to DataFrame for better visualization
    feature_names = tfidf_vectorizer.get_feature_names_out()
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=feature_names)

    print(f"Feature vector shape: {tfidf_df.shape}")

    # Save the vectorizer for later use
    joblib.dump(tfidf_vectorizer, 'models/tfidf_vectorizer.pkl')

    return tfidf_matrix, tfidf_vectorizer

def split_data(X, y):
    """Split data into training and testing sets"""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"Training set size: {X_train.shape}")
    print(f"Testing set size: {X_test.shape}")

    return X_train, X_test, y_train, y_test

if __name__ == "__main__":
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)

    # Preprocess the data
    file_path = 'Career_Dataset.csv'
    df = preprocess_data(file_path)

    # Create feature vectors
    X, vectorizer = create_feature_vectors(df)
    y = df['Career']

    # Split the data
    X_train, X_test, y_train, y_test = split_data(X, y)

    # Save the processed data for model training
    joblib.dump((X_train, X_test, y_train, y_test), 'models/processed_data.pkl')

    print("Data preprocessing completed successfully!")
