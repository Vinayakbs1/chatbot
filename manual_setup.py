import os
import sys

def main():
    """Main function to manually set up Azure keys"""
    print("=== Manual Setup for Career Guidance Chatbot ===\n")
    
    print("This script will help you manually set up your Azure keys.")
    print("You'll need to get these keys from the Azure Portal.\n")
    
    # Get Cosmos DB key
    print("Please enter your Cosmos DB Primary Key:")
    print("(You can find this in the Azure Portal under your Cosmos DB account > Keys)")
    cosmos_key = input("> ").strip()
    
    if not cosmos_key:
        print("No Cosmos DB key provided. Using placeholder value.")
        cosmos_key = "your-cosmos-key"
    
    # Get Language Service key
    print("\nPlease enter your Language Service Key:")
    print("(You can find this in the Azure Portal under your Language Service > Keys and Endpoint)")
    language_key = input("> ").strip()
    
    if not language_key:
        print("No Language Service key provided. Using placeholder value.")
        language_key = "your-language-key"
    
    # Get Function App URL
    print("\nPlease enter your Function App URL (optional):")
    print("(You can find this in the Azure Portal under your Function App > Overview)")
    function_url = input("> ").strip()
    
    if not function_url:
        print("No Function App URL provided. Using placeholder value.")
        function_url = "https://careerbot-functions.azurewebsites.net"
    
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
    
    print("Updated .env file with your Azure keys and settings.")
    
    # Install required packages
    print("\nWould you like to install the required Python packages? (y/n)")
    install_packages = input("> ").strip().lower()
    
    if install_packages == 'y':
        print("\nInstalling required Python packages...")
        os.system("pip install azure-cosmos azure-functions python-dotenv requests azure-storage-blob azure-ai-textanalytics")
    
    print("\n=== Setup completed! ===")
    
    # Run the application
    print("\nWould you like to run the application now? (y/n)")
    run_app = input("> ").strip().lower()
    
    if run_app == 'y':
        print("\nRunning the application...")
        print("The application will be available at http://localhost:5000")
        print("Press Ctrl+C to stop the application.")
        
        os.system("python app.py")
    else:
        print("\nSkipping application startup.")
        print("You can run the application later with: python app.py")

if __name__ == "__main__":
    main()
