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

def prepare_functions_for_deployment():
    """Prepare Azure Functions for deployment"""
    try:
        # Create a deployment package
        deploy_dir = 'function_deploy'
        os.makedirs(deploy_dir, exist_ok=True)
        
        # Copy Azure Functions code
        print("Copying Azure Functions code...")
        shutil.copytree('azure_functions', f'{deploy_dir}/azure_functions', dirs_exist_ok=True)
        
        # Copy models directory
        print("Copying models...")
        os.makedirs(f'{deploy_dir}/models', exist_ok=True)
        if os.path.exists('models'):
            for file in os.listdir('models'):
                if file.endswith('.pkl'):
                    shutil.copy(f'models/{file}', f'{deploy_dir}/models/{file}')
        
        # Copy preprocessed data
        print("Copying preprocessed data...")
        os.makedirs(f'{deploy_dir}/data', exist_ok=True)
        if os.path.exists('preprocessed_career_data.csv'):
            shutil.copy('preprocessed_career_data.csv', f'{deploy_dir}/data/preprocessed_career_data.csv')
        
        print("Deployment package prepared successfully.")
        return True
    
    except Exception as e:
        print(f"Error preparing functions for deployment: {str(e)}")
        return False

def deploy_functions(resource_group, function_app):
    """Deploy Azure Functions to Azure"""
    try:
        # Check if function app exists
        print(f"Checking if function app '{function_app}' exists...")
        result = subprocess.run([
            'az', 'functionapp', 'show',
            '--name', function_app,
            '--resource-group', resource_group
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Function app '{function_app}' does not exist. Please create it first.")
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
                "COSMOS_DATABASE=CareerGuidanceDB",
                "COSMOS_CONTAINER=UserPreferences"
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
            print(f"Web app '{web_app}' does not exist. Please create it first.")
            return False
        
        # Create deployment package
        print("Creating deployment package...")
        os.makedirs('web_deploy', exist_ok=True)
        
        # Copy necessary files
        files_to_copy = [
            'app.py', 'prediction.py', 'cosmos_db.py', 'requirements.txt',
            '.env', 'models/best_model.pkl', 'models/tfidf_vectorizer.pkl',
            'preprocessed_career_data.csv'
        ]
        
        for file in files_to_copy:
            if os.path.exists(file):
                target_dir = os.path.dirname(f'web_deploy/{file}')
                if target_dir and not os.path.exists(target_dir):
                    os.makedirs(target_dir, exist_ok=True)
                shutil.copy(file, f'web_deploy/{file}')
        
        # Copy templates directory
        if os.path.exists('templates'):
            shutil.copytree('templates', 'web_deploy/templates', dirs_exist_ok=True)
        
        # Create startup file
        with open('web_deploy/startup.txt', 'w') as f:
            f.write('gunicorn --bind=0.0.0.0 --timeout 600 app:app')
        
        # Zip the package
        shutil.make_archive('web_deploy_package', 'zip', 'web_deploy')
        
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
            "COSMOS_DATABASE=CareerGuidanceDB",
            "COSMOS_CONTAINER=UserPreferences",
            "FLASK_ENV=production",
            "SCM_DO_BUILD_DURING_DEPLOYMENT=true",
            "PYTHONPATH=/home/site/wwwroot"
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

def main():
    """Main function to deploy Azure Functions and Web App"""
    parser = argparse.ArgumentParser(description='Deploy Career Guidance Chatbot Functions and Web App')
    parser.add_argument('--resource-group', default='career-guidance-chatbot-rg', help='Azure resource group name')
    parser.add_argument('--function-app', default='career-guidance-functions', help='Function app name')
    parser.add_argument('--web-app', default='career-guidance-webapp', help='Web app name')
    parser.add_argument('--skip-functions', action='store_true', help='Skip Function App deployment')
    parser.add_argument('--skip-webapp', action='store_true', help='Skip Web App deployment')
    args = parser.parse_args()
    
    # Check Azure CLI
    if not check_azure_cli():
        return
    
    # Deploy Azure Functions
    if not args.skip_functions:
        if not deploy_functions(args.resource_group, args.function_app):
            print("Function deployment failed.")
    
    # Deploy Web App
    if not args.skip_webapp:
        if not deploy_web_app(args.resource_group, args.web_app):
            print("Web app deployment failed.")
    
    print("\nDeployment completed!")

if __name__ == "__main__":
    main()
