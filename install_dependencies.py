import subprocess
import sys
import os

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

def install_python_packages():
    """Install required Python packages"""
    print("\nInstalling required Python packages...")
    
    result = run_command("pip install -r requirements.txt", "Installing Python dependencies")
    
    if not result:
        print("\nFailed to install Python dependencies.")
        return False
    
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        print("\nCreating .env file...")
        
        env_content = """# Azure Cosmos DB
COSMOS_ENDPOINT=https://careerbot-cosmos.documents.azure.com:443/
COSMOS_DATABASE=careerdb
COSMOS_CONTAINER=students

# Azure Language Service
LANGUAGE_ENDPOINT=https://career-bot-rg.cognitiveservices.azure.com/

# Azure Function App
AZURE_FUNCTION_URL=https://careerbot-functions.azurewebsites.net

# Azure Resource Group
RESOURCE_GROUP=career-bot-rg

# Flask App
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this-in-production

# Note: You'll need to add your COSMOS_KEY and LANGUAGE_KEY
# These are sensitive values that should be obtained from the Azure Portal
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("Created .env file. Please update it with your API keys.")
    else:
        print("\n.env file already exists.")

def main():
    """Main function to install dependencies"""
    print("=== Installing dependencies for Career Guidance Chatbot ===\n")
    
    # Install Python packages
    if not install_python_packages():
        return
    
    # Create .env file
    create_env_file()
    
    print("\n=== Dependencies installation completed! ===")
    print("\nTo run the application:")
    print("1. Update the .env file with your API keys")
    print("2. Run: python app.py")

if __name__ == "__main__":
    main()
