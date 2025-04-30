import os
import subprocess
import json
import time
import sys
from dotenv import load_dotenv

# Load existing environment variables
load_dotenv()

def run_command(command, description=None, show_output=True):
    """Run a shell command and return the output"""
    if description and show_output:
        print(f"\n{description}...")
    
    if show_output:
        print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            if show_output:
                print(f"Error running command: {result.stderr}")
            return None
        return result.stdout.strip()
    except Exception as e:
        if show_output:
            print(f"Exception running command: {str(e)}")
        return None

def check_azure_cli():
    """Check if Azure CLI is installed"""
    print("Checking if Azure CLI is installed...")
    
    result = run_command("az --version", "Checking Azure CLI version")
    
    if not result:
        print("\nAzure CLI is not installed or not working properly.")
        print("Please install Azure CLI from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return False
    
    print("Azure CLI is installed and working properly.")
    return True

def login_to_azure():
    """Log in to Azure"""
    print("\nChecking if logged in to Azure...")
    
    # Check if already logged in
    account = run_command("az account show --query name -o tsv", "Checking Azure account")
    
    if account:
        print(f"Already logged in as: {account}")
        return True
    
    # If not logged in, try to log in
    print("\nNot logged in to Azure. Logging in...")
    result = run_command("az login", "Logging in to Azure")
    
    if not result:
        print("Failed to log in to Azure.")
        return False
    
    # Check again after login
    account = run_command("az account show --query name -o tsv", "Checking Azure account after login")
    
    if account:
        print(f"Successfully logged in as: {account}")
        return True
    
    print("Failed to log in to Azure.")
    return False

def update_env_file(key, value):
    """Update the .env file with a new key-value pair"""
    if not value:
        print(f"No value provided for {key}, skipping")
        return
    
    try:
        # Create .env file if it doesn't exist
        if not os.path.exists('.env'):
            with open('.env', 'w') as f:
                f.write(f"{key}={value}\n")
            return
        
        # Read existing .env file
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        # Check if key already exists
        key_exists = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}\n"
                key_exists = True
                break
        
        # Add key if it doesn't exist
        if not key_exists:
            lines.append(f"{key}={value}\n")
        
        # Write updated .env file
        with open('.env', 'w') as f:
            f.writelines(lines)
        
        print(f"Updated {key} in .env file")
    
    except Exception as e:
        print(f"Error updating .env file: {str(e)}")

def get_cosmos_db_key():
    """Get Cosmos DB key and update .env file"""
    print("\nGetting Cosmos DB key...")
    
    # Get Cosmos DB key
    command = "az cosmosdb keys list --name careerbot-cosmos --resource-group career-bot-rg --query primaryMasterKey -o tsv"
    cosmos_key = run_command(command, "Getting Cosmos DB key")
    
    if cosmos_key:
        update_env_file("COSMOS_KEY", cosmos_key)
        update_env_file("COSMOS_ENDPOINT", "https://careerbot-cosmos.documents.azure.com:443/")
        update_env_file("COSMOS_DATABASE", "careerdb")
        update_env_file("COSMOS_CONTAINER", "students")
        return True
    
    return False

def get_language_service_key():
    """Get Language Service key and update .env file"""
    print("\nGetting Language Service key...")
    
    # Get Language Service key
    command = "az cognitiveservices account keys list --name career-bot-rg --resource-group career-bot-rg --query key1 -o tsv"
    language_key = run_command(command, "Getting Language Service key")
    
    if language_key:
        update_env_file("LANGUAGE_KEY", language_key)
        update_env_file("LANGUAGE_ENDPOINT", "https://career-bot-rg.cognitiveservices.azure.com/")
        return True
    
    return False

def get_function_app_url():
    """Get Function App URL and update .env file"""
    print("\nGetting Function App URL...")
    
    # Get Function App URL
    command = "az functionapp show --name careerbot-functions --resource-group career-bot-rg --query defaultHostName -o tsv"
    function_host = run_command(command, "Getting Function App URL")
    
    if function_host:
        function_url = f"https://{function_host}"
        update_env_file("AZURE_FUNCTION_URL", function_url)
        return True
    
    return False

