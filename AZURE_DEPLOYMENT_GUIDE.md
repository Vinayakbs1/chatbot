# Azure Deployment Guide for Career Guidance Chatbot

This guide provides step-by-step instructions for deploying the Career Guidance Chatbot to Azure using your student account.

## Prerequisites

1. **Azure Student Account**: Make sure your student account is set up and activated
2. **Azure CLI**: Install the Azure CLI from [here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
3. **Python 3.9+**: Make sure you have Python 3.9 or higher installed
4. **Git**: Install Git for version control

## Step 1: Clone and Set Up the Project

1. Clone the repository (if you haven't already):
   ```
   git clone <repository-url>
   cd chatbot
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the data preprocessing and model training:
   ```
   python data_preprocessing.py
   python model_training.py
   ```

## Step 2: Create Azure Resources

You can create Azure resources either through the Azure Portal or using our deployment script.

### Option 1: Using the Deployment Script

1. Log in to Azure CLI:
   ```
   az login
   ```

2. Run the deployment script:
   ```
   python deploy_to_azure.py
   ```

   This script will create:
   - Resource Group
   - Cosmos DB account, database, and container
   - LUIS resource
   - Azure Function App
   - Azure Web App

3. The script will output connection details and update the `.env` file with the necessary values.

### Option 2: Manual Setup through Azure Portal

Follow the instructions in `azure_setup.md` to manually create the required resources through the Azure Portal.

## Step 3: Set Up Azure Language Understanding (LUIS)

1. Follow the instructions in `luis_setup.md` to create a LUIS app.

2. After creating and publishing your LUIS app, update the `.env` file with your LUIS App ID:
   ```
   LUIS_APP_ID=your-app-id
   ```

## Step 4: Deploy Azure Functions

1. Deploy the Azure Functions using the deployment script:
   ```
   python deploy_functions.py --skip-webapp
   ```

2. Verify that the functions are deployed correctly by checking the Azure Portal.

## Step 5: Deploy the Web App

1. Deploy the Flask web app using the deployment script:
   ```
   python deploy_functions.py --skip-functions
   ```

2. Verify that the web app is deployed correctly by visiting the web app URL.

## Step 6: Test the Application

1. Open the web app URL in your browser.

2. Test the chatbot by entering your skills and checking the career recommendations.

3. Verify that all Azure services are working correctly:
   - LUIS for intent recognition
   - Azure Functions for backend processing
   - Cosmos DB for data storage

## Troubleshooting

### Common Issues

1. **CORS Errors**: If you encounter CORS errors when calling Azure Functions from the web app, you may need to configure CORS settings for your Function App:
   ```
   az functionapp cors add --name <function-app-name> --resource-group <resource-group> --allowed-origins <web-app-url>
   ```

2. **Connection Issues**: If the web app cannot connect to Cosmos DB or LUIS, check the environment variables in the Azure Portal.

3. **Function App Errors**: Check the Function App logs in the Azure Portal for any errors.

### Checking Logs

1. **Function App Logs**:
   ```
   az functionapp log tail --name <function-app-name> --resource-group <resource-group>
   ```

2. **Web App Logs**:
   ```
   az webapp log tail --name <web-app-name> --resource-group <resource-group>
   ```

## Cost Management

As a student, you're using free tiers for most services, but it's good to monitor usage:

1. **Cosmos DB**: Free tier includes 25GB of storage
2. **LUIS**: Free tier includes 10,000 transactions per month
3. **Azure Functions**: Free tier includes 1 million executions per month
4. **Web App**: Free tier has limitations on compute resources

Monitor your usage in the Azure Portal to avoid unexpected charges.

## Cleaning Up

When you're done with the project, you can delete all resources to avoid any charges:

```
az group delete --name <resource-group> --yes --no-wait
```

## Additional Resources

- [Azure for Students](https://azure.microsoft.com/en-us/free/students/)
- [Azure Functions Documentation](https://docs.microsoft.com/en-us/azure/azure-functions/)
- [Azure Cosmos DB Documentation](https://docs.microsoft.com/en-us/azure/cosmos-db/)
- [LUIS Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/luis/)
- [Azure Web Apps Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
