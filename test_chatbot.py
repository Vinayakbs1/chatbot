import requests
import json
from prediction import CareerPredictor
import pandas as pd

def test_local_prediction():
    """Test the local prediction functionality"""
    print("\n=== Testing Local Prediction ===")
    
    # Initialize the predictor
    predictor = CareerPredictor()
    
    # Test different skill sets
    test_cases = [
        "Python, Machine Learning, Data Analysis, Statistics",
        "Web Development, JavaScript, HTML, CSS",
        "UX Design, User Research, Wireframing, Prototyping",
        "Network Security, Penetration Testing, Cryptography",
        "Cloud Computing, AWS, Azure, DevOps"
    ]
    
    for skills in test_cases:
        print(f"\nTesting skills: {skills}")
        
        # Get predictions
        predictions = predictor.predict_career(skills)
        
        # Print predictions
        print("Predicted careers:")
        for pred in predictions:
            print(f"- {pred['career']} (Confidence: {pred['confidence']:.2f})")
        
        # Get details for the top predicted career
        if predictions:
            top_career = predictions[0]['career']
            details = predictor.get_career_details(top_career)
            
            if "error" in details:
                print(f"Error getting career details: {details['error']}")
            else:
                print(f"\nDetails for {top_career}:")
                print(f"Number of entries: {details.get('count', 'N/A')}")
                print("Common skills (first 5):")
                for skill in details.get('skills', [])[:5]:
                    print(f"- {skill}")

def test_api_endpoint():
    """Test the API endpoint if the Flask app is running"""
    print("\n=== Testing API Endpoint ===")
    
    try:
        # Test the predict endpoint
        url = "http://localhost:5000/api/predict"
        payload = {
            "skills": "Python, Machine Learning, Data Analysis, Statistics"
        }
        
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print("API Response:")
            print(json.dumps(result, indent=2))
        else:
            print(f"API request failed with status code: {response.status_code}")
            print(response.text)
    
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to API: {e}")
        print("Make sure the Flask app is running (python app.py)")

def check_dataset():
    """Check the dataset for available careers"""
    print("\n=== Checking Dataset ===")
    
    try:
        # Load the preprocessed dataset
        df = pd.read_csv('preprocessed_career_data.csv')
        
        # Get unique careers
        careers = df['Career'].unique()
        
        print(f"Found {len(careers)} unique careers in the dataset:")
        for career in careers:
            count = len(df[df['Career'] == career])
            print(f"- {career} ({count} entries)")
    
    except Exception as e:
        print(f"Error checking dataset: {e}")

if __name__ == "__main__":
    print("=== Career Chatbot Testing ===")
    
    # Check the dataset
    check_dataset()
    
    # Test local prediction
    test_local_prediction()
    
    # Test API endpoint (if Flask app is running)
    test_api_endpoint()
