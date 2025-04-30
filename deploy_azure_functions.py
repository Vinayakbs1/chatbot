import os
import subprocess
import shutil
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_command(command, description=None):
    """Run a shell command and print the output"""
    if description:
        print(f"\n{description}...")
    
    print(f"Running: {command}")
    
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Print output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # Get the return code
        return_code = process.poll()
        
        if return_code != 0:
            error = process.stderr.read()
            print(f"Error: {error}")
            return False
        
        return True
    
    except Exception as e:
        print(f"Exception: {str(e)}")
        return False

def create_function_project():
    """Create Azure Functions project structure"""
    print("\nCreating Azure Functions project structure...")
    
    # Create azure_functions directory if it doesn't exist
    if os.path.exists("azure_functions"):
        print("azure_functions directory already exists. Removing...")
        shutil.rmtree("azure_functions")
    
    os.makedirs("azure_functions")
    
    # Create host.json
    host_json = {
        "version": "2.0",
        "logging": {
            "applicationInsights": {
                "samplingSettings": {
                    "isEnabled": True,
                    "excludedTypes": "Request"
                }
            }
        },
        "extensionBundle": {
            "id": "Microsoft.Azure.Functions.ExtensionBundle",
            "version": "[3.*, 4.0.0)"
        }
    }
    
    with open("azure_functions/host.json", "w") as f:
        json.dump(host_json, f, indent=4)
    
    # Create local.settings.json
    local_settings = {
        "IsEncrypted": False,
        "Values": {
            "AzureWebJobsStorage": "",
            "FUNCTIONS_WORKER_RUNTIME": "python",
            "COSMOS_ENDPOINT": os.environ.get("COSMOS_ENDPOINT", ""),
            "COSMOS_KEY": os.environ.get("COSMOS_KEY", ""),
            "COSMOS_DATABASE": os.environ.get("COSMOS_DATABASE", "careerdb"),
            "COSMOS_CONTAINER": os.environ.get("COSMOS_CONTAINER", "students"),
            "LANGUAGE_ENDPOINT": os.environ.get("LANGUAGE_ENDPOINT", ""),
            "LANGUAGE_KEY": os.environ.get("LANGUAGE_KEY", "")
        }
    }
    
    with open("azure_functions/local.settings.json", "w") as f:
        json.dump(local_settings, f, indent=4)
    
    # Create requirements.txt
    requirements = """
azure-functions
azure-cosmos
azure-ai-textanalytics
python-dotenv
requests
numpy
pandas
scikit-learn
joblib
nltk
"""
    
    with open("azure_functions/requirements.txt", "w") as f:
        f.write(requirements.strip())
    
    # Create shared directory
    shared_dir = "azure_functions/shared"
    os.makedirs(shared_dir)
    
    # Create __init__.py in shared directory
    with open(f"{shared_dir}/__init__.py", "w") as f:
        f.write("# Shared module")
    
    # Copy prediction.py to shared directory
    if os.path.exists("prediction.py"):
        shutil.copy("prediction.py", f"{shared_dir}/prediction.py")
    else:
        print("Warning: prediction.py not found. Please create it manually.")
    
    # Create models directory in shared directory
    models_dir = f"{shared_dir}/models"
    os.makedirs(models_dir)
    
    # Copy model files to models directory
    if os.path.exists("models"):
        for file in os.listdir("models"):
            if os.path.isfile(os.path.join("models", file)):
                shutil.copy(os.path.join("models", file), os.path.join(models_dir, file))
    else:
        print("Warning: models directory not found. Please create it manually.")
    
    print("Azure Functions project structure created successfully.")
    return True

def create_predict_career_function():
    """Create predict_career function"""
    print("\nCreating predict_career function...")
    
    # Create function directory
    func_dir = "azure_functions/predict_career"
    os.makedirs(func_dir)
    
    # Create function.json
    function_json = {
        "scriptFile": "__init__.py",
        "bindings": [
            {
                "authLevel": "anonymous",
                "type": "httpTrigger",
                "direction": "in",
                "name": "req",
                "methods": ["post"],
                "route": "predict_career"
            },
            {
                "type": "http",
                "direction": "out",
                "name": "$return"
            }
        ]
    }
    
    with open(f"{func_dir}/function.json", "w") as f:
        json.dump(function_json, f, indent=4)
    
    # Create __init__.py
    init_py = """
import logging
import json
import azure.functions as func
from shared.prediction import CareerPredictor

# Initialize predictor
predictor = CareerPredictor()

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request for predict_career.')
    
    try:
        # Get request body
        req_body = req.get_json()
        skills = req_body.get('skills', '')
        
        if not skills:
            return func.HttpResponse(
                json.dumps({"error": "No skills provided"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Predict career
        predictions = predictor.predict_career(skills)
        
        return func.HttpResponse(
            json.dumps({"predictions": predictions}),
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in predict_career: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
"""
    
    with open(f"{func_dir}/__init__.py", "w") as f:
        f.write(init_py.strip())
    
    print("predict_career function created successfully.")
    return True

