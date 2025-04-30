import os
import shutil
import subprocess
import sys

def deploy_updated_functions():
    """Deploy updated Azure Functions"""
    print("=== Deploying updated Azure Functions ===")
    
    # Check if Azure Functions Core Tools is installed
    try:
        subprocess.run(["func", "--version"], check=True, capture_output=True)
        print("Azure Functions Core Tools is installed.")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Azure Functions Core Tools is not installed or not in PATH.")
        print("Please install it using: npm install -g azure-functions-core-tools@4")
        return False
    
    # Change to the azure_functions directory
    os.chdir("azure_functions")
    
    # Deploy the functions
    try:
        print("Deploying functions to Azure...")
        result = subprocess.run(["func", "azure", "functionapp", "publish", "careerbot-functions"], 
                               check=True, capture_output=True, text=True)
        
        print(result.stdout)
        
        if "Deployment successful" in result.stdout:
            print("Functions deployed successfully!")
            return True
        else:
            print("Deployment may have failed. Check the output above.")
            return False
    
    except subprocess.CalledProcessError as e:
        print(f"Error deploying functions: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False
    finally:
        # Change back to the original directory
        os.chdir("..")

if __name__ == "__main__":
    deploy_updated_functions()
