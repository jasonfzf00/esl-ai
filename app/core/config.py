import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "ESL AI - Vocabulary Practice Generator"
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./esl_ai.db")
    
    # Ollama settings
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama2")
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    
    # Output directory
    OUTPUT_DIR: str = "output"

settings = Settings() 