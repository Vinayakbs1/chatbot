# Azure App Service Extension Guide

This guide explains how to use the Azure App Service extension in VS Code to deploy your Azure Functions.

## Installing the Azure App Service Extension

1. Run the provided setup script:
   - For PowerShell: `.\setup_vscode_extensions.ps1`
   - For Command Prompt: `setup_vscode_extensions.bat`

   Or manually install the extensions:
   - Open VS Code
   - Go to Extensions (Ctrl+Shift+X)
   - Search for "Azure Functions" and install
   - Search for "Azure Account" and install
   - Search for "Azure Resources" and install

2. Restart VS Code after installing the extensions

## Using the Azure App Service Extension

### Sign in to Azure

1. Click on the Azure icon in the VS Code Activity Bar (left side)
2. Click "Sign in to Azure..."
3. Follow the authentication process in your browser

### Deploy Using the Extension

1. Click on the Azure icon in the VS Code Activity Bar
2. Expand the "FUNCTIONS" section
3. Find your subscription and function app
4. Right-click on your function app and select "Deploy to Function App..."
5. Select the folder containing your functions (usually `azure_functions`)
6. Wait for the deployment to complete

### Monitor Your Functions

1. Expand your function app in the Azure Functions extension
2. Right-click on your function app and select "Start Streaming Logs"
3. View the logs in the output panel

### Test Your Functions

1. Expand your function app in the Azure Functions extension
2. Expand the "Functions" node to see your deployed functions
3. Right-click on a function and select "Execute Function Now..."
4. Enter the required parameters and click "Execute"

## Automating Deployment with the Extension

While the Azure App Service extension provides a GUI for deployment, you can also automate the process:

1. Use the provided deployment scripts:
   - `deploy_azure_functions.ps1` (PowerShell)
   - `deploy_azure_functions.bat` (Batch)

2. Use VS Code tasks:
   - Press `Ctrl+Shift+B` to run the default build task
   - Select "Deploy Azure Functions" from the task list

3. Use GitHub Actions for continuous deployment:
   - Push changes to your repository
   - GitHub Actions will automatically deploy your functions

## Troubleshooting

If you encounter issues with the Azure App Service extension:

1. **Authentication Issues**:
   - Sign out and sign in again to Azure
   - Check if your Azure subscription is active

2. **Deployment Failures**:
   - Check the Output panel in VS Code for error messages
   - Verify your function app settings in the Azure Portal

3. **Extension Not Working**:
   - Reload VS Code (Ctrl+Shift+P, then "Developer: Reload Window")
   - Reinstall the extension

## Additional Resources

- [Azure Functions Extension Documentation](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurefunctions)
- [Azure Functions in VS Code](https://docs.microsoft.com/en-us/azure/azure-functions/functions-develop-vs-code)
- [Azure App Service Extension Documentation](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azureappservice)
