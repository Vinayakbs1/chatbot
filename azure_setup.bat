@echo off
echo === Automated Azure Setup for Career Guidance Chatbot ===
echo.

echo Checking if Azure CLI is installed...
where az >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Azure CLI is not installed or not in PATH.
    echo Please install Azure CLI from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
    echo After installation, you may need to restart your computer.
    pause
    exit /b
)

echo.
echo Getting Cosmos DB key...
for /f "tokens=*" %%a in ('az cosmosdb keys list --name careerbot-cosmos --resource-group career-bot-rg --query primaryMasterKey -o tsv 2^>nul') do set COSMOS_KEY=%%a

if "%COSMOS_KEY%"=="" (
    echo Failed to get Cosmos DB key. Check if the resource exists and you have access to it.
) else (
    echo Successfully retrieved Cosmos DB key.
)

echo.
echo Getting Language Service key...
for /f "tokens=*" %%a in ('az cognitiveservices account keys list --name career-bot-rg --resource-group career-bot-rg --query key1 -o tsv 2^>nul') do set LANGUAGE_KEY=%%a

if "%LANGUAGE_KEY%"=="" (
    echo Failed to get Language Service key. Check if the resource exists and you have access to it.
) else (
    echo Successfully retrieved Language Service key.
)

echo.
echo Getting Function App URL...
for /f "tokens=*" %%a in ('az functionapp show --name careerbot-functions --resource-group career-bot-rg --query defaultHostName -o tsv 2^>nul') do set FUNCTION_HOST=%%a

if "%FUNCTION_HOST%"=="" (
    echo Failed to get Function App URL. Check if the resource exists and you have access to it.
    set FUNCTION_URL=
) else (
    set FUNCTION_URL=https://%FUNCTION_HOST%
    echo Successfully retrieved Function App URL: %FUNCTION_URL%
)

echo.
echo Checking if Cosmos DB database exists...
az cosmosdb sql database show --name careerdb --account-name careerbot-cosmos --resource-group career-bot-rg --query id -o tsv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Database 'careerdb' does not exist. Creating...
    az cosmosdb sql database create --name careerdb --account-name careerbot-cosmos --resource-group career-bot-rg >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create database.
    ) else (
        echo Database 'careerdb' created successfully.
    )
) else (
    echo Database 'careerdb' already exists.
)

echo.
echo Checking if Cosmos DB container exists...
az cosmosdb sql container show --name students --database-name careerdb --account-name careerbot-cosmos --resource-group career-bot-rg --query id -o tsv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Container 'students' does not exist. Creating...
    az cosmosdb sql container create --name students --database-name careerdb --account-name careerbot-cosmos --resource-group career-bot-rg --partition-key-path "/userId" >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to create container.
    ) else (
        echo Container 'students' created successfully.
    )
) else (
    echo Container 'students' already exists.
)

echo.
echo Updating .env file...

echo # Azure Cosmos DB > .env
echo COSMOS_ENDPOINT=https://careerbot-cosmos.documents.azure.com:443/ >> .env
echo COSMOS_KEY=%COSMOS_KEY% >> .env
echo COSMOS_DATABASE=careerdb >> .env
echo COSMOS_CONTAINER=students >> .env
echo. >> .env
echo # Azure Language Service >> .env
echo LANGUAGE_ENDPOINT=https://career-bot-rg.cognitiveservices.azure.com/ >> .env
echo LANGUAGE_KEY=%LANGUAGE_KEY% >> .env
echo. >> .env
echo # Azure Function App >> .env
echo AZURE_FUNCTION_URL=%FUNCTION_URL% >> .env
echo. >> .env
echo # Azure Resource Group >> .env
echo RESOURCE_GROUP=career-bot-rg >> .env
echo. >> .env
echo # Flask App >> .env
echo FLASK_APP=app.py >> .env
echo FLASK_ENV=development >> .env
echo SECRET_KEY=your-secret-key-change-this-in-production >> .env

echo Updated .env file with Azure keys and settings.

echo.
echo Installing required Python packages...
pip install azure-cosmos azure-functions python-dotenv requests azure-storage-blob azure-ai-textanalytics

echo.
echo === Azure setup completed! ===

echo.
set /p RUN_APP=Would you like to run the application now? (y/n): 

if /i "%RUN_APP%"=="y" (
    echo.
    echo Running the application...
    echo The application will be available at http://localhost:5000
    echo Press Ctrl+C to stop the application.
    
    python app.py
) else (
    echo.
    echo Skipping application startup.
    echo You can run the application later with: python app.py
)

pause
