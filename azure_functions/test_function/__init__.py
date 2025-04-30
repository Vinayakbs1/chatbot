import logging
import azure.functions as func
import json
import os
import sys
import traceback

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Get environment variables
        env_vars = {key: value for key, value in os.environ.items()}
        
        # Get current directory
        current_dir = os.getcwd()
        
        # List directories
        try:
            root_files = os.listdir(current_dir)
        except Exception as e:
            root_files = f"Error listing root directory: {str(e)}"
        
        # Try to list models directory
        try:
            models_dir = os.path.join(current_dir, 'models')
            if os.path.exists(models_dir):
                model_files = os.listdir(models_dir)
            else:
                model_files = "Models directory does not exist"
        except Exception as e:
            model_files = f"Error listing models directory: {str(e)}"
        
        # Try to list data directory
        try:
            data_dir = os.path.join(current_dir, 'data')
            if os.path.exists(data_dir):
                data_files = os.listdir(data_dir)
            else:
                data_files = "Data directory does not exist"
        except Exception as e:
            data_files = f"Error listing data directory: {str(e)}"
        
        # Create response
        response = {
            "message": "Test function executed successfully",
            "current_directory": current_dir,
            "root_files": root_files,
            "model_files": model_files,
            "data_files": data_files,
            "environment_variables": env_vars
        }
        
        return func.HttpResponse(
            json.dumps(response, default=str),
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
