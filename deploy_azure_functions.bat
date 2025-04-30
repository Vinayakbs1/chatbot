@echo off
echo === Azure Functions Automated Deployment ===

rem Configuration
set functionAppName=careerbot-functions
set resourceGroup=career-bot-rg

echo Checking if Azure CLI is installed...
where az >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Azure CLI is not installed or not in PATH.
    echo Please install Azure CLI from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
    pause
    exit /b 1
)
echo Azure CLI is installed.

echo Checking if Azure Functions Core Tools is installed...
where func >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Azure Functions Core Tools is not installed or not in PATH.
    echo Please install Azure Functions Core Tools from: https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('func --version') do set funcVersion=%%i
echo Azure Functions Core Tools is installed: %funcVersion%

echo Checking if logged in to Azure...
az account show --query name -o tsv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Not logged in to Azure. Please log in.
    az login
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to log in to Azure.
        pause
        exit /b 1
    )
)
for /f "tokens=*" %%i in ('az account show --query name -o tsv') do set account=%%i
echo Logged in as: %account%

echo Checking if function app '%functionAppName%' exists...
az functionapp show --name %functionAppName% --resource-group %resourceGroup% --query name -o tsv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Function app '%functionAppName%' does not exist in resource group '%resourceGroup%'.
    echo Please create the function app first or update the script with the correct function app name and resource group.
    pause
    exit /b 1
)
echo Function app '%functionAppName%' exists.

echo Deploying Azure Functions to '%functionAppName%'...

rem Navigate to the azure_functions directory
cd azure_functions

rem Deploy to Azure Functions
func azure functionapp publish %functionAppName% --force

rem Return to the original directory
cd ..

echo Verifying deployment...
for /f "tokens=*" %%i in ('az functionapp show --name %functionAppName% --resource-group %resourceGroup% --query defaultHostName -o tsv') do set functionAppUrl=%%i
if defined functionAppUrl (
    echo Deployment successful!
    echo Function App URL: https://%functionAppUrl%
    
    echo Functions deployed:
    az functionapp function list --name %functionAppName% --resource-group %resourceGroup% --query "[].name" -o tsv
) else (
    echo Failed to verify deployment.
)

echo === Deployment process completed ===
pause
