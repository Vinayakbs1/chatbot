import logging
import azure.functions as func
import json
import os
import sys
import traceback

# Add the parent directory to sys.path to import from parent modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Print current directory and sys.path for debugging
logging.info(f"Current directory: {os.getcwd()}")
logging.info(f"sys.path: {sys.path}")

# Import from parent modules
try:
    from shared.prediction import get_skill_recommendations
    logging.info("Successfully imported get_skill_recommendations")
except Exception as e:
    logging.error(f"Error importing get_skill_recommendations: {str(e)}")
    logging.error(traceback.format_exc())

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Get request body
        try:
            req_body = req.get_json()
            user_skills = req_body.get('skills', [])
            logging.info(f"Request body: skills={user_skills}")
        except ValueError:
            logging.warning("Request body is not valid JSON")
            user_skills = []

        if not user_skills:
            logging.warning("No skills provided")
            return func.HttpResponse(
                json.dumps({"error": "No skills provided"}),
                status_code=400,
                mimetype="application/json"
            )

        # Get skill recommendations
        logging.info(f"Getting skill recommendations for: {user_skills}")
        recommended_skills = get_skill_recommendations(user_skills)
        logging.info(f"Recommended skills: {recommended_skills}")

        return func.HttpResponse(
            json.dumps({"recommended_skills": recommended_skills}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        error_message = str(e)
        stack_trace = traceback.format_exc()
        logging.error(f"Error: {error_message}")
        logging.error(f"Stack trace: {stack_trace}")
        return func.HttpResponse(
            json.dumps({
                "error": error_message,
                "stack_trace": stack_trace
            }),
            status_code=500,
            mimetype="application/json"
        )
