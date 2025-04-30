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

def install_dependencies():
    """Install required Python packages"""
    print("\nInstalling required Python packages...")
    
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
        result = run_command(f"pip install {package}", f"Installing {package}")
        
        if not result:
            print(f"Failed to install {package}.")
    
    return True

def update_env_file():
    """Update the .env file with placeholder values"""
    print("\nUpdating .env file with placeholder values...")
    
    env_content = """# Azure Cosmos DB
COSMOS_ENDPOINT=https://careerbot-cosmos.documents.azure.com:443/
COSMOS_KEY=your-cosmos-key
COSMOS_DATABASE=careerdb
COSMOS_CONTAINER=students

# Azure Language Service
LANGUAGE_ENDPOINT=https://career-bot-rg.cognitiveservices.azure.com/
LANGUAGE_KEY=your-language-key

# Azure Function App
AZURE_FUNCTION_URL=https://careerbot-functions.azurewebsites.net

# Azure Resource Group
RESOURCE_GROUP=career-bot-rg

# Flask App
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this-in-production

# Note: Replace the placeholder values with your actual API keys
# You can get these from the Azure Portal
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("Updated .env file with placeholder values.")
    print("Please replace the placeholder values with your actual API keys from the Azure Portal.")
    
    return True

def run_application():
    """Run the Flask application"""
    print("\nWould you like to run the application now? (y/n)")
    choice = input().lower()
    
    if choice == 'y':
        print("\nRunning the application...")
        
        # Run the application
        run_command("python app.py", "Starting Flask application")
    else:
        print("\nSkipping application startup.")
        print("You can run the application later with: python app.py")

def main():
    """Main function to set up the application"""
    print("=== Local Setup for Career Guidance Chatbot ===\n")
    
    # Install dependencies
    install_dependencies()
    
    # Update .env file
    update_env_file()
    
    print("\n=== Setup completed! ===")
    print("\nTo complete the setup:")
    print("1. Open the .env file and replace the placeholder values with your actual API keys from the Azure Portal.")
    print("2. Make sure you have created the necessary resources in Azure:")
    print("   - Cosmos DB database 'careerdb' and container 'students'")
    print("   - Language Service")
    print("   - Function App with the necessary functions")
    
    # Run the application
    run_application()

if __name__ == "__main__":
    main()
