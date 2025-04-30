import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LanguageService:
    def __init__(self):
        """Initialize the Language Service client"""
        self.endpoint = os.environ.get("LANGUAGE_ENDPOINT")
        self.key = os.environ.get("LANGUAGE_KEY")
        
        if not self.endpoint or not self.key:
            print("Language Service credentials not found in environment variables")
    
    def is_configured(self):
        """Check if Language Service is configured"""
        return self.endpoint is not None and self.key is not None
    
    def analyze_text(self, text):
        """Analyze text using Azure Language Service"""
        if not self.is_configured():
            print("Language Service not configured")
            return {"error": "Language Service not configured"}
        
        try:
            # Construct the request URL for text analytics
            url = f"{self.endpoint}text/analytics/v3.1/entities/recognition/general"
            
            # Prepare the request headers
            headers = {
                "Ocp-Apim-Subscription-Key": self.key,
                "Content-Type": "application/json"
            }
            
            # Prepare the request body
            body = {
                "documents": [
                    {
                        "id": "1",
                        "language": "en",
                        "text": text
                    }
                ]
            }
            
            # Make the request
            response = requests.post(url, headers=headers, json=body)
            
            # Check if the request was successful
            if response.status_code == 200:
                result = response.json()
                
                # Extract skills from entities
                skills = []
                if "documents" in result and len(result["documents"]) > 0:
                    for entity in result["documents"][0]["entities"]:
                        if entity["category"] in ["Skill", "Product", "PersonType", "Organization"]:
                            skills.append(entity["text"])
                
                return {
                    "skills": skills,
                    "raw_result": result
                }
            else:
                print(f"Language Service request failed: {response.status_code} - {response.text}")
                return {"error": f"Request failed with status code {response.status_code}"}
        
        except Exception as e:
            print(f"Error analyzing text: {str(e)}")
            return {"error": str(e)}
    
    def extract_skills(self, text):
        """Extract skills from text"""
        result = self.analyze_text(text)
        
        if "error" in result:
            # Fall back to simple extraction if Language Service fails
            print("Falling back to simple skill extraction")
            words = text.split(',')
            return [word.strip() for word in words if word.strip()]
        
        skills = result.get("skills", [])
        
        # If no skills were found, fall back to simple extraction
        if not skills:
            print("No skills found by Language Service, falling back to simple extraction")
            words = text.split(',')
            return [word.strip() for word in words if word.strip()]
        
        return skills
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of text"""
        if not self.is_configured():
            print("Language Service not configured")
            return {"error": "Language Service not configured"}
        
        try:
            # Construct the request URL for sentiment analysis
            url = f"{self.endpoint}text/analytics/v3.1/sentiment"
            
            # Prepare the request headers
            headers = {
                "Ocp-Apim-Subscription-Key": self.key,
                "Content-Type": "application/json"
            }
            
            # Prepare the request body
            body = {
                "documents": [
                    {
                        "id": "1",
                        "language": "en",
                        "text": text
                    }
                ]
            }
            
            # Make the request
            response = requests.post(url, headers=headers, json=body)
            
            # Check if the request was successful
            if response.status_code == 200:
                result = response.json()
                
                # Extract sentiment
                if "documents" in result and len(result["documents"]) > 0:
                    sentiment = result["documents"][0]["sentiment"]
                    confidence_scores = result["documents"][0]["confidenceScores"]
                    
                    return {
                        "sentiment": sentiment,
                        "confidence_scores": confidence_scores,
                        "raw_result": result
                    }
                else:
                    return {"error": "No sentiment results found"}
            else:
                print(f"Language Service request failed: {response.status_code} - {response.text}")
                return {"error": f"Request failed with status code {response.status_code}"}
        
        except Exception as e:
            print(f"Error analyzing sentiment: {str(e)}")
            return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    # Set environment variables for testing
    os.environ["LANGUAGE_ENDPOINT"] = "https://your-language-service.cognitiveservices.azure.com/"
    os.environ["LANGUAGE_KEY"] = "your-language-service-key"
    
    # Initialize the Language Service
    language_service = LanguageService()
    
    if language_service.is_configured():
        # Example: Extract skills from text
        text = "I have experience with Python, Machine Learning, and Data Analysis. I've worked on several projects using TensorFlow and PyTorch."
        
        skills = language_service.extract_skills(text)
        print(f"Extracted skills: {skills}")
        
        # Example: Analyze sentiment
        feedback = "I really enjoyed using this career guidance chatbot. It provided helpful recommendations."
        
        sentiment = language_service.analyze_sentiment(feedback)
        print(f"Sentiment analysis: {json.dumps(sentiment, indent=2)}")
    else:
        print("Language Service not configured. Check your environment variables.")
