# Using Existing Azure Resources for Career Guidance Chatbot

This guide provides instructions for deploying the Career Guidance Chatbot to your existing Azure resources.

## Your Existing Resources

Based on your Azure account, you have the following resources:

1. `careerbot-functions` - Function App
2. `ASP-careerbotg-b509` - App Service Plan
3. `careerchatbotstorage` - Storage Account
4. `career-bot-rg` - Resource Group
5. `careerbot-cosmos` - Azure Cosmos DB Account
6. `career-bot-rg` - Language Service (likely for LUIS)

## Prerequisites

1. **Azure CLI**: Install the Azure CLI from [here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
2. **Python 3.9+**: Make sure you have Python 3.9 or higher installed
3. **Git**: Install Git for version control

## Step 1: Prepare Your Local Environment

1. Make sure you have run the data preprocessing and model training:
   ```
   python data_preprocessing.py
   python model_training.py
   ```

2. Log in to Azure CLI:
   ```
   az login
   ```

## Step 2: Get Cosmos DB Keys

You need to get your Cosmos DB primary key to connect to your database:

1. Go to the Azure Portal
2. Navigate to your Cosmos DB account (`careerbot-cosmos`)
3. In the left menu, under "Settings", click on "Keys"
4. Copy the "Primary Key" value
5. Add it to your `.env` file:
   ```
   COSMOS_KEY=your-primary-key
   ```

## Step 3: Set Up LUIS (Language Understanding)

If you haven't already set up LUIS:

1. Go to [LUIS Portal](https://www.luis.ai/)
2. Sign in with your Azure account
3. Create a new app following the instructions in `luis_setup.md`
4. After publishing your app, get the following values:
   - LUIS App ID
   - LUIS Endpoint
   - LUIS API Key
5. Add these values to your `.env` file:
   ```
   LUIS_APP_ID=your-app-id
   LUIS_ENDPOINT=your-endpoint
   LUIS_API_KEY=your-api-key
   ```

## Step 4: Deploy to Your Existing Resources

Use the deployment script to deploy to your existing resources:

```
python deploy_to_existing.py
```

This script will:
1. Set up the Cosmos DB database and container
2. Deploy the Azure Functions to your existing Function App
3. Create a web app (if it doesn't exist) and deploy the Flask application

You can skip specific steps if needed:
- `--skip-cosmos`: Skip Cosmos DB setup
- `--skip-functions`: Skip Function App deployment
- `--skip-webapp`: Skip Web App deployment

Example:
```
python deploy_to_existing.py --skip-cosmos
```

## Step 5: Test Your Application

1. After deployment, you'll get a URL for your web app
2. Open this URL in your browser
3. Test the chatbot by entering your skills and checking the career recommendations

## Troubleshooting

### Common Issues

1. **Deployment Failures**: If deployment fails, check the Azure CLI output for specific error messages.

2. **Connection Issues**: If the web app cannot connect to Cosmos DB or LUIS, verify that the environment variables are correctly set in the Azure Portal.

3. **Function App Errors**: Check the Function App logs in the Azure Portal for any errors.

### Checking Logs

1. **Function App Logs**:
   ```
   az functionapp log tail --name careerbot-functions --resource-group career-bot-rg
   ```

2. **Web App Logs**:
   ```
   az webapp log tail --name careerbot-webapp --resource-group career-bot-rg
   ```

## Additional Resources

- [Azure Functions Documentation](https://docs.microsoft.com/en-us/azure/azure-functions/)
- [Azure Cosmos DB Documentation](https://docs.microsoft.com/en-us/azure/cosmos-db/)
- [LUIS Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/luis/)
- [Azure Web Apps Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
