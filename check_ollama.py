import requests
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_ollama():
    """Check if Ollama is running and the model is available."""
    # Get the model name from environment variables
    model = os.getenv("OLLAMA_MODEL", "llama2")
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    
    # Ollama API URL
    url = f"{ollama_url}/api/tags"
    
    try:
        # Send a request to the Ollama API
        print(f"Checking if Ollama is running...")
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            print("Ollama is running.")
            
            # Check if the model is available
            models = response.json().get("models", [])
            model_names = [m.get("name") for m in models]
            
            if model in model_names:
                print(f"Model '{model}' is available.")
                return True
            else:
                print(f"Model '{model}' is not available.")
                print(f"Available models: {', '.join(model_names)}")
                print(f"\nTo pull the model, run:")
                print(f"ollama pull {model}")
                return False
        else:
            print(f"Error: Ollama API returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Ollama.")
        print("Make sure Ollama is running.")
        print("\nTo start Ollama, run:")
        print("ollama serve")
        return False

if __name__ == "__main__":
    if not check_ollama():
        sys.exit(1) 