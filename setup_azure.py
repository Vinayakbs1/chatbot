import os
import subprocess
import sys
import time

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

def check_azure_cli():
    """Check if Azure CLI is installed"""
    print("Checking if Azure CLI is installed...")
    
    result = run_command("az --version", "Checking Azure CLI version")
    
    if not result:
        print("\nAzure CLI is not installed or not working properly.")
        print("Please install Azure CLI from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return False
    
    return True

def check_azure_login():
    """Check if logged in to Azure"""
    print("\nChecking if logged in to Azure...")
    
    result = run_command("az account show", "Checking Azure account")
    
    if not result:
        print("\nNot logged in to Azure. Please log in.")
        run_command("az login", "Logging in to Azure")
        
        # Check again after login
        result = run_command("az account show", "Checking Azure account after login")
        
        if not result:
            print("\nFailed to log in to Azure.")
            return False
    
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\nInstalling required Python packages...")
    
    result = run_command("pip install -r requirements.txt", "Installing dependencies")
    
    if not result:
        print("\nFailed to install dependencies.")
        return False
    
    return True

def get_azure_keys():
    """Get Azure keys and update .env file"""
    print("\nGetting Azure keys and updating .env file...")
    
    result = run_command("python get_azure_keys.py", "Getting Azure keys")
    
    if not result:
        print("\nFailed to get Azure keys.")
        return False
    
    return True

def create_cosmos_resources():
    """Create Cosmos DB database and container if they don't exist"""
    print("\nCreating Cosmos DB resources...")
    
    # Create a simple script to create Cosmos DB resources
    script_content = """
import os
from cosmos_db import CosmosDBManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Cosmos DB manager
cosmos_manager = CosmosDBManager()

# Create database and container
if cosmos_manager.is_connected():
    print("Connected to Cosmos DB")
    cosmos_manager.create_database_if_not_exists()
    cosmos_manager.create_container_if_not_exists()
    print("Cosmos DB resources created successfully")
else:
    print("Failed to connect to Cosmos DB. Check your environment variables.")
"""
    
    # Save the script
    with open("create_cosmos_resources.py", "w") as f:
        f.write(script_content)
    
    # Run the script
    result = run_command("python create_cosmos_resources.py", "Creating Cosmos DB resources")
    
    # Clean up
    if os.path.exists("create_cosmos_resources.py"):
        os.remove("create_cosmos_resources.py")
    
    if not result:
        print("\nFailed to create Cosmos DB resources.")
        return False
    
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
    print("Language Service is configured")
    
    # Test text analysis
    text = "I have experience with Python, Machine Learning, and Data Analysis"
    result = language_service.analyze_text(text)
    
    if "error" in result:
        print(f"Error analyzing text: {result['error']}")
    else:
        print(f"Extracted skills: {result['skills']}")
        print("Language Service is working correctly")
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
    
    if not result:
        print("\nFailed to test Language Service.")
        return False
    
    return True

def main():
    """Main function to set up Azure resources"""
    print("=== Setting up Azure resources for Career Guidance Chatbot ===\n")
    
    # Check Azure CLI
    if not check_azure_cli():
        return
    
    # Check Azure login
    if not check_azure_login():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Get Azure keys
    if not get_azure_keys():
        return
    
    # Create Cosmos DB resources
    if not create_cosmos_resources():
        return
    
    # Test Language Service
    if not test_language_service():
        return
    
    print("\n=== Azure resources setup completed successfully! ===")
    print("\nYou can now run your Career Guidance Chatbot with Azure services integration.")
    print("To start the application, run: python app.py")

if __name__ == "__main__":
    main()
