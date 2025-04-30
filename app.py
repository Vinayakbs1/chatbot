from flask import Flask, request, jsonify, render_template, session, make_response
import os
import json
import uuid
import requests
from prediction import CareerPredictor, get_skill_recommendations
from dotenv import load_dotenv

# Load environment variables
dotenv_file = os.environ.get('DOTENV_FILE', '.env')
load_dotenv(dotenv_file)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default-secret-key')

# Initialize the career predictor
predictor = CareerPredictor()

# Initialize Cosmos DB manager
try:
    from cosmos_db import CosmosDBManager
    cosmos_manager = CosmosDBManager()
except Exception as e:
    print(f"Error initializing Cosmos DB manager: {str(e)}")
    cosmos_manager = None

# Initialize Language Service
try:
    from language_service import LanguageService
    language_service = LanguageService()
except Exception as e:
    print(f"Error initializing Language Service: {str(e)}")
    language_service = None

# Initialize Azure Functions client
try:
    from azure_functions import AzureFunctionsClient
    azure_functions = AzureFunctionsClient()
except Exception as e:
    print(f"Error initializing Azure Functions client: {str(e)}")
    azure_functions = None

def get_user_id():
    """Get or create a user ID for the session"""
    # Check if user_id is in the session
    if 'user_id' not in session:
        # Check if user_id is in a cookie
        user_id = request.cookies.get('user_id')
        if not user_id:
            # Generate a new user ID if none exists
            # Use a shorter, more user-friendly ID format
            user_id = str(uuid.uuid4())[:8]
        # Store in session
        session['user_id'] = user_id
    return session['user_id']

def detect_intent(text):
    """Detect the intent of the user's message"""
    # Convert to lowercase and remove punctuation
    text_lower = text.lower().strip()
    for char in '.,!?;:':
        text_lower = text_lower.replace(char, '')

    # Check for different intents
    if is_greeting(text_lower):
        return "Greeting"
    elif is_farewell(text_lower):
        return "Farewell"
    elif is_thanks(text_lower):
        return "Thanks"
    elif is_help(text_lower):
        return "Help"
    elif is_about(text_lower):
        return "About"
    else:
        return "SkillsInput"

def is_greeting(text_lower):
    """Check if the text is a greeting"""
    greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening',
                'howdy', 'hola', 'namaste', 'what\'s up', 'sup', 'yo', 'hi there', 'hello there']

    # Check if the text is a greeting
    for greeting in greetings:
        if text_lower == greeting or text_lower.startswith(greeting + ' '):
            return True

    return False

def is_farewell(text_lower):
    """Check if the text is a farewell"""
    farewells = ['bye', 'goodbye', 'see you', 'farewell', 'see you later', 'cya', 'good night',
                'have a good day', 'until next time', 'take care', 'exit', 'quit']

    for farewell in farewells:
        if text_lower == farewell or text_lower.startswith(farewell + ' '):
            return True

    return False

def is_thanks(text_lower):
    """Check if the text is an expression of gratitude"""
    thanks_phrases = ['thank', 'thanks', 'thank you', 'appreciate', 'grateful', 'thx', 'ty']

    for phrase in thanks_phrases:
        if phrase in text_lower:
            return True

    return False

def is_help(text_lower):
    """Check if the user is asking for help"""
    help_phrases = ['help', 'how do', 'how can', 'how to', 'what can you do', 'assist me', 'instructions', 'guide me']

    for phrase in help_phrases:
        if phrase in text_lower:
            return True

    return False

def is_about(text_lower):
    """Check if the user is asking about the chatbot"""
    about_phrases = ['who are you', 'what are you', 'tell me about yourself', 'your purpose', 'about you',
                    'how do you work', 'what do you do', 'your capabilities']

    for phrase in about_phrases:
        if phrase in text_lower:
            return True

    return False

def get_greeting_response():
    """Get a random greeting response"""
    import random

    responses = [
        "Hello! I'm your career guidance assistant. How can I help you today?",
        "Hi there! I can help you explore career options based on your skills. What skills do you have?",
        "Greetings! I'm here to assist with your career planning. Tell me about your skills and interests.",
        "Hello! I'm excited to help you find the right career path. What skills would you like me to analyze?",
        "Hi! I'm your AI career advisor. Share your skills with me, and I'll recommend suitable career paths.",
        "Hey there! Ready to explore career opportunities? Let me know your skills, and I'll guide you.",
        "Welcome! I'm here to help you discover career paths that match your skills. What are you good at?"
    ]

    return random.choice(responses)

def get_farewell_response():
    """Get a random farewell response"""
    import random

    responses = [
        "Goodbye! Feel free to come back anytime for more career guidance.",
        "Farewell! I hope I was able to help with your career planning.",
        "Take care! Remember, your skills are valuable assets in your career journey.",
        "Goodbye! I'm here whenever you need career advice or guidance.",
        "Until next time! Keep developing your skills and exploring new opportunities.",
        "See you later! Don't hesitate to return if you have more questions about your career path."
    ]

    return random.choice(responses)

