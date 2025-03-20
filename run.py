import os
import subprocess
import sys

def check_dependencies():
    """Check if all required dependencies are installed."""
    try:
        import streamlit
        import openai
        import pandas
        import plotly
        import dotenv
        print("✅ All dependencies are installed.")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed.")
        return True

def check_api_key():
    """Check if the OpenAI API key is set."""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        print("❌ OpenAI API key not found or not set.")
        api_key = input("Please enter your OpenAI API key: ")
        
        # Update the .env file
        with open(".env", "w") as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")

        print("✅ API key saved to .env file.")
    else:
        print("✅ OpenAI API key found.")

def run_app():
    """Run the Streamlit app."""
    print("Starting the Finance & PE AI Assistant...")
    subprocess.call(["streamlit", "run", "app.py"])

if __name__ == "__main__":
    print("=" * 50)
    print("Finance & Private Equity AI Assistant")
    print("=" * 50)
    
    if check_dependencies():
        check_api_key()
        run_app() 