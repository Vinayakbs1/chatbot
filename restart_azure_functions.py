import os
import subprocess
import sys
import time

def restart_azure_functions():
    """Restart Azure Functions to apply changes"""
    print("Restarting Azure Functions...")
    
    # Check if Azure CLI is installed
    try:
        subprocess.run(["az", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Azure CLI is not installed or not in PATH. Please install it first.")
        return False
    
    # Check if user is logged in
    try:
        result = subprocess.run(["az", "account", "show"], check=True, capture_output=True, text=True)
        print("Already logged in to Azure.")
    except subprocess.CalledProcessError:
        print("Not logged in to Azure. Please log in.")
        subprocess.run(["az", "login"], check=True)
    
    # Get function app name from environment or use default
    function_app_name = os.environ.get("FUNCTION_APP_NAME", "careerbot-functions")
    resource_group = os.environ.get("RESOURCE_GROUP", "career-bot-rg")
    
    print(f"Restarting function app: {function_app_name} in resource group: {resource_group}")
    
    try:
        # Restart the function app
        subprocess.run(["az", "functionapp", "restart", "--name", function_app_name, 
                       "--resource-group", resource_group], check=True)
        
        print(f"Successfully restarted {function_app_name}.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error restarting function app: {e}")
        return False

if __name__ == "__main__":
    restart_azure_functions()
