# Azure Setup Script for Career Guidance Chatbot
Write-Host "=== Automated Azure Setup for Career Guidance Chatbot ===" -ForegroundColor Cyan

# Check if Azure CLI is installed
Write-Host "`nChecking if Azure CLI is installed..." -ForegroundColor Yellow
$azCliInstalled = $null -ne (Get-Command az -ErrorAction SilentlyContinue)

if (-not $azCliInstalled) {
    Write-Host "Azure CLI is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Azure CLI from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Red
    Write-Host "After installation, you may need to restart your computer." -ForegroundColor Red
    exit
}

# Check if logged in to Azure
Write-Host "`nChecking if logged in to Azure..." -ForegroundColor Yellow
$azAccount = az account show --query name -o tsv 2>$null

if (-not $azAccount) {
    Write-Host "Not logged in to Azure. Please run 'az login' first." -ForegroundColor Red
    exit
}

Write-Host "Logged in as: $azAccount" -ForegroundColor Green

# Get Cosmos DB key
Write-Host "`nGetting Cosmos DB key..." -ForegroundColor Yellow
$cosmosKey = az cosmosdb keys list --name careerbot-cosmos --resource-group career-bot-rg --query primaryMasterKey -o tsv 2>$null

if (-not $cosmosKey) {
    Write-Host "Failed to get Cosmos DB key. Check if the resource exists and you have access to it." -ForegroundColor Red
} else {
    Write-Host "Successfully retrieved Cosmos DB key." -ForegroundColor Green
}

# Get Language Service key
Write-Host "`nGetting Language Service key..." -ForegroundColor Yellow
$languageKey = az cognitiveservices account keys list --name career-bot-rg --resource-group career-bot-rg --query key1 -o tsv 2>$null

if (-not $languageKey) {
    Write-Host "Failed to get Language Service key. Check if the resource exists and you have access to it." -ForegroundColor Red
} else {
    Write-Host "Successfully retrieved Language Service key." -ForegroundColor Green
}

# Get Function App URL
Write-Host "`nGetting Function App URL..." -ForegroundColor Yellow
$functionHost = az functionapp show --name careerbot-functions --resource-group career-bot-rg --query defaultHostName -o tsv 2>$null

if (-not $functionHost) {
    Write-Host "Failed to get Function App URL. Check if the resource exists and you have access to it." -ForegroundColor Red
    $functionUrl = $null
} else {
    $functionUrl = "https://$functionHost"
    Write-Host "Successfully retrieved Function App URL: $functionUrl" -ForegroundColor Green
}

# Create Cosmos DB database if it doesn't exist
Write-Host "`nChecking if Cosmos DB database exists..." -ForegroundColor Yellow
$dbExists = az cosmosdb sql database show --name careerdb --account-name careerbot-cosmos --resource-group career-bot-rg --query id -o tsv 2>$null

if (-not $dbExists) {
    Write-Host "Database 'careerdb' does not exist. Creating..." -ForegroundColor Yellow
    $createDb = az cosmosdb sql database create --name careerdb --account-name careerbot-cosmos --resource-group career-bot-rg 2>$null
    
    if (-not $createDb) {
        Write-Host "Failed to create database." -ForegroundColor Red
    } else {
        Write-Host "Database 'careerdb' created successfully." -ForegroundColor Green
    }
} else {
    Write-Host "Database 'careerdb' already exists." -ForegroundColor Green
}

# Create Cosmos DB container if it doesn't exist
Write-Host "`nChecking if Cosmos DB container exists..." -ForegroundColor Yellow
$containerExists = az cosmosdb sql container show --name students --database-name careerdb --account-name careerbot-cosmos --resource-group career-bot-rg --query id -o tsv 2>$null

if (-not $containerExists) {
    Write-Host "Container 'students' does not exist. Creating..." -ForegroundColor Yellow
    $createContainer = az cosmosdb sql container create --name students --database-name careerdb --account-name careerbot-cosmos --resource-group career-bot-rg --partition-key-path "/userId" 2>$null
    
    if (-not $createContainer) {
        Write-Host "Failed to create container." -ForegroundColor Red
    } else {
        Write-Host "Container 'students' created successfully." -ForegroundColor Green
    }
} else {
    Write-Host "Container 'students' already exists." -ForegroundColor Green
}

# Update .env file
Write-Host "`nUpdating .env file..." -ForegroundColor Yellow

$envContent = @"
# Azure Cosmos DB
COSMOS_ENDPOINT=https://careerbot-cosmos.documents.azure.com:443/
COSMOS_KEY=$cosmosKey
COSMOS_DATABASE=careerdb
COSMOS_CONTAINER=students

# Azure Language Service
LANGUAGE_ENDPOINT=https://career-bot-rg.cognitiveservices.azure.com/
LANGUAGE_KEY=$languageKey

# Azure Function App
AZURE_FUNCTION_URL=$functionUrl

# Azure Resource Group
RESOURCE_GROUP=career-bot-rg

# Flask App
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this-in-production
"@

Set-Content -Path ".env" -Value $envContent

Write-Host "Updated .env file with Azure keys and settings." -ForegroundColor Green

# Install required Python packages
Write-Host "`nInstalling required Python packages..." -ForegroundColor Yellow
pip install azure-cosmos azure-functions python-dotenv requests azure-storage-blob azure-ai-textanalytics

Write-Host "`n=== Azure setup completed! ===" -ForegroundColor Cyan

# Ask to run the application
Write-Host "`nWould you like to run the application now? (y/n)" -ForegroundColor Yellow
$runApp = Read-Host

if ($runApp -eq "y") {
    Write-Host "`nRunning the application..." -ForegroundColor Green
    Write-Host "The application will be available at http://localhost:5000" -ForegroundColor Green
    Write-Host "Press Ctrl+C to stop the application." -ForegroundColor Yellow
    
    python app.py
} else {
    Write-Host "`nSkipping application startup." -ForegroundColor Yellow
    Write-Host "You can run the application later with: python app.py" -ForegroundColor Green
}
