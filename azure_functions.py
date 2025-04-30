import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AzureFunctionsClient:
    def __init__(self):
        """Initialize the Azure Functions client"""
        self.base_url = os.environ.get("AZURE_FUNCTION_URL")

        if not self.base_url:
            print("Azure Functions URL not found in environment variables")

    def is_configured(self):
        """Check if Azure Functions is configured"""
        return self.base_url is not None

    def predict_career(self, skills):
        """Call the simple_predict Azure Function"""
        if not self.is_configured():
            print("Azure Functions not configured")
            return {"error": "Azure Functions not configured"}

        try:
            # Construct the request URL
            url = f"{self.base_url}/api/simple_predict"

            # Prepare the request body
            body = {
                "skills": skills if isinstance(skills, str) else ", ".join(skills)
            }

            # Make the request
            response = requests.post(url, json=body)

            # Check if the request was successful
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Azure Function request failed: {response.status_code} - {response.text}")
                return {"error": f"Request failed with status code {response.status_code}"}

        except Exception as e:
            print(f"Error calling simple_predict function: {str(e)}")
            return {"error": str(e)}

    def get_career_details(self, career):
        """Call the get_career_details Azure Function"""
        if not self.is_configured():
            print("Azure Functions not configured")
            return {"error": "Azure Functions not configured"}

        try:
            # Construct the request URL
            url = f"{self.base_url}/api/get_career_details"

            # Prepare the query parameters
            params = {
                "career": career
            }

            # Make the request
            response = requests.get(url, params=params)

            # Check if the request was successful
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Azure Function request failed: {response.status_code} - {response.text}")
                return {"error": f"Request failed with status code {response.status_code}"}

        except Exception as e:
            print(f"Error calling get_career_details function: {str(e)}")
            return {"error": str(e)}

    def recommend_skills(self, current_skills, target_career=None):
        """Call the recommend_skills Azure Function"""
        if not self.is_configured():
            print("Azure Functions not configured")
            return {"error": "Azure Functions not configured"}

        try:
            # Construct the request URL
            url = f"{self.base_url}/api/recommend_skills"

            # Prepare the request body
            body = {
                "skills": current_skills if isinstance(current_skills, list) else current_skills.split(",")
            }

            if target_career:
                body["targetCareer"] = target_career

            # Make the request
            response = requests.post(url, json=body)

            # Check if the request was successful
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Azure Function request failed: {response.status_code} - {response.text}")
                return {"error": f"Request failed with status code {response.status_code}"}

        except Exception as e:
            print(f"Error calling recommend_skills function: {str(e)}")
            return {"error": str(e)}

# Example usage
if __name__ == "__main__":
    # Set environment variables for testing
    os.environ["AZURE_FUNCTION_URL"] = "https://your-function-app.azurewebsites.net"

    # Initialize the Azure Functions client
    functions_client = AzureFunctionsClient()

    if functions_client.is_configured():
        # Example: Predict career
        skills = ["Python", "Machine Learning", "Data Analysis"]

        prediction = functions_client.predict_career(skills)
        print(f"Career prediction: {json.dumps(prediction, indent=2)}")

        # Example: Get career details
        career = "Data Scientist"

        details = functions_client.get_career_details(career)
        print(f"Career details: {json.dumps(details, indent=2)}")

        # Example: Recommend skills
        recommended_skills = functions_client.recommend_skills(skills, "Data Scientist")
        print(f"Recommended skills: {json.dumps(recommended_skills, indent=2)}")
    else:
        print("Azure Functions not configured. Check your environment variables.")
