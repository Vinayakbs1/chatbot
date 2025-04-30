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
    from shared.prediction import get_career_details
    logging.info("Successfully imported get_career_details")
except Exception as e:
    logging.error(f"Error importing get_career_details: {str(e)}")
    logging.error(traceback.format_exc())

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Get career from query parameters
        career = req.params.get('career')
        logging.info(f"Career from query parameters: {career}")

        if not career:
            # If not in query parameters, check request body
            try:
                req_body = req.get_json()
                career = req_body.get('career')
                logging.info(f"Career from request body: {career}")
            except ValueError:
                logging.warning("Request body is not valid JSON")
                pass

        if not career:
            logging.warning("No career specified")
            return func.HttpResponse(
                json.dumps({"error": "No career specified"}),
                status_code=400,
                mimetype="application/json"
            )

        # Get career details
        logging.info(f"Getting details for career: {career}")
        details = get_career_details(career)
        logging.info(f"Career details: {details}")

        return func.HttpResponse(
            json.dumps(details),
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
