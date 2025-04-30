@echo off
echo Uploading data files to Azure Functions...

rem Create data directory in azure_functions if it doesn't exist
if not exist "azure_functions\data" mkdir "azure_functions\data"

rem Copy preprocessed_career_data.csv to azure_functions\data
if exist "preprocessed_career_data.csv" (
    copy "preprocessed_career_data.csv" "azure_functions\data\"
    echo Copied preprocessed_career_data.csv to azure_functions\data\
)

rem Create models directory in azure_functions if it doesn't exist
if not exist "azure_functions\models" mkdir "azure_functions\models"

rem Copy model files to azure_functions\models
if exist "models" (
    copy "models\*.pkl" "azure_functions\models\"
    echo Copied model files to azure_functions\models\
)

rem Navigate to the azure_functions directory
cd azure_functions

rem Deploy to Azure Functions
echo Publishing to careerbot-functions...
func azure functionapp publish careerbot-functions

rem Return to the original directory
cd ..

echo Deployment completed!
pause
