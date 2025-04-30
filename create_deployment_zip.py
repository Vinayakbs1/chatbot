import os
import shutil
import zipfile
import webbrowser

def create_deployment_package():
    """Create a deployment package for Azure Functions"""
    print("Creating deployment package for Azure Functions...")
    
    # Create a temporary directory for the package
    if os.path.exists("deploy_package"):
        shutil.rmtree("deploy_package")
    
    os.makedirs("deploy_package")
    
    # Copy the necessary files
    print("Copying files...")
    
    # Copy the shared directory
    shutil.copytree("azure_functions/shared", "deploy_package/shared")
    
    # Copy the simple_predict function
    shutil.copytree("azure_functions/simple_predict", "deploy_package/simple_predict")
    
    # Copy the get_career_details function
    shutil.copytree("azure_functions/get_career_details", "deploy_package/get_career_details")
    
    # Copy the predict_career function if it exists
    if os.path.exists("azure_functions/predict_career"):
        shutil.copytree("azure_functions/predict_career", "deploy_package/predict_career")
    
    # Copy the recommend_skills function if it exists
    if os.path.exists("azure_functions/recommend_skills"):
        shutil.copytree("azure_functions/recommend_skills", "deploy_package/recommend_skills")
    
    # Copy the host.json file
    shutil.copy("azure_functions/host.json", "deploy_package/host.json")
    
    # Copy the local.settings.json file
    shutil.copy("azure_functions/local.settings.json", "deploy_package/local.settings.json")
    
    # Copy the data directory
    if os.path.exists("azure_functions/data"):
        shutil.copytree("azure_functions/data", "deploy_package/data")
    
    # Copy the models directory
    if os.path.exists("azure_functions/models"):
        shutil.copytree("azure_functions/models", "deploy_package/models")
    
    # Create a zip file
    print("Creating zip file...")
    with zipfile.ZipFile("azure_functions_updated.zip", "w") as zipf:
        for root, dirs, files in os.walk("deploy_package"):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, "deploy_package")
                zipf.write(file_path, arcname)
    
    print("Deployment package created: azure_functions_updated.zip")
    
    # Open the Azure Portal
    print("Opening Azure Portal...")
    webbrowser.open("https://portal.azure.com/#blade/WebsitesExtension/FunctionsIFrameBlade")
    
    print("\nInstructions to deploy the package:")
    print("1. Log in to the Azure Portal")
    print("2. Navigate to your Function App (careerbot-functions)")
    print("3. Click on 'Advanced Tools' (Kudu)")
    print("4. Click on 'Go' to open Kudu")
    print("5. Click on 'Debug console' and select 'CMD'")
    print("6. Navigate to 'site/wwwroot'")
    print("7. Delete all existing files (you can use the trash icon)")
    print("8. Upload the 'azure_functions_updated.zip' file")
    print("9. Extract the zip file using the command: 'unzip azure_functions_updated.zip'")
    print("10. Restart your Function App")

if __name__ == "__main__":
    create_deployment_package()
