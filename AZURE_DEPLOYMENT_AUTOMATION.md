# Azure Functions Deployment Automation

This guide explains how to use the automated deployment tools for Azure Functions in this project.

## Prerequisites

1. **Azure CLI**: Install from [here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
2. **Azure Functions Core Tools**: Install from [here](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local)
3. **Azure Account**: You need an active Azure account with a student plan
4. **VS Code with Azure Functions Extension**: Install the Azure Functions extension for VS Code

## Deployment Methods

There are several ways to deploy your Azure Functions:

### Method 1: Using the PowerShell Script

1. Open PowerShell
2. Navigate to your project directory
3. Run the deployment script:
   ```powershell
   .\deploy_azure_functions.ps1
   ```

This script will:
- Check if Azure CLI and Azure Functions Core Tools are installed
- Verify you're logged in to Azure
- Check if the function app exists
- Deploy your functions
- Verify the deployment

### Method 2: Using the Batch File

1. Open Command Prompt
2. Navigate to your project directory
3. Run the batch file:
   ```
   deploy_azure_functions.bat
   ```

This batch file performs the same steps as the PowerShell script.

### Method 3: Using VS Code Tasks

1. Open your project in VS Code
2. Press `Ctrl+Shift+B` to run the default build task
3. Select "Deploy Azure Functions" from the task list

This will run the PowerShell script in a VS Code terminal.

### Method 4: Using GitHub Actions (Continuous Deployment)

If you push your code to GitHub, you can set up continuous deployment:

1. Create a publish profile for your function app in the Azure Portal
2. Add the publish profile as a secret in your GitHub repository with the name `AZURE_FUNCTIONAPP_PUBLISH_PROFILE`
3. Push changes to the `main` branch
4. GitHub Actions will automatically deploy your functions

## Customizing the Deployment

To customize the deployment for your specific Azure resources:

1. Open `deploy_azure_functions.ps1` or `deploy_azure_functions.bat`
2. Update the following variables:
   - `functionAppName`: Your Azure Function App name
   - `resourceGroup`: Your Azure Resource Group name

3. If using GitHub Actions, update the `.github/workflows/azure-functions-deploy.yml` file:
   - Update the `AZURE_FUNCTIONAPP_NAME` environment variable

## Troubleshooting

If you encounter issues during deployment:

1. **Authentication Issues**: Run `az login` to log in to Azure
2. **Function App Not Found**: Verify the function app name and resource group
3. **Deployment Failures**: Check the Azure Functions logs in the Azure Portal
4. **Permission Issues**: Ensure you have the necessary permissions to deploy to the function app

## Additional Resources

- [Azure Functions Documentation](https://docs.microsoft.com/en-us/azure/azure-functions/)
- [Azure Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local)
- [GitHub Actions for Azure](https://docs.microsoft.com/en-us/azure/developer/github/github-actions)
