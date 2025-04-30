# Azure Functions Automated Deployment Script
# This script automates the deployment of Azure Functions using the Azure App Service extension

# Configuration
$functionAppName = "careerbot-functions"  # Change this to your function app name
$resourceGroup = "career-bot-rg"          # Change this to your resource group name

Write-Host "=== Azure Functions Automated Deployment ===" -ForegroundColor Cyan

# Check if Azure CLI is installed
Write-Host "Checking if Azure CLI is installed..." -ForegroundColor Yellow
try {
    $azVersion = az --version
    Write-Host "Azure CLI is installed." -ForegroundColor Green
} catch {
    Write-Host "Azure CLI is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Azure CLI from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Red
    exit 1
}

# Check if Azure Functions Core Tools is installed
Write-Host "Checking if Azure Functions Core Tools is installed..." -ForegroundColor Yellow
try {
    $funcVersion = func --version
    Write-Host "Azure Functions Core Tools is installed: $funcVersion" -ForegroundColor Green
} catch {
    Write-Host "Azure Functions Core Tools is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Azure Functions Core Tools from: https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local" -ForegroundColor Red
    exit 1
}

# Check if logged in to Azure
Write-Host "Checking if logged in to Azure..." -ForegroundColor Yellow
$account = az account show --query name -o tsv 2>$null
if (-not $account) {
    Write-Host "Not logged in to Azure. Please log in." -ForegroundColor Yellow
    az login
    $account = az account show --query name -o tsv
    if (-not $account) {
        Write-Host "Failed to log in to Azure." -ForegroundColor Red
        exit 1
    }
}
Write-Host "Logged in as: $account" -ForegroundColor Green

# Check if function app exists
Write-Host "Checking if function app '$functionAppName' exists..." -ForegroundColor Yellow
$functionApp = az functionapp show --name $functionAppName --resource-group $resourceGroup --query name -o tsv 2>$null
if (-not $functionApp) {
    Write-Host "Function app '$functionAppName' does not exist in resource group '$resourceGroup'." -ForegroundColor Red
    Write-Host "Please create the function app first or update the script with the correct function app name and resource group." -ForegroundColor Red
    exit 1
}
Write-Host "Function app '$functionAppName' exists." -ForegroundColor Green

# Deploy the functions
Write-Host "Deploying Azure Functions to '$functionAppName'..." -ForegroundColor Yellow

# Navigate to the azure_functions directory
Set-Location -Path "azure_functions"

# Deploy to Azure Functions
func azure functionapp publish $functionAppName --force

# Return to the original directory
Set-Location -Path ".."

# Verify deployment
Write-Host "Verifying deployment..." -ForegroundColor Yellow
$functionAppUrl = az functionapp show --name $functionAppName --resource-group $resourceGroup --query defaultHostName -o tsv
if ($functionAppUrl) {
    Write-Host "Deployment successful!" -ForegroundColor Green
    Write-Host "Function App URL: https://$functionAppUrl" -ForegroundColor Cyan
    
    # List functions
    Write-Host "Functions deployed:" -ForegroundColor Cyan
    $functions = az functionapp function list --name $functionAppName --resource-group $resourceGroup --query "[].name" -o tsv
    foreach ($function in $functions) {
        Write-Host "- $function" -ForegroundColor White
    }
} else {
    Write-Host "Failed to verify deployment." -ForegroundColor Red
}

Write-Host "=== Deployment process completed ===" -ForegroundColor Cyan
