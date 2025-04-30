import os
from azure.cosmos import CosmosClient, PartitionKey, exceptions
import uuid
import time
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CosmosDBManager:
    def __init__(self):
        """Initialize the Cosmos DB manager"""
        # Get connection details from environment variables
        self.endpoint = os.environ.get("COSMOS_ENDPOINT")
        self.key = os.environ.get("COSMOS_KEY")
        self.database_name = os.environ.get("COSMOS_DATABASE", "careerdb")
        self.container_name = os.environ.get("COSMOS_CONTAINER", "students")

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

    def create_database_if_not_exists(self):
        """Create the database if it doesn't exist"""
        try:
            self.database = self.client.create_database_if_not_exists(id=self.database_name)
            print(f"Database '{self.database_name}' created or already exists")
            return True
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error creating database: {e}")
            return False

    def create_container_if_not_exists(self):
        """Create the container if it doesn't exist"""
        try:
            self.container = self.database.create_container_if_not_exists(
                id=self.container_name,
                partition_key=PartitionKey(path="/userId"),
                offer_throughput=400
            )
            print(f"Container '{self.container_name}' created or already exists")
            return True
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error creating container: {e}")
            return False

    def save_user_preferences(self, user_id, skills, predicted_career=None):
        """
        This method is now a no-op since we're storing all information in the chat history.
        Kept for backward compatibility.
        """
        # Do nothing - we're not storing separate user preference documents anymore
        return None

    def get_user_preferences(self, user_id):
        """
        This method is now a no-op since we're storing all information in the chat history.
        Kept for backward compatibility.
        """
        # Return empty list - we're not storing separate user preference documents anymore
        return []

    def save_chat_history(self, user_id, messages, chat_title=None):
        """Save or update chat history to Cosmos DB - maintains a single chat per user"""
        if not self.is_connected():
            print("Not connected to Cosmos DB")
            return None

        try:
            # First check if a chat document already exists for this user
            query = f"SELECT * FROM c WHERE c.userId = '{user_id}' AND c.type = 'userChat'"
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))

            # Generate a chat title if not provided
            if not chat_title and messages and len(messages) > 0:
                # Find the first user message to use as title
                for msg in messages:
                    if msg.get("role") == "user":
                        # Use the first 30 characters of the first user message as title
                        user_content = msg.get("content", "")
                        chat_title = user_content[:30] + ("..." if len(user_content) > 30 else "")
                        break

            # If still no title, use a default
            if not chat_title:
                chat_title = "New Chat"

            if items:
                # Update existing chat document
                existing_chat = items[0]
                existing_chat["messages"] = messages
                existing_chat["timestamp"] = datetime.utcnow().isoformat()

                # Only update title if it's not already set (preserve original title)
                if not existing_chat.get("chatTitle"):
                    existing_chat["chatTitle"] = chat_title

                # Update the document in the container
                updated_item = self.container.replace_item(item=existing_chat["id"], body=existing_chat)
                print(f"Chat history updated with id: {updated_item['id']}")
                return updated_item
            else:
                # Create a new chat document
                document = {
                    "id": str(uuid.uuid4()),
                    "userId": user_id,
                    "type": "userChat",
                    "chatTitle": chat_title,
                    "messages": messages,
                    "timestamp": datetime.utcnow().isoformat()
                }

                # Create the document in the container
                created_item = self.container.create_item(body=document)
                print(f"Chat history created with id: {created_item['id']}")
                return created_item
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error saving chat history: {e}")
            return None

    def get_chat_history(self, user_id):
        """Get chat history from Cosmos DB - retrieves the single chat for a user"""
        if not self.is_connected():
            print("Not connected to Cosmos DB")
            return []

        try:
            # Query for the user's chat
            query = f"SELECT * FROM c WHERE c.userId = '{user_id}' AND c.type = 'userChat'"
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))

            if items:
                # Return messages from the user's chat
                return items[0].get("messages", [])
            return []
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error getting chat history: {e}")
            return []

    def get_all_users(self):
        """Get all users with chat history from Cosmos DB"""
        if not self.is_connected():
            print("Not connected to Cosmos DB")
            return []

        try:
            # Query for all chat documents, including chat title
            query = "SELECT c.userId, c.timestamp, c.chatTitle FROM c WHERE c.type = 'userChat'"
            items = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))

            # Sort by timestamp (newest first)
            items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

            return items
        except exceptions.CosmosHttpResponseError as e:
            print(f"Error getting all users: {e}")
            return []

# Example usage
if __name__ == "__main__":
    # Set environment variables for testing
    os.environ["COSMOS_ENDPOINT"] = "https://your-cosmos-account.documents.azure.com:443/"
    os.environ["COSMOS_KEY"] = "your-cosmos-key"

    # Initialize the Cosmos DB manager
    cosmos_manager = CosmosDBManager()

    # Create database and container if they don't exist
    if cosmos_manager.is_connected():
        cosmos_manager.create_database_if_not_exists()
        cosmos_manager.create_container_if_not_exists()

        # Example: Save chat history
        user_id = "test-user-123"
        messages = [
            {"role": "system", "content": "Welcome to the Career Guidance Chatbot!"},
            {"role": "user", "content": "I know Python and Machine Learning"},
            {"role": "assistant", "content": "Based on your skills, I recommend a career in Data Science."}
        ]

        cosmos_manager.save_chat_history(user_id, messages)

        # Example: Get chat history
        history = cosmos_manager.get_chat_history(user_id)
        print(f"Chat history: {json.dumps(history, indent=2)}")
    else:
        print("Could not connect to Cosmos DB. Check your environment variables.")
