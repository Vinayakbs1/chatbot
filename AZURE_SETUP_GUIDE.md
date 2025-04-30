# Azure Setup Guide for Career Guidance Chatbot

This guide will help you set up the necessary Azure resources and API keys for your Career Guidance Chatbot.

## Prerequisites

- An Azure account with the following resources already created:
  - Azure Cosmos DB account (`careerbot-cosmos`)
  - Azure Language Service (`career-bot-rg`)
  - Azure Function App (`careerbot-functions`)
  - Azure Storage Account (`careerchatbotstorage`)

## Step 1: Get Azure Cosmos DB Key

1. Go to the [Azure Portal](https://portal.azure.com)
2. Navigate to your Cosmos DB account (`careerbot-cosmos`)
3. In the left sidebar, under "Settings", click on "Keys"
4. Copy the "PRIMARY KEY" value
5. Open the `.env` file in your project
6. Replace `your-cosmos-key` with the copied key

## Step 2: Get Azure Language Service Key

1. Go to the [Azure Portal](https://portal.azure.com)
2. Navigate to your Language Service (`career-bot-rg`)
3. In the left sidebar, under "Resource Management", click on "Keys and Endpoint"
4. Copy "KEY 1" value
5. Open the `.env` file in your project
6. Replace `your-language-key` with the copied key

## Step 3: Create Cosmos DB Database and Container

1. Go to the [Azure Portal](https://portal.azure.com)
2. Navigate to your Cosmos DB account (`careerbot-cosmos`)
3. In the left sidebar, click on "Data Explorer"
4. Click "New Container" at the top
5. For "Database id", enter `careerdb` (create new)
6. For "Container id", enter `students`
7. For "Partition key", enter `/userId`
8. Click "OK" to create the database and container

## Step 4: Test Your Setup

1. Open a command prompt or terminal
2. Navigate to your project directory
3. Run the application:
   ```
   python app.py
   ```
4. Open your browser and go to http://localhost:5000
5. Test the chatbot by entering some skills

## Troubleshooting

If you encounter any issues:

1. **Cosmos DB Connection Error**: Make sure your Cosmos DB key is correct and the database and container exist.
2. **Language Service Error**: Make sure your Language Service key is correct.
3. **Azure Functions Error**: The application will fall back to local processing if Azure Functions are not available.

## Next Steps

If you want to deploy Azure Functions:

1. Install Azure Functions Core Tools:
   ```
   npm install -g azure-functions-core-tools@4
   ```

2. Create and deploy your functions:
   ```
   func init azure_functions --worker-runtime python
   cd azure_functions
   func new --name predict_career --template "HTTP trigger"
   func new --name get_career_details --template "HTTP trigger"
   func new --name recommend_skills --template "HTTP trigger"
   func azure functionapp publish careerbot-functions
   ```

For more detailed instructions, refer to the [Azure Functions documentation](https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-first-function-vs-code?pivots=programming-language-python).