def create_get_career_details_function():
    """Create get_career_details function"""
    print("\nCreating get_career_details function...")
    
    # Create function directory
    func_dir = "azure_functions/get_career_details"
    os.makedirs(func_dir)
    
    # Create function.json
    function_json = {
        "scriptFile": "__init__.py",
        "bindings": [
            {
                "authLevel": "anonymous",
                "type": "httpTrigger",
                "direction": "in",
                "name": "req",
                "methods": ["get"],
                "route": "get_career_details"
            },
            {
                "type": "http",
                "direction": "out",
                "name": "$return"
            }
        ]
    }
    
    with open(f"{func_dir}/function.json", "w") as f:
        json.dump(function_json, f, indent=4)
    
    # Create __init__.py
    init_py = """
import logging
import json
import azure.functions as func
from shared.prediction import CareerPredictor

# Initialize predictor
predictor = CareerPredictor()

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request for get_career_details.')
    
    try:
        # Get career from query parameters
        career = req.params.get('career')
        
        if not career:
            return func.HttpResponse(
                json.dumps({"error": "No career specified"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Get career details
        details = predictor.get_career_details(career)
        
        return func.HttpResponse(
            json.dumps(details),
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in get_career_details: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
"""
    
    with open(f"{func_dir}/__init__.py", "w") as f:
        f.write(init_py.strip())
    
    print("get_career_details function created successfully.")
    return True

def create_recommend_skills_function():
    """Create recommend_skills function"""
    print("\nCreating recommend_skills function...")
    
    # Create function directory
    func_dir = "azure_functions/recommend_skills"
    os.makedirs(func_dir)
    
    # Create function.json
    function_json = {
        "scriptFile": "__init__.py",
        "bindings": [
            {
                "authLevel": "anonymous",
                "type": "httpTrigger",
                "direction": "in",
                "name": "req",
                "methods": ["post"],
                "route": "recommend_skills"
            },
            {
                "type": "http",
                "direction": "out",
                "name": "$return"
            }
        ]
    }
    
    with open(f"{func_dir}/function.json", "w") as f:
        json.dump(function_json, f, indent=4)
    
    # Create __init__.py
    init_py = """
import logging
import json
import azure.functions as func
from shared.prediction import get_skill_recommendations

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request for recommend_skills.')
    
    try:
        # Get request body
        req_body = req.get_json()
        skills = req_body.get('skills', [])
        target_career = req_body.get('targetCareer', None)
        
        if not skills:
            return func.HttpResponse(
                json.dumps({"error": "No skills provided"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Get skill recommendations
        recommended_skills = get_skill_recommendations(skills)
        
        return func.HttpResponse(
            json.dumps({"recommended_skills": recommended_skills}),
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f"Error in recommend_skills: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )
"""
    
    with open(f"{func_dir}/__init__.py", "w") as f:
        f.write(init_py.strip())
    
    print("recommend_skills function created successfully.")
    return True

def deploy_functions():
    """Deploy Azure Functions"""
    print("\nDeploying Azure Functions...")
    
    # Check if Azure Functions Core Tools is installed
    result = run_command("func --version", "Checking Azure Functions Core Tools version")
    
    if not result:
        print("\nAzure Functions Core Tools is not installed.")
        print("Please install it from: https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local")
        return False
    
    # Change to azure_functions directory
    os.chdir("azure_functions")
    
    # Deploy to Azure
    result = run_command("func azure functionapp publish careerbot-functions", "Deploying Azure Functions")
    
    # Change back to original directory
    os.chdir("..")
    
    if not result:
        print("Failed to deploy Azure Functions.")
        return False
    
    print("Azure Functions deployed successfully!")
    return True

def main():
    """Main function to deploy Azure Functions"""
    print("=== Deploying Azure Functions for Career Guidance Chatbot ===\n")
    
    # Create function project
    if not create_function_project():
        print("\nFailed to create function project.")
        return
    
    # Create functions
    create_predict_career_function()
    create_get_career_details_function()
    create_recommend_skills_function()
    
    # Deploy functions
    print("\nWould you like to deploy the functions to Azure? (y/n)")
    choice = input().lower()
    
    if choice == 'y':
        if not deploy_functions():
            print("\nFailed to deploy functions.")
            return
    else:
        print("\nSkipping function deployment.")
        print("You can deploy the functions later with: cd azure_functions && func azure functionapp publish careerbot-functions")
    
    print("\n=== Azure Functions deployment completed! ===")
    print("\nYou can now run your application with Azure Functions integration.")

if __name__ == "__main__":
    main()
