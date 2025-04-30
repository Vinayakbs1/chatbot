import os
import argparse
import subprocess
import json
import time
import shutil
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

def get_cosmos_keys(resource_group, account_name):
    """Get Cosmos DB keys and update .env file"""
    try:
        print(f"Getting keys for Cosmos DB account '{account_name}'...")
        result = subprocess.run([
            'az', 'cosmosdb', 'keys', 'list',
            '--name', account_name,
            '--resource-group', resource_group
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error getting Cosmos DB keys: {result.stderr}")
            return False
        
        keys = json.loads(result.stdout)
        primary_key = keys['primaryMasterKey']
        
        # Update .env file
        update_env_file("COSMOS_KEY", primary_key)
        print("Cosmos DB key added to .env file.")
        
        return True
    
    except Exception as e:
        print(f"Error getting Cosmos DB keys: {str(e)}")
        return False

def setup_cosmos_db(resource_group, account_name):
    """Set up Cosmos DB database and container if they don't exist"""
    try:
        # Get Cosmos DB keys first
        if not get_cosmos_keys(resource_group, account_name):
            return False
        
        # Create database
        database_name = os.environ.get("COSMOS_DATABASE", "CareerGuidanceDB")
        print(f"Creating Cosmos DB database '{database_name}' if it doesn't exist...")
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
        container_name = os.environ.get("COSMOS_CONTAINER", "UserPreferences")
        print(f"Creating Cosmos DB container '{container_name}' if it doesn't exist...")
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
        
        print(f"Cosmos DB setup complete.")
        return True
    
    except Exception as e:
        print(f"Error setting up Cosmos DB: {str(e)}")
        return False

def prepare_functions_for_deployment():
    """Prepare Azure Functions for deployment"""
    try:
        # Create a deployment package
        deploy_dir = 'function_deploy'
        if os.path.exists(deploy_dir):
            shutil.rmtree(deploy_dir)
        os.makedirs(deploy_dir, exist_ok=True)
        
        # Copy Azure Functions code
        print("Copying Azure Functions code...")
        shutil.copytree('azure_functions', f'{deploy_dir}/azure_functions', dirs_exist_ok=True)
        
        # Create models directory
        os.makedirs(f'{deploy_dir}/models', exist_ok=True)
        
        # Copy models
        print("Copying models...")
        if os.path.exists('models'):
            for file in os.listdir('models'):
                if file.endswith('.pkl'):
                    shutil.copy(f'models/{file}', f'{deploy_dir}/models/{file}')
        
        # Create data directory
        os.makedirs(f'{deploy_dir}/data', exist_ok=True)
        
        # Copy preprocessed data
        print("Copying preprocessed data...")
        if os.path.exists('preprocessed_career_data.csv'):
            shutil.copy('preprocessed_career_data.csv', f'{deploy_dir}/data/preprocessed_career_data.csv')
        
        # Create zip file
        print("Creating deployment zip file...")
        shutil.make_archive('function_deploy', 'zip', deploy_dir)
        
        print("Deployment package prepared successfully.")
        return True
    
    except Exception as e:
        print(f"Error preparing functions for deployment: {str(e)}")
        return False

def deploy_functions(resource_group, function_app):
    """Deploy Azure Functions to existing Function App"""
    try:
        # Check if function app exists
        print(f"Checking if function app '{function_app}' exists...")
        result = subprocess.run([
            'az', 'functionapp', 'show',
            '--name', function_app,
            '--resource-group', resource_group
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Function app '{function_app}' does not exist.")
            return False
        
        # Prepare deployment package
        if not prepare_functions_for_deployment():
            return False
        
        # Deploy functions
        print(f"Deploying functions to '{function_app}'...")
        result = subprocess.run([
            'az', 'functionapp', 'deployment', 'source', 'config-zip',
            '--name', function_app,
            '--resource-group', resource_group,
            '--src', 'function_deploy.zip'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error deploying functions: {result.stderr}")
            return False
        
        print("Functions deployed successfully.")
        
        # Configure app settings
        print("Configuring function app settings...")
        cosmos_endpoint = os.environ.get('COSMOS_ENDPOINT', '')
        cosmos_key = os.environ.get('COSMOS_KEY', '')
        
        if cosmos_endpoint and cosmos_key:
            result = subprocess.run([
                'az', 'functionapp', 'config', 'appsettings', 'set',
                '--name', function_app,
                '--resource-group', resource_group,
                '--settings',
                f"COSMOS_ENDPOINT={cosmos_endpoint}",
                f"COSMOS_KEY={cosmos_key}",
                f"COSMOS_DATABASE={os.environ.get('COSMOS_DATABASE', 'CareerGuidanceDB')}",
                f"COSMOS_CONTAINER={os.environ.get('COSMOS_CONTAINER', 'UserPreferences')}"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error configuring app settings: {result.stderr}")
                return False
            
            print("Function app settings configured successfully.")
        else:
            print("Warning: Cosmos DB connection details not found in environment variables.")
        
        return True
    
    except Exception as e:
        print(f"Error deploying functions: {str(e)}")
        return False

def create_web_app(resource_group, app_service_plan, name):
    """Create a web app if it doesn't exist"""
    try:
        # Check if web app exists
        print(f"Checking if web app '{name}' exists...")
        result = subprocess.run([
            'az', 'webapp', 'show',
            '--name', name,
            '--resource-group', resource_group
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Web app '{name}' already exists.")
            return True
        
        # Create web app
        print(f"Creating web app '{name}'...")
        result = subprocess.run([
            'az', 'webapp', 'create',
            '--name', name,
            '--resource-group', resource_group,
            '--plan', app_service_plan,
            '--runtime', 'PYTHON:3.9'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error creating web app: {result.stderr}")
            return False
        
        print(f"Web app '{name}' created successfully.")
        return True
    
    except Exception as e:
        print(f"Error creating web app: {str(e)}")
        return False

def deploy_web_app(resource_group, web_app):
    """Deploy Flask app to Azure Web App"""
    try:
        # Check if web app exists
        print(f"Checking if web app '{web_app}' exists...")
        result = subprocess.run([
            'az', 'webapp', 'show',
            '--name', web_app,
            '--resource-group', resource_group
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Web app '{web_app}' does not exist.")
            return False
        
        # Create deployment package
        print("Creating deployment package...")
        deploy_dir = 'web_deploy'
        if os.path.exists(deploy_dir):
            shutil.rmtree(deploy_dir)
        os.makedirs(deploy_dir, exist_ok=True)
        
        # Copy necessary files
        files_to_copy = [
            'app.py', 'prediction.py', 'cosmos_db.py', 'requirements.txt',
            '.env'
        ]
        
        for file in files_to_copy:
            if os.path.exists(file):
                target_dir = os.path.dirname(f'{deploy_dir}/{file}')
                if target_dir and not os.path.exists(target_dir):
                    os.makedirs(target_dir, exist_ok=True)
                shutil.copy(file, f'{deploy_dir}/{file}')
        
        # Copy models
        os.makedirs(f'{deploy_dir}/models', exist_ok=True)
        if os.path.exists('models'):
            for file in os.listdir('models'):
                if file.endswith('.pkl'):
                    shutil.copy(f'models/{file}', f'{deploy_dir}/models/{file}')
        
        # Copy preprocessed data
        if os.path.exists('preprocessed_career_data.csv'):
            shutil.copy('preprocessed_career_data.csv', f'{deploy_dir}/preprocessed_career_data.csv')
        
        # Copy templates directory
        if os.path.exists('templates'):
            shutil.copytree('templates', f'{deploy_dir}/templates', dirs_exist_ok=True)
        
        # Create startup file
        with open(f'{deploy_dir}/startup.txt', 'w') as f:
            f.write('gunicorn --bind=0.0.0.0 --timeout 600 app:app')
        
        # Create web.config file
        with open(f'{deploy_dir}/web.config', 'w') as f:
            f.write('''<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="FastCgiModule" scriptProcessor="D:\\home\\Python\\python.exe|D:\\home\\Python\\wfastcgi.py" resourceType="Unspecified" requireAccess="Script"/>
    </handlers>
    <rewrite>
      <rules>
        <rule name="Static Files" stopProcessing="true">
          <match url="^/static/.*" ignoreCase="true"/>
          <action type="Rewrite" url="^/static/.*" appendQueryString="true"/>
        </rule>
        <rule name="Configure Python" stopProcessing="true">
          <match url="(.*)" ignoreCase="false"/>
          <action type="Rewrite" url="app.py"/>
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
  <appSettings>
    <add key="PYTHONPATH" value="D:\\home\\site\\wwwroot"/>
    <add key="WSGI_HANDLER" value="app.app"/>
    <add key="WSGI_LOG" value="D:\\home\\LogFiles\\wfastcgi.log"/>
  </appSettings>
</configuration>''')
        
        # Create requirements.txt with gunicorn
        with open(f'{deploy_dir}/requirements.txt', 'w') as f:
            with open('requirements.txt', 'r') as original:
                content = original.read()
            if 'gunicorn' not in content:
                f.write(content + '\ngunicorn==20.1.0\n')
            else:
                f.write(content)
        
        # Zip the package
        print("Creating zip file...")
        shutil.make_archive('web_deploy_package', 'zip', deploy_dir)
        
        # Deploy to Azure
        print(f"Deploying to web app '{web_app}'...")
        result = subprocess.run([
            'az', 'webapp', 'deployment', 'source', 'config-zip',
            '--name', web_app,
            '--resource-group', resource_group,
            '--src', 'web_deploy_package.zip'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error deploying web app: {result.stderr}")
            return False
        
        # Configure app settings
        print("Configuring web app settings...")
        cosmos_endpoint = os.environ.get('COSMOS_ENDPOINT', '')
        cosmos_key = os.environ.get('COSMOS_KEY', '')
        luis_endpoint = os.environ.get('LUIS_ENDPOINT', '')
        luis_app_id = os.environ.get('LUIS_APP_ID', '')
        luis_api_key = os.environ.get('LUIS_API_KEY', '')
        azure_function_url = os.environ.get('AZURE_FUNCTION_URL', '')
        
        settings = [
            f"COSMOS_DATABASE={os.environ.get('COSMOS_DATABASE', 'CareerGuidanceDB')}",
            f"COSMOS_CONTAINER={os.environ.get('COSMOS_CONTAINER', 'UserPreferences')}",
            "FLASK_ENV=production",
            "SCM_DO_BUILD_DURING_DEPLOYMENT=true",
            "PYTHONPATH=/home/site/wwwroot",
            f"SECRET_KEY={os.environ.get('SECRET_KEY', 'default-secret-key')}"
        ]
        
        if cosmos_endpoint:
            settings.append(f"COSMOS_ENDPOINT={cosmos_endpoint}")
        if cosmos_key:
            settings.append(f"COSMOS_KEY={cosmos_key}")
        if luis_endpoint:
            settings.append(f"LUIS_ENDPOINT={luis_endpoint}")
        if luis_app_id:
            settings.append(f"LUIS_APP_ID={luis_app_id}")
        if luis_api_key:
            settings.append(f"LUIS_API_KEY={luis_api_key}")
        if azure_function_url:
            settings.append(f"AZURE_FUNCTION_URL={azure_function_url}")
        
        result = subprocess.run([
            'az', 'webapp', 'config', 'appsettings', 'set',
            '--name', web_app,
            '--resource-group', resource_group,
            '--settings'
        ] + settings, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error configuring app settings: {result.stderr}")
            return False
        
        print("Web app deployed and configured successfully.")
        
        # Get web app URL
        result = subprocess.run([
            'az', 'webapp', 'show',
            '--name', web_app,
            '--resource-group', resource_group,
            '--query', 'defaultHostName',
            '--output', 'tsv'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            web_app_url = f"https://{result.stdout.strip()}"
            print(f"Web app URL: {web_app_url}")
        
        return True
    
    except Exception as e:
        print(f"Error deploying web app: {str(e)}")
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
    """Main function to deploy to existing Azure resources"""
    parser = argparse.ArgumentParser(description='Deploy Career Guidance Chatbot to existing Azure resources')
    parser.add_argument('--resource-group', default=os.environ.get('RESOURCE_GROUP', 'career-bot-rg'), 
                        help='Azure resource group name')
    parser.add_argument('--cosmos-account', default='careerbot-cosmos', 
                        help='Cosmos DB account name')
    parser.add_argument('--function-app', default='careerbot-functions', 
                        help='Function app name')
    parser.add_argument('--app-service-plan', default='ASP-careerbotg-b509', 
                        help='App Service Plan name')
    parser.add_argument('--web-app', default='careerbot-webapp', 
                        help='Web app name')
    parser.add_argument('--skip-cosmos', action='store_true', 
                        help='Skip Cosmos DB setup')
    parser.add_argument('--skip-functions', action='store_true', 
                        help='Skip Function App deployment')
    parser.add_argument('--skip-webapp', action='store_true', 
                        help='Skip Web App deployment')
    args = parser.parse_args()
    
    # Check Azure CLI
    if not check_azure_cli():
        return
    
    # Set up Cosmos DB
    if not args.skip_cosmos:
        if not setup_cosmos_db(args.resource_group, args.cosmos_account):
            print("Cosmos DB setup failed.")
    
    # Deploy Azure Functions
    if not args.skip_functions:
        if not deploy_functions(args.resource_group, args.function_app):
            print("Function deployment failed.")
    
    # Create and deploy Web App
    if not args.skip_webapp:
        if not create_web_app(args.resource_group, args.app_service_plan, args.web_app):
            print("Web app creation failed.")
        elif not deploy_web_app(args.resource_group, args.web_app):
            print("Web app deployment failed.")
    
    print("\nDeployment completed!")
    print("\nNext steps:")
    print("1. If you haven't already, set up LUIS at https://www.luis.ai/")
    print("2. Update the .env file with your LUIS_APP_ID and LUIS_API_KEY")
    print("3. Test your application by visiting the web app URL")

if __name__ == "__main__":
    main()
