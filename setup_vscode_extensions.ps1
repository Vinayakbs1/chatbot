# Setup VS Code Extensions for Azure Functions Development
Write-Host "Setting up VS Code extensions for Azure Functions development..." -ForegroundColor Cyan

# Check if VS Code is installed
Write-Host "Checking if VS Code is installed..." -ForegroundColor Yellow
try {
    $vsCodeVersion = code --version
    Write-Host "VS Code is installed." -ForegroundColor Green
} catch {
    Write-Host "VS Code is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install VS Code from: https://code.visualstudio.com/" -ForegroundColor Red
    exit 1
}

# Install required extensions
Write-Host "Installing required VS Code extensions..." -ForegroundColor Yellow

# Azure Functions extension
Write-Host "Installing Azure Functions extension..." -ForegroundColor Yellow
code --install-extension ms-azuretools.vscode-azurefunctions

# Azure Account extension
Write-Host "Installing Azure Account extension..." -ForegroundColor Yellow
code --install-extension ms-vscode.azure-account

# Azure Resources extension
Write-Host "Installing Azure Resources extension..." -ForegroundColor Yellow
code --install-extension ms-azuretools.vscode-azureresourcegroups

# Python extension
Write-Host "Installing Python extension..." -ForegroundColor Yellow
code --install-extension ms-python.python

Write-Host "VS Code extensions installed successfully!" -ForegroundColor Green
Write-Host "Please restart VS Code to activate the extensions." -ForegroundColor Cyan
