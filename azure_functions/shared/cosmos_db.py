import os
from azure.cosmos import CosmosClient, PartitionKey, exceptions
import uuid
from datetime import datetime
import json

class CosmosDBManager:
    def __init__(self):
        """Initialize the Cosmos DB manager"""
        # Get connection details from environment variables
        self.endpoint = os.environ.get("COSMOS_ENDPOINT")
        self.key = os.environ.get("COSMOS_KEY")
        self.database_name = os.environ.get("COSMOS_DATABASE", "CareerGuidanceDB")
        self.container_name = os.environ.get("COSMOS_CONTAINER", "UserPreferences")
        
        # Initialize the Cosmos client
        if self.endpoint and self.key:
            self.client = CosmosClient(self.endpoint, self.key)
            self.database = self.client.get_database_client(self.database_name)
            self.container = self.database.get_container_client(self.container_name)
            print(f"Connected to Cosmos DB: {self.database_name}/{self.container_name}")
        else:
            print("Cosmos DB connection details not found in environment variables")
            self.client = None
            self.database = None
            self.container = None
    
    def is_connected(self):
        """Check if connected to Cosmos DB"""
        return self.client is not None
    
    def save_user_preferences(self, user_id, skills, predicted_career=None):
        """Save user preferences to Cosmos DB"""
        if not self.is_connected():
            print("Not connected to Cosmos DB")
            return None
        
        try:
            # Create a document with user preferences
            document = {
                "id": str(uuid.uuid4()),
                "userId": user_id,
                "skills": skills,
                "predictedCareer": predicted_career,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Create the document in the container
            created_item = self.container.create_item(body=document)
            print(f"User preferences saved with id: {created_item['id']}")
            return created_item
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error saving user preferences: {e}")
            return None
    
    def get_user_preferences(self, user_id):
        """Get user preferences from Cosmos DB"""
        if not self.is_connected():
            print("Not connected to Cosmos DB")
            return []
        
        try:
            # Query for items by user ID
            query = f"SELECT * FROM c WHERE c.userId = '{user_id}' ORDER BY c.timestamp DESC"
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            return items
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error getting user preferences: {e}")
            return []
    
    def save_chat_history(self, user_id, messages):
        """Save chat history to Cosmos DB"""
        if not self.is_connected():
            print("Not connected to Cosmos DB")
            return None
        
        try:
            # Create a document with chat history
            document = {
                "id": str(uuid.uuid4()),
                "userId": user_id,
                "type": "chatHistory",
                "messages": messages,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Create the document in the container
            created_item = self.container.create_item(body=document)
            print(f"Chat history saved with id: {created_item['id']}")
            return created_item
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error saving chat history: {e}")
            return None
    
    def get_chat_history(self, user_id):
        """Get chat history from Cosmos DB"""
        if not self.is_connected():
            print("Not connected to Cosmos DB")
            return []
        
        try:
            # Query for chat history by user ID
            query = f"SELECT * FROM c WHERE c.userId = '{user_id}' AND c.type = 'chatHistory' ORDER BY c.timestamp DESC LIMIT 1"
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            if items:
                return items[0].get("messages", [])
            return []
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error getting chat history: {e}")
            return []