def get_thanks_response():
    """Get a random response to thanks"""
    import random

    responses = [
        "You're welcome! I'm glad I could help with your career guidance.",
        "Happy to assist! Is there anything else you'd like to know about your career options?",
        "My pleasure! I'm here to help you navigate your career journey.",
        "Anytime! Your career development is important, and I'm here to support you.",
        "You're welcome! Remember, continuous learning is key to career growth.",
        "No problem at all! Feel free to ask if you have more questions about your career path."
    ]

    return random.choice(responses)

def get_help_response():
    """Get a help response"""
    return """I'm your Career Guidance Chatbot! Here's how I can help you:

1. Share your skills with me (e.g., "I know Python, data analysis, and project management")
2. I'll analyze your skills and recommend suitable career paths
3. I'll provide details about each recommended career
4. I can suggest additional skills to learn for your target career

You can also ask me about specific careers or skills at any time!"""

def get_about_response():
    """Get information about the chatbot"""
    return """I'm an AI-powered Career Guidance Chatbot built with Azure services. I use:

- Azure Language Service to understand your skills and interests
- Azure Cosmos DB to store your preferences and chat history
- Azure Functions for advanced career predictions and recommendations

My goal is to help you explore career options based on your unique skills and interests. I can analyze your skills, recommend career paths, and suggest additional skills to develop for your target career."""

def analyze_text_with_language_service(text):
    """Analyze text using Azure Language Service to extract skills and entities"""
    # Detect the intent of the message
    intent = detect_intent(text)

    # Handle different intents
    if intent == "Greeting":
        return {
            "intent": "Greeting",
            "entities": {},
            "response": get_greeting_response()
        }
    elif intent == "Farewell":
        return {
            "intent": "Farewell",
            "entities": {},
            "response": get_farewell_response()
        }
    elif intent == "Thanks":
        return {
            "intent": "Thanks",
            "entities": {},
            "response": get_thanks_response()
        }
    elif intent == "Help":
        return {
            "intent": "Help",
            "entities": {},
            "response": get_help_response()
        }
    elif intent == "About":
        return {
            "intent": "About",
            "entities": {},
            "response": get_about_response()
        }

    # For SkillsInput intent, process skills
    if not language_service.is_configured():
        # If Language Service is not configured, return default values
        print("Language Service not configured, using simple text processing")
        skills = [s.strip() for s in text.split(',') if s.strip()]
        return {
            "intent": "SkillsInput",
            "entities": {
                "Skills": skills
            }
        }

    try:
        # Use Language Service to extract skills
        result = language_service.analyze_text(text)

        if "error" in result:
            print(f"Error analyzing text with Language Service: {result['error']}")
            # Fall back to simple text processing
            skills = [s.strip() for s in text.split(',') if s.strip()]
        else:
            skills = result.get("skills", [])
            # If no skills were found, fall back to simple text processing
            if not skills:
                skills = [s.strip() for s in text.split(',') if s.strip()]

        # Also analyze sentiment if it's feedback
        sentiment = None
        if "feedback" in text.lower() or "review" in text.lower():
            sentiment_result = language_service.analyze_sentiment(text)
            if "error" not in sentiment_result:
                sentiment = sentiment_result.get("sentiment")

        return {
            "intent": "SkillsInput",
            "entities": {
                "Skills": skills
            },
            "sentiment": sentiment
        }

    except Exception as e:
        print(f"Error analyzing text with Language Service: {str(e)}")
        # Fall back to simple text processing
        skills = [s.strip() for s in text.split(',') if s.strip()]
        return {
            "intent": "SkillsInput",
            "entities": {
                "Skills": skills
            }
        }

@app.route('/')
def index():
    """Render the main page"""
    # Get or create a user ID
    user_id = get_user_id()

    # Get chat history from Cosmos DB
    chat_history = []

    if cosmos_manager.is_connected():
        # Get the user's chat history
        chat_history = cosmos_manager.get_chat_history(user_id)

    # Create response with template
    response = make_response(render_template('index.html',
                          user_id=user_id,
                          chat_history=json.dumps(chat_history)))

    # Set a persistent cookie with the user ID (expires in 1 year)
    response.set_cookie('user_id', user_id, max_age=31536000, httponly=True, samesite='Lax')

    return response

