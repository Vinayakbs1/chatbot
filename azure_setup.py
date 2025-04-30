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
    """Check if Azure CLI is installed and logged in"""
    print("Checking if Azure CLI is installed and logged in...")
    
    # Check if Azure CLI is installed
    result = run_command("az --version", "Checking Azure CLI version", show_output=False)
    
    if not result:
        print("\nAzure CLI is not installed or not working properly.")
        print("Please install Azure CLI from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return False
    
    # Check if logged in
    account = run_command("az account show --query name -o tsv", "Checking Azure account", show_output=False)
    
    if not account:
        print("\nNot logged in to Azure. Please run 'az login' first.")
        return False
    
    print(f"Azure CLI is installed and logged in as: {account}")
    return True

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
    db_exists_command = "az cosmosdb sql database show --name careerdb --account-name careerbot-cosmos --resource-group career-bot-rg --query id -o tsv 2>/dev/null"
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
    container_exists_command = "az cosmosdb sql container show --name students --database-name careerdb --account-name careerbot-cosmos --resource-group career-bot-rg --query id -o tsv 2>/dev/null"
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
    print("\nChecking required Python packages...")
    
    # Check if packages are installed
    packages = [
        "azure-cosmos",
        "azure-functions",
        "python-dotenv",
        "requests",
        "azure-storage-blob",
        "azure-ai-textanalytics"
    ]
    
    missing_packages = []
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Installing missing packages: {', '.join(missing_packages)}")
        for package in missing_packages:
            result = run_command(f"pip install {package}", f"Installing {package}")
            if not result:
                print(f"Failed to install {package}.")
    else:
        print("All required packages are already installed.")
    
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

def run_application():
    """Run the Flask application"""
    print("\nWould you like to run the application now? (y/n)")
    choice = input().lower()
    
    if choice == 'y':
        print("\nRunning the application...")
        print("The application will be available at http://localhost:5000")
        print("Press Ctrl+C to stop the application.")
        
        # Run the application
        os.system("python app.py")
    else:
        print("\nSkipping application startup.")
        print("You can run the application later with: python app.py")

def main():
    """Main function to set up Azure resources"""
    print("=== Automated Azure Setup for Career Guidance Chatbot ===\n")
    
    # Check Azure CLI
    if not check_azure_cli():
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
    
    print("\n=== Azure setup completed! ===")
    
    # Run the application
    run_application()

if __name__ == "__main__":
    main()
