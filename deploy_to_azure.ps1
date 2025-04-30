# Deploy to Azure Functions script
Write-Host "Deploying to Azure Functions..." -ForegroundColor Green

# Navigate to the azure_functions directory
Set-Location -Path "azure_functions"

# Deploy to Azure Functions
Write-Host "Publishing to careerbot-functions..." -ForegroundColor Yellow
func azure functionapp publish careerbot-functions

# Return to the original directory
Set-Location -Path ".."

Write-Host "Deployment completed!" -ForegroundColor Green
