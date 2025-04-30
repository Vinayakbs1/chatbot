import os
import subprocess
import sys

def main():
    """Run the application with local processing only"""
    print("=== Running Career Guidance Chatbot with Local Processing ===\n")
    
    # Create a temporary .env file with local processing settings
    env_content = """# Local processing settings
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=local-development-key
"""
    
    # Save the temporary .env file
    with open('.env.local', 'w') as f:
        f.write(env_content)
    
    # Run the application with the temporary .env file
    print("Starting the application with local processing...")
    print("The application will be available at http://localhost:5000")
    print("Press Ctrl+C to stop the application.")
    
    # Use the temporary .env file
    os.environ['DOTENV_FILE'] = '.env.local'
    
    # Run the application
    subprocess.run([sys.executable, "app.py"])
    
    # Clean up
    if os.path.exists('.env.local'):
        os.remove('.env.local')

if __name__ == "__main__":
    main()
