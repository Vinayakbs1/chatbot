import os
import subprocess
import json
from dotenv import load_dotenv

# Load existing environment variables
load_dotenv()

def run_command(command):
    """Run a shell command and return the output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running command: {result.stderr}")
            return None
        return result.stdout.strip()
    except Exception as e:
        print(f"Exception running command: {str(e)}")
        return None

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
    print("Getting Cosmos DB key...")
    
    # Get Cosmos DB key
    command = "az cosmosdb keys list --name careerbot-cosmos --resource-group career-bot-rg --query primaryMasterKey -o tsv"
    cosmos_key = run_command(command)
    
    if cosmos_key:
        update_env_file("COSMOS_KEY", cosmos_key)
        update_env_file("COSMOS_ENDPOINT", "https://careerbot-cosmos.documents.azure.com:443/")
        update_env_file("COSMOS_DATABASE", "careerdb")
        update_env_file("COSMOS_CONTAINER", "students")
        return True
    
    return False

def get_language_service_key():
    """Get Language Service key and update .env file"""
    print("Getting Language Service key...")
    
    # Get Language Service key
    command = "az cognitiveservices account keys list --name career-bot-rg --resource-group career-bot-rg --query key1 -o tsv"
    language_key = run_command(command)
    
    if language_key:
        update_env_file("LANGUAGE_KEY", language_key)
        update_env_file("LANGUAGE_ENDPOINT", "https://career-bot-rg.cognitiveservices.azure.com/")
        return True
    
    return False

def get_function_app_url():
    """Get Function App URL and update .env file"""
    print("Getting Function App URL...")
    
    # Get Function App URL
    command = "az functionapp show --name careerbot-functions --resource-group career-bot-rg --query defaultHostName -o tsv"
    function_host = run_command(command)
    
    if function_host:
        function_url = f"https://{function_host}"
        update_env_file("AZURE_FUNCTION_URL", function_url)
        return True
    
    return False

def main():
    """Main function to get all Azure keys and update .env file"""
    print("Checking if logged in to Azure CLI...")
    
    # Check if logged in to Azure CLI
    command = "az account show --query name -o tsv"
    account = run_command(command)
    
    if not account:
        print("Not logged in to Azure CLI. Please run 'az login' first.")
        return
    
    print(f"Logged in as: {account}")
    
    # Get all keys and update .env file
    cosmos_success = get_cosmos_db_key()
    language_success = get_language_service_key()
    function_success = get_function_app_url()
    
    # Add other required environment variables
    update_env_file("FLASK_APP", "app.py")
    update_env_file("FLASK_ENV", "development")
    update_env_file("SECRET_KEY", "your-secret-key-change-this-in-production")
    
    if cosmos_success and language_success and function_success:
        print("\nSuccessfully retrieved all Azure keys and updated .env file!")
        print("You can now run your application with Azure services integration.")
    else:
        print("\nSome keys could not be retrieved. Please check the error messages above.")

if __name__ == "__main__":
    main()
