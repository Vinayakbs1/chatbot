import os
import subprocess
import sys

def run_command(command):
    """Run a command and return the output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return None
        return result.stdout.strip()
    except Exception as e:
        print(f"Exception: {str(e)}")
        return None

def main():
    """Main function to get Azure keys and update .env file"""
    print("=== Getting Azure Keys for Career Guidance Chatbot ===\n")
    
    # Check if Azure CLI is installed
    print("Checking if Azure CLI is installed...")
    az_version = run_command("az --version")
    
    if not az_version:
        print("Azure CLI is not installed or not in PATH.")
        print("Please install Azure CLI from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return
    
    # Check if logged in to Azure
    print("\nChecking if logged in to Azure...")
    account = run_command("az account show --query name -o tsv")
    
    if not account:
        print("Not logged in to Azure. Please run 'az login' first.")
        return
    
    print(f"Logged in as: {account}")
    
    # Get Cosmos DB key
    print("\nGetting Cosmos DB key...")
    cosmos_key = run_command("az cosmosdb keys list --name careerbot-cosmos --resource-group career-bot-rg --query primaryMasterKey -o tsv")
    
    if not cosmos_key:
        print("Failed to get Cosmos DB key.")
    else:
        print("Successfully retrieved Cosmos DB key.")
    
    # Get Language Service key
    print("\nGetting Language Service key...")
    language_key = run_command("az cognitiveservices account keys list --name career-bot-rg --resource-group career-bot-rg --query key1 -o tsv")
    
    if not language_key:
        print("Failed to get Language Service key.")
    else:
        print("Successfully retrieved Language Service key.")
    
    # Get Function App URL
    print("\nGetting Function App URL...")
    function_host = run_command("az functionapp show --name careerbot-functions --resource-group career-bot-rg --query defaultHostName -o tsv")
    
    if not function_host:
        print("Failed to get Function App URL.")
        function_url = ""
    else:
        function_url = f"https://{function_host}"
        print(f"Successfully retrieved Function App URL: {function_url}")
    
    # Update .env file
    print("\nUpdating .env file...")
    
    env_content = f"""# Azure Cosmos DB
COSMOS_ENDPOINT=https://careerbot-cosmos.documents.azure.com:443/
COSMOS_KEY={cosmos_key}
COSMOS_DATABASE=careerdb
COSMOS_CONTAINER=students

# Azure Language Service
LANGUAGE_ENDPOINT=https://career-bot-rg.cognitiveservices.azure.com/
LANGUAGE_KEY={language_key}

# Azure Function App
AZURE_FUNCTION_URL={function_url}

# Azure Resource Group
RESOURCE_GROUP=career-bot-rg

# Flask App
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this-in-production
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("Updated .env file with Azure keys and settings.")
    
    # Create Cosmos DB database and container
    print("\nCreating Cosmos DB database and container...")
    
    # Check if database exists
    db_exists = run_command("az cosmosdb sql database show --name careerdb --account-name careerbot-cosmos --resource-group career-bot-rg --query id -o tsv")
    
    if not db_exists:
        print("Creating database 'careerdb'...")
        create_db = run_command("az cosmosdb sql database create --name careerdb --account-name careerbot-cosmos --resource-group career-bot-rg")
        
        if not create_db:
            print("Failed to create database.")
        else:
            print("Database 'careerdb' created successfully.")
    else:
        print("Database 'careerdb' already exists.")
    
    # Check if container exists
    container_exists = run_command("az cosmosdb sql container show --name students --database-name careerdb --account-name careerbot-cosmos --resource-group career-bot-rg --query id -o tsv")
    
    if not container_exists:
        print("Creating container 'students'...")
        create_container = run_command("az cosmosdb sql container create --name students --database-name careerdb --account-name careerbot-cosmos --resource-group career-bot-rg --partition-key-path '/userId'")
        
        if not create_container:
            print("Failed to create container.")
        else:
            print("Container 'students' created successfully.")
    else:
        print("Container 'students' already exists.")
    
    print("\n=== Azure keys and resources setup completed! ===")
    print("\nYou can now run your application with: python app.py")

if __name__ == "__main__":
    main()
