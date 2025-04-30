@echo off
echo === Running Azure Setup Script ===

REM Check if Azure CLI is installed
where az >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Azure CLI is not installed or not in PATH.
    echo Please install Azure CLI from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
    echo After installation, you may need to restart your computer.
    pause
    exit /b
)

REM Run the Python script
python azure_setup_automated.py

pause
