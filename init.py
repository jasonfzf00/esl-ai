import os
import sys
import subprocess

def check_python_version():
    """Check if Python version is 3.11 or higher."""
    if sys.version_info < (3, 11):
        print("Error: Python 3.11 or higher is required.")
        sys.exit(1)

def install_dependencies():
    """Install dependencies from requirements.txt."""
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def create_directories():
    """Create necessary directories."""
    print("Creating directories...")
    os.makedirs("output", exist_ok=True)
    os.makedirs("sample", exist_ok=True)

def check_ollama():
    """Check if Ollama is running."""
    print("Checking if Ollama is running...")
    try:
        subprocess.run([sys.executable, "check_ollama.py"], check=True)
    except subprocess.CalledProcessError:
        print("Warning: Ollama check failed. Make sure Ollama is running before using the API.")

def create_test_file():
    """Create a test Markdown file."""
    print("Creating test Markdown file...")
    subprocess.run([sys.executable, "create_test_file.py"])

def main():
    """Initialize the project."""
    print("Initializing ESL AI project...")
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Create directories
    create_directories()
    
    # Create test file
    create_test_file()
    
    # Check Ollama
    check_ollama()
    
    print("\nInitialization complete!")
    print("\nTo start the server, run:")
    print("python run.py")
    print("\nTo test the API, run:")
    print("python test_api.py")

if __name__ == "__main__":
    main() 