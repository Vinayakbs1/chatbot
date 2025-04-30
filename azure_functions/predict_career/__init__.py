import logging
import azure.functions as func
import json
import os
import sys
import joblib
import numpy as np
from datetime import datetime
import uuid
import traceback

# Add the parent directory to sys.path to import from parent modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Print current directory and sys.path for debugging
logging.info(f"Current directory: {os.getcwd()}")
logging.info(f"sys.path: {sys.path}")

# Import from parent modules
try:
    from shared.prediction import preprocess_skills, predict_career
    logging.info("Successfully imported prediction functions")
except Exception as e:
    logging.error(f"Error importing prediction functions: {str(e)}")
    logging.error(traceback.format_exc())

try:
    from shared.cosmos_db import CosmosDBManager
    logging.info("Successfully imported CosmosDBManager")
except Exception as e:
    logging.error(f"Error importing CosmosDBManager: {str(e)}")
    logging.error(traceback.format_exc())

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Get request body
        try:
            req_body = req.get_json()
            skills = req_body.get('skills', '')
            user_id = req_body.get('userId', str(uuid.uuid4()))
            logging.info(f"Request body: skills={skills}, userId={user_id}")
        except ValueError:
            logging.warning("Request body is not valid JSON")
            skills = ''
            user_id = str(uuid.uuid4())

        if not skills:
            logging.warning("No skills provided")
            return func.HttpResponse(
                json.dumps({"error": "No skills provided"}),
                status_code=400,
                mimetype="application/json"
            )

        # Preprocess skills
        logging.info(f"Preprocessing skills: {skills}")
        processed_skills = preprocess_skills(skills)
        logging.info(f"Processed skills: {processed_skills}")

        # Get career predictions
        logging.info("Getting career predictions")
        predictions = predict_career(processed_skills)
        logging.info(f"Predictions: {predictions}")

        # Check if predictions contains an error
        if predictions and 'error' in predictions[0]:
            error_message = predictions[0]['error']
            logging.error(f"Error in prediction: {error_message}")
            return func.HttpResponse(
                json.dumps({
                    "error": error_message,
                    "details": "Error occurred during career prediction"
                }),
                status_code=500,
                mimetype="application/json"
            )

        # Get top career
        top_career = predictions[0]['career'] if predictions and 'career' in predictions[0] else None
        logging.info(f"Top career: {top_career}")

        # Save user preferences to Cosmos DB
        try:
            cosmos_manager = CosmosDBManager()
            if cosmos_manager.is_connected():
                logging.info("Connected to Cosmos DB")
                user_skills = [s.strip() for s in skills.split(',')]
                cosmos_manager.save_user_preferences(user_id, user_skills, top_career)
                logging.info("Saved user preferences to Cosmos DB")
            else:
                logging.warning("Not connected to Cosmos DB")
        except Exception as cosmos_error:
            logging.error(f"Error saving to Cosmos DB: {str(cosmos_error)}")
            logging.error(traceback.format_exc())

        # Create response
        response = {
            "predictions": predictions,
            "timestamp": datetime.utcnow().isoformat(),
            "userId": user_id
        }

        logging.info(f"Returning response: {response}")
        return func.HttpResponse(
            json.dumps(response),
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
