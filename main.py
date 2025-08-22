import os
import sys
import subprocess
from pathlib import Path

def main():
    """
    Main entry point for the GraviLog Smart Risk Analysis Agent.
    This script launches the Streamlit application.
    """
    print("Starting GraviLog Smart Risk Analysis Agent...")

    # Check if OPENAI_API_KEY is set
    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable is not set.")
        print("The application may not function correctly without an API key.")
        print("Please set your OpenAI API key in the .env file or as an environment variable.")

    # Get the path to the app.py file
    app_path = Path("app.py").absolute()

    if not app_path.exists():
        print(f"Error: Could not find the application file at {app_path}")
        sys.exit(1)

    # Launch the Streamlit app
    try:
        print(f"Launching Streamlit app from {app_path}")
        subprocess.run(["streamlit", "run", str(app_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: Streamlit not found. Please make sure it's installed.")
        print("You can install it with: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main()
