import os
import argparse
import subprocess
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_azure_cli():
    """Check if Azure CLI is installed and logged in"""
    try:
        # Check if Azure CLI is installed
        result = subprocess.run(['az', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Azure CLI is not installed. Please install it from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
            return False
        
        # Check if logged in
        result = subprocess.run(['az', 'account', 'show'], capture_output=True, text=True)
        if result.returncode != 0:
            print("You are not logged in to Azure. Please run 'az login' first.")
            return False
        
        account_info = json.loads(result.stdout)
        print(f"Logged in as: {account_info['user']['name']}")
        print(f"Subscription: {account_info['name']}")
        
        return True
    
    except Exception as e:
        print(f"Error checking Azure CLI: {str(e)}")
        return False

def create_resource_group(resource_group, location):
    """Create a resource group if it doesn't exist"""
    try:
        # Check if resource group exists
        result = subprocess.run(
            ['az', 'group', 'exists', '--name', resource_group],
            capture_output=True, text=True
        )
        
        if result.stdout.strip() == 'true':
            print(f"Resource group '{resource_group}' already exists.")
            return True
        
        # Create resource group
        print(f"Creating resource group '{resource_group}' in {location}...")
        result = subprocess.run(
            ['az', 'group', 'create', '--name', resource_group, '--location', location],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            print(f"Error creating resource group: {result.stderr}")
            return False
        
        print(f"Resource group '{resource_group}' created successfully.")
        return True
    
    except Exception as e:
        print(f"Error creating resource group: {str(e)}")
        return False

def create_cosmos_db(resource_group, account_name, location):
    """Create a Cosmos DB account, database, and container"""
    try:
        # Check if Cosmos DB account exists
        result = subprocess.run(
            ['az', 'cosmosdb', 'check-name-exists', '--name', account_name],
            capture_output=True, text=True
        )
        
        if result.stdout.strip() == 'true':
            print(f"Cosmos DB account '{account_name}' already exists.")
        else:
            # Create Cosmos DB account
            print(f"Creating Cosmos DB account '{account_name}'...")
            result = subprocess.run([
                'az', 'cosmosdb', 'create',
                '--name', account_name,
                '--resource-group', resource_group,
                '--kind', 'GlobalDocumentDB',
                '--default-consistency-level', 'Session',
                '--locations', f"regionName={location}"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error creating Cosmos DB account: {result.stderr}")
                return False
            
            print(f"Cosmos DB account '{account_name}' created successfully.")
        
        # Create database
        database_name = "CareerGuidanceDB"
        print(f"Creating Cosmos DB database '{database_name}'...")
        result = subprocess.run([
            'az', 'cosmosdb', 'sql', 'database', 'create',
            '--account-name', account_name,
            '--resource-group', resource_group,
            '--name', database_name
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error creating database: {result.stderr}")
            return False
        
        # Create container
        container_name = "UserPreferences"
        print(f"Creating Cosmos DB container '{container_name}'...")
        result = subprocess.run([
            'az', 'cosmosdb', 'sql', 'container', 'create',
            '--account-name', account_name,
            '--database-name', database_name,
            '--resource-group', resource_group,
            '--name', container_name,
            '--partition-key-path', '/userId',
            '--throughput', '400'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error creating container: {result.stderr}")
            return False
        
        # Get connection string
        print("Getting Cosmos DB connection string...")
        result = subprocess.run([
            'az', 'cosmosdb', 'keys', 'list',
            '--name', account_name,
            '--resource-group', resource_group,
            '--type', 'connection-strings'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error getting connection string: {result.stderr}")
            return False
        
        connection_info = json.loads(result.stdout)
        connection_string = connection_info['connectionStrings'][0]['connectionString']
        
        # Get endpoint and key
        result = subprocess.run([
            'az', 'cosmosdb', 'keys', 'list',
            '--name', account_name,
            '--resource-group', resource_group
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error getting keys: {result.stderr}")
            return False
        
        keys_info = json.loads(result.stdout)
        endpoint = f"https://{account_name}.documents.azure.com:443/"
        key = keys_info['primaryMasterKey']
        
        print(f"Cosmos DB setup complete.")
        print(f"COSMOS_ENDPOINT={endpoint}")
        print(f"COSMOS_KEY={key}")
        
        # Update .env file
        update_env_file("COSMOS_ENDPOINT", endpoint)
        update_env_file("COSMOS_KEY", key)
        
        return True
    
    except Exception as e:
        print(f"Error creating Cosmos DB: {str(e)}")
        return False

def create_luis_resource(resource_group, name, location):
    """Create a LUIS resource"""
    try:
        # Create LUIS resource
        print(f"Creating LUIS resource '{name}'...")
        result = subprocess.run([
            'az', 'cognitiveservices', 'account', 'create',
            '--name', name,
            '--resource-group', resource_group,
            '--kind', 'LUIS',
            '--sku', 'F0',
            '--location', location
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error creating LUIS resource: {result.stderr}")
            return False
        
        # Get keys
        print("Getting LUIS keys...")
        result = subprocess.run([
            'az', 'cognitiveservices', 'account', 'keys', 'list',
            '--name', name,
            '--resource-group', resource_group
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error getting LUIS keys: {result.stderr}")
            return False
        
        keys_info = json.loads(result.stdout)
        key = keys_info['key1']
        
        # Get endpoint
        result = subprocess.run([
            'az', 'cognitiveservices', 'account', 'show',
            '--name', name,
            '--resource-group', resource_group
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error getting LUIS endpoint: {result.stderr}")
            return False
        
        account_info = json.loads(result.stdout)
        endpoint = account_info['properties']['endpoint']
        
        print(f"LUIS resource created successfully.")
        print(f"LUIS_ENDPOINT={endpoint}")
        print(f"LUIS_API_KEY={key}")
        
        # Update .env file
        update_env_file("LUIS_ENDPOINT", endpoint)
        update_env_file("LUIS_API_KEY", key)
        
        print("Now you need to create a LUIS app at https://www.luis.ai/ and get the app ID.")
        print("Then update the .env file with LUIS_APP_ID=your-app-id")
        
        return True
    
    except Exception as e:
        print(f"Error creating LUIS resource: {str(e)}")
        return False

def create_function_app(resource_group, name, location, storage_account=None):
    """Create an Azure Function App"""
    try:
        # Create storage account if not provided
        if not storage_account:
            storage_account = f"{name}storage".lower().replace('-', '')
            print(f"Creating storage account '{storage_account}'...")
            result = subprocess.run([
                'az', 'storage', 'account', 'create',
                '--name', storage_account,
                '--resource-group', resource_group,
                '--location', location,
                '--sku', 'Standard_LRS'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error creating storage account: {result.stderr}")
                return False
        
        # Create function app
        print(f"Creating function app '{name}'...")
        result = subprocess.run([
            'az', 'functionapp', 'create',
            '--name', name,
            '--resource-group', resource_group,
            '--storage-account', storage_account,
            '--consumption-plan-location', location,
            '--runtime', 'python',
            '--runtime-version', '3.9',
            '--functions-version', '4'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error creating function app: {result.stderr}")
            return False
        
        # Get function app URL
        result = subprocess.run([
            'az', 'functionapp', 'show',
            '--name', name,
            '--resource-group', resource_group,
            '--query', 'defaultHostName',
            '--output', 'tsv'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error getting function app URL: {result.stderr}")
            return False
        
        function_url = f"https://{result.stdout.strip()}"
        print(f"Function app created successfully.")
        print(f"AZURE_FUNCTION_URL={function_url}")
        
        # Update .env file
        update_env_file("AZURE_FUNCTION_URL", function_url)
        
        return True
    
    except Exception as e:
        print(f"Error creating function app: {str(e)}")
        return False

def create_web_app(resource_group, name, location):
    """Create an Azure Web App"""
    try:
        # Create app service plan
        plan_name = f"{name}-plan"
        print(f"Creating app service plan '{plan_name}'...")
        result = subprocess.run([
            'az', 'appservice', 'plan', 'create',
            '--name', plan_name,
            '--resource-group', resource_group,
            '--location', location,
            '--sku', 'F1',
            '--is-linux'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error creating app service plan: {result.stderr}")
            return False
        
        # Create web app
        print(f"Creating web app '{name}'...")
        result = subprocess.run([
            'az', 'webapp', 'create',
            '--name', name,
            '--resource-group', resource_group,
            '--plan', plan_name,
            '--runtime', 'PYTHON:3.9'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error creating web app: {result.stderr}")
            return False
        
        # Get web app URL
        result = subprocess.run([
            'az', 'webapp', 'show',
            '--name', name,
            '--resource-group', resource_group,
            '--query', 'defaultHostName',
            '--output', 'tsv'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error getting web app URL: {result.stderr}")
            return False
        
        web_app_url = f"https://{result.stdout.strip()}"
        print(f"Web app created successfully.")
        print(f"Web app URL: {web_app_url}")
        
        return True
    
    except Exception as e:
        print(f"Error creating web app: {str(e)}")
        return False

def update_env_file(key, value):
    """Update the .env file with a new key-value pair"""
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
    
    except Exception as e:
        print(f"Error updating .env file: {str(e)}")

def main():
    """Main function to deploy resources to Azure"""
    parser = argparse.ArgumentParser(description='Deploy Career Guidance Chatbot to Azure')
    parser.add_argument('--resource-group', default='career-guidance-chatbot-rg', help='Azure resource group name')
    parser.add_argument('--location', default='eastus', help='Azure region')
    parser.add_argument('--cosmos-account', default='career-guidance-cosmos', help='Cosmos DB account name')
    parser.add_argument('--luis-name', default='career-guidance-luis', help='LUIS resource name')
    parser.add_argument('--function-app', default='career-guidance-functions', help='Function app name')
    parser.add_argument('--web-app', default='career-guidance-webapp', help='Web app name')
    parser.add_argument('--skip-cosmos', action='store_true', help='Skip Cosmos DB creation')
    parser.add_argument('--skip-luis', action='store_true', help='Skip LUIS creation')
    parser.add_argument('--skip-function', action='store_true', help='Skip Function App creation')
    parser.add_argument('--skip-webapp', action='store_true', help='Skip Web App creation')
    args = parser.parse_args()
    
    # Check Azure CLI
    if not check_azure_cli():
        return
    
    # Create resource group
    if not create_resource_group(args.resource_group, args.location):
        return
    
    # Create Cosmos DB
    if not args.skip_cosmos:
        if not create_cosmos_db(args.resource_group, args.cosmos_account, args.location):
            return
    
    # Create LUIS resource
    if not args.skip_luis:
        if not create_luis_resource(args.resource_group, args.luis_name, args.location):
            return
    
    # Create Function App
    if not args.skip_function:
        if not create_function_app(args.resource_group, args.function_app, args.location):
            return
    
    # Create Web App
    if not args.skip_webapp:
        if not create_web_app(args.resource_group, args.web_app, args.location):
            return
    
    print("\nDeployment completed successfully!")
    print("Next steps:")
    print("1. Create a LUIS app at https://www.luis.ai/ and update the .env file with LUIS_APP_ID")
    print("2. Deploy your Azure Functions code")
    print("3. Deploy your Flask app to the Web App")
    print("4. Test your application")

if __name__ == "__main__":
    main()
