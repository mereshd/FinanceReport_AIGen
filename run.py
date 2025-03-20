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
    
    # First try to get from .env
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Then try to get from secrets.toml if .env fails
    if not api_key or api_key == "your_api_key_here":
        secrets_path = os.path.join(os.path.expanduser("~"), ".streamlit", "secrets.toml")
        project_secrets_path = os.path.join(".streamlit", "secrets.toml")
        
        # Check project-level secrets.toml
        if os.path.exists(project_secrets_path):
            try:
                with open(project_secrets_path, "r") as f:
                    import toml
                    secrets = toml.load(f)
                    if "OPENAI_API_KEY" in secrets and secrets["OPENAI_API_KEY"] != "your_api_key_here":
                        print("✅ OpenAI API key found in project secrets.toml file.")
                        return
            except:
                pass
                
        # Check global secrets.toml
        if os.path.exists(secrets_path):
            try:
                with open(secrets_path, "r") as f:
                    import toml
                    secrets = toml.load(f)
                    if "OPENAI_API_KEY" in secrets and secrets["OPENAI_API_KEY"] != "your_api_key_here":
                        print("✅ OpenAI API key found in global secrets.toml file.")
                        return
            except:
                pass
        
        print("❌ OpenAI API key not found in .env or secrets.toml.")
        api_key = input("Please enter your OpenAI API key: ")
        
        # Ask user where to save the API key
        save_location = input("Save to [1] .env or [2] .streamlit/secrets.toml? (1/2): ")
        
        if save_location == "2":
            # Ensure .streamlit directory exists
            os.makedirs(".streamlit", exist_ok=True)
            
            # Save to secrets.toml
            with open(project_secrets_path, "w") as f:
                f.write(f'OPENAI_API_KEY = "{api_key}"\n')
            print("✅ API key saved to .streamlit/secrets.toml file.")
            
            # Add to .gitignore if not already there
            with open(".gitignore", "a+") as f:
                f.seek(0)
                content = f.read()
                if ".streamlit/secrets.toml" not in content:
                    f.write("\n# Streamlit secrets\n.streamlit/secrets.toml\n")
        else:
            # Save to .env
            with open(".env", "w") as f:
                f.write(f"OPENAI_API_KEY={api_key}\n")
            print("✅ API key saved to .env file.")
    else:
        print("✅ OpenAI API key found in .env file.")

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