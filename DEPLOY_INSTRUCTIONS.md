# Azure Functions Deployment Instructions

This guide will help you deploy the Azure Functions for your Career Guidance Chatbot.

## Prerequisites

- Azure CLI installed and configured
- Azure Functions Core Tools installed (optional)

## Option 1: Deploy Using Azure Portal

1. **Prepare the Functions**
   - The `azure_functions` directory has been created with all the necessary files
   - Zip the contents of the `azure_functions` directory (not the directory itself)
   - You can use the `function_deploy.zip` file that was created

2. **Deploy Using Azure Portal**
   - Go to the [Azure Portal](https://portal.azure.com)
   - Navigate to your Function App (`careerbot-functions`)
   - Click on "Deployment Center" in the left sidebar
   - Select "External" as the source
   - Click "Continue"
   - Click "Upload" and select the `function_deploy.zip` file
   - Click "Deploy"

3. **Configure Application Settings**
   - In the Azure Portal, navigate to your Function App
   - Click on "Configuration" in the left sidebar
   - Add the following application settings:
     - `COSMOS_ENDPOINT`: https://careerbot-cosmos.documents.azure.com:443/
     - `COSMOS_KEY`: Your Cosmos DB key
     - `COSMOS_DATABASE`: careerdb
     - `COSMOS_CONTAINER`: students
     - `LANGUAGE_ENDPOINT`: https://career-bot-rg.cognitiveservices.azure.com/
     - `LANGUAGE_KEY`: Your Language Service key
   - Click "Save"

## Option 2: Deploy Using Azure CLI

If you have Azure CLI installed, you can use the following commands:

```bash
# Login to Azure
az login

# Deploy the functions
az functionapp deployment source config-zip --resource-group career-bot-rg --name careerbot-functions --src function_deploy.zip

# Configure application settings
az functionapp config appsettings set --resource-group career-bot-rg --name careerbot-functions --settings "COSMOS_ENDPOINT=https://careerbot-cosmos.documents.azure.com:443/" "COSMOS_KEY=your-cosmos-key" "COSMOS_DATABASE=careerdb" "COSMOS_CONTAINER=students" "LANGUAGE_ENDPOINT=https://career-bot-rg.cognitiveservices.azure.com/" "LANGUAGE_KEY=your-language-key"
```

## Option 3: Deploy Using Azure Functions Core Tools

If you have Azure Functions Core Tools installed, you can use the following commands:

```bash
# Navigate to the azure_functions directory
cd azure_functions

# Deploy the functions
func azure functionapp publish careerbot-functions
```

## Verifying the Deployment

1. Go to the Azure Portal
2. Navigate to your Function App
3. Click on "Functions" in the left sidebar
4. You should see the following functions:
   - `predict_career`
   - `get_career_details`
   - `recommend_skills`
5. Click on each function to verify it was deployed correctly

## Testing the Functions

You can test the functions using the following URLs:

- `predict_career`: https://careerbot-functions.azurewebsites.net/api/predict_career
- `get_career_details`: https://careerbot-functions.azurewebsites.net/api/get_career_details?career=Data%20Scientist
- `recommend_skills`: https://careerbot-functions.azurewebsites.net/api/recommend_skills

## Troubleshooting

If you encounter any issues:

1. Check the function logs in the Azure Portal
2. Make sure the application settings are configured correctly
3. Verify that the Cosmos DB and Language Service are accessible from the Function App

## Next Steps

After deploying the functions, you can run your application with Azure Functions integration:

```bash
python app.py
```

The application will use the Azure Functions for career prediction, career details, and skill recommendations.
