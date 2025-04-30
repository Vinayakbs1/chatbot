# Azure Setup Guide for Career Guidance Chatbot

## Prerequisites
- Azure Student Account (already set up)
- Azure CLI installed locally (optional, for command-line deployment)

## 1. Create Resource Group

All Azure resources should be organized in a resource group:

1. Sign in to the [Azure Portal](https://portal.azure.com)
2. Click on "Resource groups" in the left menu
3. Click "Create" to create a new resource group
4. Name it "career-guidance-chatbot-rg"
5. Select a region close to you (e.g., East US)
6. Click "Review + create" and then "Create"

## 2. Azure AI Language Understanding (LUIS)

1. In the Azure Portal, search for "Language Understanding" or "LUIS"
2. Click "Create" to create a new LUIS resource
3. Fill in the details:
   - Name: career-guidance-luis
   - Subscription: Your student subscription
   - Resource group: career-guidance-chatbot-rg
   - Location: Select a supported region (e.g., East US)
   - Pricing tier: Free F0 (included in student account)
4. Click "Review + create" and then "Create"
5. Once created, go to the resource and note the following from the "Keys and Endpoint" section:
   - Key 1
   - Endpoint URL

## 3. Azure Cosmos DB

1. In the Azure Portal, search for "Cosmos DB"
2. Click "Create" to create a new Cosmos DB account
3. Fill in the details:
   - Account name: career-guidance-cosmos
   - API: Core (SQL)
   - Resource group: career-guidance-chatbot-rg
   - Location: Select a region close to you
   - Capacity mode: Serverless (best for student accounts with low usage)
4. Click "Review + create" and then "Create"
5. Once created, go to the resource and:
   - Create a new database named "CareerGuidanceDB"
   - Create a container named "UserPreferences" with partition key "/userId"
   - Note the connection string from the "Keys" section

## 4. Azure Functions

1. In the Azure Portal, search for "Function App"
2. Click "Create" to create a new Function App
3. Fill in the details:
   - Function App name: career-guidance-functions
   - Resource group: career-guidance-chatbot-rg
   - Publish: Code
   - Runtime stack: Python
   - Version: 3.9
   - Region: Same as your other resources
   - Operating System: Windows
   - Plan type: Consumption (Serverless)
4. Click "Review + create" and then "Create"
5. Once created, note the function app URL

## 5. Azure Web App

1. In the Azure Portal, search for "App Services"
2. Click "Create" to create a new Web App
3. Fill in the details:
   - Resource group: career-guidance-chatbot-rg
   - Name: career-guidance-webapp
   - Publish: Code
   - Runtime stack: Python 3.9
   - Operating System: Windows
   - Region: Same as your other resources
   - Windows Plan: Create new, select Free F1 tier (included in student account)
4. Click "Review + create" and then "Create"
5. Once created, note the web app URL