@app.route('/api/predict', methods=['POST'])
def predict_career():
    """API endpoint to predict career based on skills"""
    try:
        data = request.json
        skills = data.get('skills', '')
        # Use the provided user ID or generate a new one
        user_id = data.get('userId', get_user_id())

        if not skills:
            return jsonify({"error": "No skills provided"}), 400

        # Analyze text with Language Service
        language_result = analyze_text_with_language_service(skills)

        # Check for conversational intents
        intent = language_result.get('intent')
        if intent in ["Greeting", "Farewell", "Thanks", "Help", "About"]:
            response = language_result.get('response')

            # Update chat history for conversational response
            if cosmos_manager.is_connected():
                # Get existing chat history
                existing_messages = cosmos_manager.get_chat_history(user_id)

                # Add new messages
                existing_messages.append({"role": "user", "content": skills})
                existing_messages.append({"role": "assistant", "content": response})

                # Save updated chat history
                cosmos_manager.save_chat_history(user_id, existing_messages)

            # Create response data
            response_data = {
                "conversational": True,
                "intent": intent,
                "response": response,
                "language_result": language_result
            }

            # Create response object
            api_response = make_response(jsonify(response_data))

            # Ensure the user ID cookie is set
            api_response.set_cookie('user_id', user_id, max_age=31536000, httponly=True, samesite='Lax')

            return api_response

        # Extract skills from language analysis
        extracted_skills = language_result.get('entities', {}).get('Skills', [])

        # If no skills were extracted, use the original text
        if not extracted_skills:
            processed_skills = skills
        else:
            processed_skills = ", ".join(extracted_skills)

        # Always use local predictor instead of Azure Functions
        print("Using local predictor for career prediction")

        # Use local predictor
        predictions = predictor.predict_career(processed_skills)

        # Get details for the top career
        top_career = predictions[0]['career']
        details = predictor.get_career_details(top_career)

        # Get skill recommendations
        recommended_skills = get_skill_recommendations(extracted_skills)

        # Update chat history in Cosmos DB
        if cosmos_manager.is_connected():
            existing_messages = cosmos_manager.get_chat_history(user_id)

            # Add new messages
            existing_messages.append({"role": "user", "content": skills})
            existing_messages.append({"role": "assistant", "content": f"Based on your skills, I recommend exploring a career in {top_career}."})

            # Save updated chat history
            cosmos_manager.save_chat_history(user_id, existing_messages)

        response = {
            "predictions": predictions,
            "top_career_details": details,
            "recommended_skills": recommended_skills,
            "language_result": language_result
        }

        # Create response object
        api_response = make_response(jsonify(response))

        # Ensure the user ID cookie is set
        api_response.set_cookie('user_id', user_id, max_age=31536000, httponly=True, samesite='Lax')

        return api_response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/career_details', methods=['GET'])
def get_career_details():
    """API endpoint to get details about a specific career"""
    try:
        career = request.args.get('career', '')

        if not career:
            return jsonify({"error": "No career specified"}), 400

        # Always use local predictor instead of Azure Functions
        print("Using local predictor for career details")

        # Get career details using local predictor
        details = predictor.get_career_details(career)

        # Get user ID
        user_id = get_user_id()

        # Create response object
        api_response = make_response(jsonify(details))

        # Ensure the user ID cookie is set
        api_response.set_cookie('user_id', user_id, max_age=31536000, httponly=True, samesite='Lax')

        return api_response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/recommend_skills', methods=['POST'])
def recommend_skills():
    """API endpoint to recommend skills based on user's current skills"""
    try:
        data = request.json
        user_skills = data.get('skills', [])
        target_career = data.get('targetCareer', None)

        if not user_skills:
            return jsonify({"error": "No skills provided"}), 400

        # Always use local function instead of Azure Functions
        print("Using local function for skill recommendations")

        # Get skill recommendations using local function
        recommended_skills = get_skill_recommendations(user_skills)

        # Get user ID
        user_id = get_user_id()

        # Create response object
        api_response = make_response(jsonify({"recommended_skills": recommended_skills}))

        # Ensure the user ID cookie is set
        api_response.set_cookie('user_id', user_id, max_age=31536000, httponly=True, samesite='Lax')

        return api_response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat_history', methods=['GET'])
def get_chat_history():
    """API endpoint to get chat history for a user"""
    try:
        user_id = request.args.get('userId', get_user_id())

        if not cosmos_manager.is_connected():
            return jsonify({"error": "Cosmos DB not connected"}), 500

        # Get chat history from Cosmos DB
        history = cosmos_manager.get_chat_history(user_id)

        # Create response object
        api_response = make_response(jsonify({"history": history}))

        # Ensure the user ID cookie is set
        api_response.set_cookie('user_id', user_id, max_age=31536000, httponly=True, samesite='Lax')

        return api_response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clear_chat', methods=['POST'])
def clear_chat():
    """API endpoint to clear chat history for a user"""
    try:
        data = request.json
        user_id = data.get('userId', get_user_id())

        if not cosmos_manager.is_connected():
            return jsonify({"error": "Cosmos DB not connected"}), 500

        # Clear chat history by saving an empty array
        cosmos_manager.save_chat_history(user_id, [])

        # Create response
        response = jsonify({"success": True})

        # Ensure the user ID cookie is set
        response.set_cookie('user_id', user_id, max_age=31536000, httponly=True, samesite='Lax')

        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_all_users():
    """API endpoint to get all users with chat history"""
    try:
        if not cosmos_manager.is_connected():
            return jsonify({"error": "Cosmos DB not connected"}), 500

        # Get all users from Cosmos DB
        users = cosmos_manager.get_all_users()

        # Create response
        return jsonify({"users": users})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Create the templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)

    # Run the Flask app
    app.run(debug=True, port=5000)
