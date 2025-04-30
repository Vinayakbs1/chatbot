import os
import argparse
import subprocess
import time

def run_data_preprocessing():
    """Run the data preprocessing script"""
    print("Running data preprocessing...")
    subprocess.run(["python", "data_preprocessing.py"])

def run_model_training():
    """Run the model training script"""
    print("Running model training...")
    subprocess.run(["python", "model_training.py"])

def run_flask_app():
    """Run the Flask application"""
    print("Starting Flask application...")
    subprocess.run(["python", "app.py"])

def main():
    """Main function to run the entire pipeline"""
    parser = argparse.ArgumentParser(description='Career Guidance Chatbot')
    parser.add_argument('--skip-preprocessing', action='store_true', help='Skip data preprocessing')
    parser.add_argument('--skip-training', action='store_true', help='Skip model training')
    parser.add_argument('--only-app', action='store_true', help='Only run the Flask app')
    args = parser.parse_args()
    
    # Create necessary directories
    os.makedirs('models', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    if args.only_app:
        # Only run the Flask app
        run_flask_app()
    else:
        # Run the full pipeline
        if not args.skip_preprocessing:
            run_data_preprocessing()
        
        if not args.skip_training:
            run_model_training()
        
        # Run the Flask app
        run_flask_app()

if __name__ == "__main__":
    main()
