import logging
import azure.functions as func
import json
import os
import sys
import traceback
from datetime import datetime
import uuid

# Add the parent directory to sys.path to import from parent modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Print current directory and sys.path for debugging
logging.info(f"Current directory: {os.getcwd()}")
logging.info(f"sys.path: {sys.path}")

# Import from shared module
try:
    from shared.prediction import predictor
    logging.info("Successfully imported predictor")
except Exception as e:
    logging.error(f"Error importing predictor: {str(e)}")
    logging.error(traceback.format_exc())
    predictor = None

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Check if predictor is initialized
        if predictor is None:
            return func.HttpResponse(
                json.dumps({"error": "Predictor not initialized"}),
                status_code=500,
                mimetype="application/json"
            )

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

        # Get career predictions
        logging.info(f"Predicting careers for skills: {skills}")
        try:
            predictions = predictor.predict_career(skills)
            logging.info(f"Predictions: {predictions}")
        except Exception as pred_error:
            error_message = str(pred_error)
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
        top_career = predictions[0]['career'] if predictions and len(predictions) > 0 else None
        logging.info(f"Top career: {top_career}")

        # Get career details
        if top_career:
            logging.info(f"Getting details for career: {top_career}")
            try:
                details = predictor.get_career_details(top_career)
                logging.info(f"Career details: {details}")
            except Exception as details_error:
                logging.error(f"Error getting career details: {str(details_error)}")
                details = {"career": top_career, "error": str(details_error)}
        else:
            details = {"error": "No career predicted"}

        # Create response
        response = {
            "predictions": predictions,
            "top_career_details": details,
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
