import os
from language_service import LanguageService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    """Test Azure Language Service"""
    print("=== Testing Azure Language Service ===\n")
    
    # Initialize Language Service
    language_service = LanguageService()
    
    # Check if Language Service is configured
    if not language_service.is_configured():
        print("Language Service is not configured.")
        print("Please check your .env file and make sure LANGUAGE_ENDPOINT and LANGUAGE_KEY are set.")
        return
    
    print("Language Service is configured.")
    print(f"Endpoint: {language_service.endpoint}")
    
    # Test text analysis
    print("\nTesting text analysis...")
    
    # Example text with skills
    text = "I have experience with Python, Machine Learning, and Data Analysis. I've worked on several projects using TensorFlow and PyTorch."
    
    # Analyze text
    result = language_service.analyze_text(text)
    
    if "error" in result:
        print(f"Error analyzing text: {result['error']}")
    else:
        print("Text analysis successful!")
        print(f"Extracted skills: {result['skills']}")
    
    # Test skill extraction
    print("\nTesting skill extraction...")
    
    # Extract skills
    skills = language_service.extract_skills(text)
    
    print(f"Extracted skills: {skills}")
    
    # Test sentiment analysis
    print("\nTesting sentiment analysis...")
    
    # Example feedback
    feedback = "I really enjoyed using this career guidance chatbot. It provided helpful recommendations."
    
    # Analyze sentiment
    sentiment_result = language_service.analyze_sentiment(feedback)
    
    if "error" in sentiment_result:
        print(f"Error analyzing sentiment: {sentiment_result['error']}")
    else:
        print("Sentiment analysis successful!")
        print(f"Sentiment: {sentiment_result['sentiment']}")
        print(f"Confidence scores: {sentiment_result['confidence_scores']}")
    
    print("\n=== Language Service testing completed! ===")

if __name__ == "__main__":
    main()