def create_cosmos_db_resources():
    """Create Cosmos DB database and container"""
    print("\nCreating Cosmos DB resources...")
    
    # Check if database exists
    db_exists_command = "az cosmosdb sql database show --name careerdb --account-name careerbot-cosmos --resource-group career-bot-rg --query id -o tsv"
    db_exists = run_command(db_exists_command, "Checking if database exists", show_output=False)
    
    if not db_exists:
        print("Database 'careerdb' does not exist. Creating...")
        create_db_command = "az cosmosdb sql database create --name careerdb --account-name careerbot-cosmos --resource-group career-bot-rg"
        result = run_command(create_db_command, "Creating database")
        
        if not result:
            print("Failed to create database.")
            return False
        
        print("Database 'careerdb' created successfully.")
    else:
        print("Database 'careerdb' already exists.")
    
    # Check if container exists
    container_exists_command = "az cosmosdb sql container show --name students --database-name careerdb --account-name careerbot-cosmos --resource-group career-bot-rg --query id -o tsv"
    container_exists = run_command(container_exists_command, "Checking if container exists", show_output=False)
    
    if not container_exists:
        print("Container 'students' does not exist. Creating...")
        create_container_command = "az cosmosdb sql container create --name students --database-name careerdb --account-name careerbot-cosmos --resource-group career-bot-rg --partition-key-path '/userId'"
        result = run_command(create_container_command, "Creating container")
        
        if not result:
            print("Failed to create container.")
            return False
        
        print("Container 'students' created successfully.")
    else:
        print("Container 'students' already exists.")
    
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\nInstalling required Python packages...")
    
    # Install Azure packages
    packages = [
        "azure-cosmos",
        "azure-functions",
        "python-dotenv",
        "requests",
        "azure-storage-blob",
        "azure-ai-textanalytics"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        result = run_command(f"pip install {package}", f"Installing {package}", show_output=False)
        
        if not result:
            print(f"Failed to install {package}.")
            return False
    
    print("All packages installed successfully.")
    return True

def test_cosmos_db_connection():
    """Test connection to Cosmos DB"""
    print("\nTesting connection to Cosmos DB...")
    
    # Create a simple script to test Cosmos DB connection
    script_content = """
import os
from cosmos_db import CosmosDBManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Cosmos DB manager
cosmos_manager = CosmosDBManager()

# Test connection
if cosmos_manager.is_connected():
    print("Successfully connected to Cosmos DB!")
    print(f"Database: {cosmos_manager.database_name}")
    print(f"Container: {cosmos_manager.container_name}")
else:
    print("Failed to connect to Cosmos DB. Check your environment variables.")
"""
    
    # Save the script
    with open("test_cosmos_connection.py", "w") as f:
        f.write(script_content)
    
    # Run the script
    result = run_command("python test_cosmos_connection.py", "Testing Cosmos DB connection")
    
    # Clean up
    if os.path.exists("test_cosmos_connection.py"):
        os.remove("test_cosmos_connection.py")
    
    if not result or "Failed to connect" in result:
        print("Failed to connect to Cosmos DB.")
        return False
    
    print("Cosmos DB connection test successful.")
    return True

def test_language_service():
    """Test Azure Language Service"""
    print("\nTesting Azure Language Service...")
    
    # Create a simple script to test Language Service
    script_content = """
import os
from language_service import LanguageService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Language Service
language_service = LanguageService()

if language_service.is_configured():
    print("Language Service is configured!")
    
    # Test text analysis
    text = "I have experience with Python, Machine Learning, and Data Analysis"
    result = language_service.analyze_text(text)
    
    if "error" in result:
        print(f"Error analyzing text: {result['error']}")
    else:
        print(f"Extracted skills: {result['skills']}")
        print("Language Service is working correctly!")
else:
    print("Language Service is not configured. Check your environment variables.")
"""
    
    # Save the script
    with open("test_language_service.py", "w") as f:
        f.write(script_content)
    
    # Run the script
    result = run_command("python test_language_service.py", "Testing Language Service")
    
    # Clean up
    if os.path.exists("test_language_service.py"):
        os.remove("test_language_service.py")
    
    if not result or "not configured" in result or "Error analyzing text" in result:
        print("Failed to test Language Service.")
        return False
    
    print("Language Service test successful.")
    return True

def deploy_azure_functions():
    """Deploy Azure Functions"""
    print("\nChecking if Azure Functions Core Tools is installed...")
    
    # Check if Azure Functions Core Tools is installed
    result = run_command("func --version", "Checking Azure Functions Core Tools version")
    
    if not result:
        print("\nAzure Functions Core Tools is not installed.")
        print("Would you like to install it? (y/n)")
        choice = input().lower()
        
        if choice == 'y':
            print("Installing Azure Functions Core Tools...")
            run_command("npm install -g azure-functions-core-tools@4", "Installing Azure Functions Core Tools")
        else:
            print("Skipping Azure Functions deployment.")
            return False
    
    print("\nPreparing to deploy Azure Functions...")
    
    # Create azure_functions directory if it doesn't exist
    if not os.path.exists("azure_functions"):
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
    
    # Create function directories and files
    functions = [
        {
            "name": "predict_career",
            "route": "predict_career",
            "methods": ["post"]
        },
        {
            "name": "get_career_details",
            "route": "get_career_details",
            "methods": ["get"]
        },
        {
            "name": "recommend_skills",
            "route": "recommend_skills",
            "methods": ["post"]
        }
    ]
    
    for func in functions:
        func_dir = f"azure_functions/{func['name']}"
        
        if not os.path.exists(func_dir):
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
                    "methods": func["methods"],
                    "route": func["route"]
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
        if func["name"] == "predict_career":
            init_py = """
import logging
import json
import azure.functions as func
from shared.prediction import CareerPredictor
from shared.language_service import LanguageService

# Initialize services
predictor = CareerPredictor()
language_service = LanguageService()

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
        
        # Extract skills using Language Service
        if language_service.is_configured():
            extracted_skills = language_service.extract_skills(skills)
            processed_skills = ", ".join(extracted_skills) if extracted_skills else skills
        else:
            processed_skills = skills
        
        # Predict career
        predictions = predictor.predict_career(processed_skills)
        
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
        elif func["name"] == "get_career_details":
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
        elif func["name"] == "recommend_skills":
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
    
    # Create shared directory
    shared_dir = "azure_functions/shared"
    
    if not os.path.exists(shared_dir):
        os.makedirs(shared_dir)
    
    # Create __init__.py in shared directory
    with open(f"{shared_dir}/__init__.py", "w") as f:
        f.write("# Shared module")
    
    # Copy prediction.py to shared directory
    if os.path.exists("prediction.py"):
        with open("prediction.py", "r") as f:
            prediction_content = f.read()
        
        with open(f"{shared_dir}/prediction.py", "w") as f:
            f.write(prediction_content)
    
    # Copy language_service.py to shared directory
    if os.path.exists("language_service.py"):
        with open("language_service.py", "r") as f:
            language_service_content = f.read()
        
        with open(f"{shared_dir}/language_service.py", "w") as f:
            f.write(language_service_content)
    
    # Copy cosmos_db.py to shared directory
    if os.path.exists("cosmos_db.py"):
        with open("cosmos_db.py", "r") as f:
            cosmos_db_content = f.read()
        
        with open(f"{shared_dir}/cosmos_db.py", "w") as f:
            f.write(cosmos_db_content)
    
    # Create models directory in shared directory
    models_dir = f"{shared_dir}/models"
    
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    
    # Copy model files to models directory
    if os.path.exists("models"):
        for file in os.listdir("models"):
            if os.path.isfile(os.path.join("models", file)):
                with open(os.path.join("models", file), "rb") as f:
                    content = f.read()
                
                with open(os.path.join(models_dir, file), "wb") as f:
                    f.write(content)
    
    print("\nAzure Functions prepared for deployment.")
    print("Would you like to deploy the functions to Azure? (y/n)")
    choice = input().lower()
    
    if choice == 'y':
        print("\nDeploying Azure Functions...")
        
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
    else:
        print("Skipping Azure Functions deployment.")
    
    return True

def run_application():
    """Run the Flask application"""
    print("\nWould you like to run the application now? (y/n)")
    choice = input().lower()
    
    if choice == 'y':
        print("\nRunning the application...")
        
        # Run the application
        subprocess.Popen(["python", "app.py"])
        
        print("\nApplication is running at http://127.0.0.1:5000")
        print("Press Ctrl+C in the terminal to stop the application.")
    else:
        print("\nSkipping application startup.")
        print("You can run the application later with: python app.py")

def main():
    """Main function to set up Azure resources"""
    print("=== Automated Azure Setup for Career Guidance Chatbot ===\n")
    
    # Check Azure CLI
    if not check_azure_cli():
        return
    
    # Log in to Azure
    if not login_to_azure():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Get Azure keys
    cosmos_success = get_cosmos_db_key()
    language_success = get_language_service_key()
    function_success = get_function_app_url()
    
    # Add other required environment variables
    update_env_file("FLASK_APP", "app.py")
    update_env_file("FLASK_ENV", "development")
    update_env_file("SECRET_KEY", "your-secret-key-change-this-in-production")
    
    # Create Cosmos DB resources
    if cosmos_success:
        cosmos_db_success = create_cosmos_db_resources()
    else:
        print("\nSkipping Cosmos DB resource creation due to previous errors.")
        cosmos_db_success = False
    
    # Test connections
    if cosmos_success and cosmos_db_success:
        test_cosmos_db_connection()
    
    if language_success:
        test_language_service()
    
    # Deploy Azure Functions
    if function_success:
        deploy_azure_functions()
    
    print("\n=== Azure setup completed! ===")
    
    # Run the application
    run_application()

if __name__ == "__main__":
    main()
