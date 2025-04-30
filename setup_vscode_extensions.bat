@echo off
echo Setting up VS Code extensions for Azure Functions development...

echo Checking if VS Code is installed...
where code >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo VS Code is not installed or not in PATH.
    echo Please install VS Code from: https://code.visualstudio.com/
    pause
    exit /b 1
)
echo VS Code is installed.

echo Installing required VS Code extensions...

echo Installing Azure Functions extension...
call code --install-extension ms-azuretools.vscode-azurefunctions

echo Installing Azure Account extension...
call code --install-extension ms-vscode.azure-account

echo Installing Azure Resources extension...
call code --install-extension ms-azuretools.vscode-azureresourcegroups

echo Installing Python extension...
call code --install-extension ms-python.python

echo VS Code extensions installed successfully!
echo Please restart VS Code to activate the extensions.
pause
