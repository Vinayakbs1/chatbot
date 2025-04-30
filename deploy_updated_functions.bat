@echo off
echo Deploying updated Azure Functions...

rem Navigate to the azure_functions directory
cd azure_functions

rem Deploy to Azure Functions
echo Publishing to careerbot-functions...
func azure functionapp publish careerbot-functions --force

rem Return to the original directory
cd ..

echo Deployment completed!
pause
