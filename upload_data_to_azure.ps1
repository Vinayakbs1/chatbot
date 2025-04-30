# Upload data files to Azure Functions
Write-Host "Uploading data files to Azure Functions..." -ForegroundColor Green

# Create data directory in azure_functions if it doesn't exist
if (-not (Test-Path -Path "azure_functions\data")) {
    New-Item -Path "azure_functions\data" -ItemType Directory
}

# Copy preprocessed_career_data.csv to azure_functions\data
if (Test-Path -Path "preprocessed_career_data.csv") {
    Copy-Item -Path "preprocessed_career_data.csv" -Destination "azure_functions\data\"
    Write-Host "Copied preprocessed_career_data.csv to azure_functions\data\" -ForegroundColor Yellow
}

# Create models directory in azure_functions if it doesn't exist
if (-not (Test-Path -Path "azure_functions\models")) {
    New-Item -Path "azure_functions\models" -ItemType Directory
}

# Copy model files to azure_functions\models
if (Test-Path -Path "models") {
    Copy-Item -Path "models\*.pkl" -Destination "azure_functions\models\"
    Write-Host "Copied model files to azure_functions\models\" -ForegroundColor Yellow
}

# Navigate to the azure_functions directory
Set-Location -Path "azure_functions"

# Deploy to Azure Functions
Write-Host "Publishing to careerbot-functions..." -ForegroundColor Yellow
func azure functionapp publish careerbot-functions

# Return to the original directory
Set-Location -Path ".."

Write-Host "Deployment completed!" -ForegroundColor Green
